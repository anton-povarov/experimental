// Task 3: Concurrent LRU Cache
//
// Goal: Implement a thread-safe LRU (Least Recently Used) cache with per-bucket locking.
//
// Requirements
// 	•	Use an LRU eviction policy (recently used keys stay, least recent ones get removed).
// 	•	Must be safe for concurrent readers and writers.
// 	•	You may partition the cache into N buckets to reduce lock contention.
// 	•	Use std::mutex, std::shared_mutex, or your choice of lock strategy.
// 	•	Do not use std::unordered_map with std::mutex per entry — prefer a higher-level approach.

// Evaluation Focus
// 	•	Understanding of concurrent access patterns
// 	•	Trade-offs between coarse and fine-grained locking
// 	•	Maintaining LRU order correctly
// 	•	Balancing correctness and performance
// 	•	Clean API and RAII correctness

// Bonus
// 	•	Add get_or_compute() that computes and caches values on demand (testing double-checked locking or synchronization).

#include <algorithm>
#include <bit>
#include <cstdint>
#include <list>
#include <memory>
#include <mutex>
#include <random>
#include <type_traits>
#include <unordered_map>

//
#include <format>
#include <print>
#include <thread>

#include "meow/hash/hash.hpp"

template <class K, class V, class HashT = std::hash<K>>
    requires std::is_nothrow_move_constructible_v<V> && std::is_nothrow_move_assignable_v<V>
struct lru_cache_t
{
	inline static const unsigned int min_concurrency = 8;
	inline static const unsigned int max_concurrency = 256;

	constexpr explicit lru_cache_t(uint32_t capacity, unsigned int concurrency = min_concurrency)
	    : approx_size_{0}
	    , evictor_count_{0}
	    , capacity_{capacity}
	{
		auto value = std::bit_ceil(concurrency); // round to the nearest 2^N >= concurrency
		concurrency = std::min(max_concurrency, std::max(concurrency, min_concurrency));

		shard_count_ = value;
		shards_ = std::unique_ptr<shard_t[]>(new shard_t[shard_count_]);
		for (size_t i = 0; i < shard_count_; i++) {
			// this will force eviction from a shard locally in case
			//  global eviction is not keeping up and shards are overflowing
			shards_[i].max_size = std::max({
			        uint32_t(double(capacity_ / shard_count_) * 1.75),
			        uint32_t{1},
			});
		}
	}

	bool get(K const &key, V &value)
	{
		shard_t *shard = this->shard_for_key(key);
		{
			std::scoped_lock lk_(shard->mtx);

			auto map_it = shard->map.find(key);
			if (map_it == shard->map.end())
				return false;

			// move the item to the end of lru list
			// 1. this does not allocate and does not throw
			// 2. this should also not invalidate iterators -> don't need to update the map
			shard->lru.splice(shard->lru.end(), shard->lru, map_it->second);

			// update map to point to moved items
			// map_it->second = std::prev(shard->lru.end());

			// it pains me to copy under lock, but oh well, store pointers!
			// TODO(antoxa)
			//  figure out if moving this assignment above the list splice would improve performance
			//  the idea is that it would allow better pipelining by the compiler (i.e. starting the copy process earlier)
			value = map_it->second->second;
		}

		return true;
	}

	// puts an item into the cache, overwrites the old key if it exists
	//  take `value` by value, to allow moves if supported
	void put(K const &key, V value)
	{
		shard_t *shard = this->shard_for_key(key);
		{
			std::scoped_lock lk_(shard->mtx);

			// step_0: find the item, if it exists - we'll overwrite it later
			auto       map_it = shard->map.find(key);
			bool const key_exists = (map_it != shard->map.end());

			if (key_exists) {
				// move to end of the list, this is nothrow
				shard->lru.splice(shard->lru.end(), shard->lru, map_it->second);

				// move assign, this is nothrow (see requires for this class)
				map_it->second->second = std::move(value);

				return;
			}

			// we're inserting a key now, can overflow max_size, maybe evict first
			// this is a failsafe mechanism in addition to global eviction
			// should not be triggered, unless
			//  a) global eviction is not keeping up OR
			//  b) there is a significant shard population imbalance (bad hash function?)
			if (shard->map.size() >= shard->max_size) {
				auto &[key, value] = shard->lru.front();
				shard->map.erase(key);
				shard->lru.pop_front();

				approx_size_.fetch_sub(1, std::memory_order_relaxed);
			}

			// inserting now

			// step_1: push back into the list, this allocates and can throw
			//         if it does throw - it's fine, we've not done anything yet
			shard->lru.emplace_back(key, std::move(value));
			auto list_it = std::prev(shard->lru.end());

			try {
				// step_2: insert into the hash map
				//         this will allocate and might throw, so we'll need to clean up in such case
				auto iter = shard->map.emplace_hint(map_it, key, list_it);
				(void)iter; // we don't need this iterator, we've inserted the value already
			}
			catch (...) {
				// clean up whatever we've already inserted into the lru list before the try block
				shard->lru.erase(list_it);
				throw;
			}
		}

		// we have inserted an item and increased size
		// relaxed = just need atomicity, not memory visibility ordering
		approx_size_.fetch_add(1, std::memory_order_relaxed);

		// maybe clean some records that are over capacity, in LRU order
		this->maybe_evict_if_over_capacity();
	}

private:
	struct alignas(64) shard_t
	{
		std::mutex                                                                  mtx;
		std::size_t                                                                 max_size;
		std::list<std::pair<K, V>>                                                  lru;
		std::unordered_map<K, typename std::list<std::pair<K, V>>::iterator, HashT> map;
	};

	shard_t *shard_for_key(K const &key)
	{
		auto const hash_v = HashT{}(key);
		using hash_t = decltype(hash_v);

		if constexpr (std::is_integral_v<K>) {
			if (hash_v == key) { // HashT is an 'identity' hash, take %
				return &shards_[hash_v % shard_count_];
			}
		}

		// we have either non-integral keys or the hash function is not an identity
		// take the top X bits as offset into shards_
		// remember that shard_count_ is a power of 2, so shard_count - 1 is a mask for that power
		uint32_t const offset = (hash_v >> std::countl_zero(hash_t(shard_count_ - 1)));
		return &shards_[offset];
	}

	void maybe_evict_if_over_capacity()
	{
		// these thread locals are shared across instances of this class - per executing thread
		// should be fine, generating more random numbers does not cross-affect caches
		thread_local std::mt19937                            rng(std::random_device{}());
		thread_local std::uniform_int_distribution<uint32_t> dist(0, shard_count_ - 1);

		uint32_t local_approx_size = approx_size_.load(std::memory_order_relaxed);
		if (local_approx_size < capacity_)
			return;

		//
		size_t const max_evictors = shard_count_ / 2;

		size_t n_evictors = evictor_count_.load(std::memory_order_acquire);
		while (n_evictors < max_evictors) {
			bool exchanged = evictor_count_.compare_exchange_weak(
			        n_evictors, n_evictors + 1, std::memory_order_acquire, std::memory_order_relaxed);

			// ok, we've got our increment and are one of evictors now
			if (exchanged)
				break;
		}

		// there are more evictors than needed already
		if (n_evictors >= max_evictors)
			return;

		uint32_t const shard_id = dist(rng);
		shard_t       *shard = &shards_[shard_id];
		bool           evicted = false;

		{
			std::scoped_lock lk(shard->mtx);
			if (!shard->lru.empty()) {
				auto &[k, v] = shard->lru.front();
				shard->map.erase(k);
				shard->lru.pop_front();

				evicted = true;
			}
		}

		if (evicted) {
			approx_size_.fetch_sub(1, std::memory_order_relaxed);
		}

		evictor_count_.fetch_sub(1, std::memory_order_release);
	}

private:
	std::atomic<size_t>        approx_size_;
	std::atomic<size_t>        evictor_count_;
	uint32_t                   capacity_;
	uint32_t                   shard_count_;
	std::unique_ptr<shard_t[]> shards_;

private:
	lru_cache_t(lru_cache_t const &) = delete;
	lru_cache_t &operator=(lru_cache_t const &) = delete;
	lru_cache_t(lru_cache_t &&) = delete;
	lru_cache_t &operator=(lru_cache_t &&) = delete;
};

int main()
{
	lru_cache_t<int, std::string, meow::hash<int>> cache{100, 5};

	size_t const n_items_to_insert = 109;
	size_t const n_reads = 150;

	for (uint32_t i = 0; i < n_items_to_insert; i++) {
		cache.put(i + 1, std::format("item-{}", i + 1));
	}

	srandom(time(NULL));
	for (uint32_t i = 0; i < n_reads; i++) {
		uint32_t const k = random() % (n_items_to_insert + 1);

		std::string value;
		bool const  found = cache.get(k, value);
		std::print("get({}) -> [{}] {}\n", k, (found) ? "found" : "not", value);
	}

	return 0;
}