// compilation/linking quirks
// 1) GCC: requires linking -latomic due to 128 bit CAS
// even with -latomic GCC would not compile anything but CAS (i.e. no fetch_add, ++ increments, etc.)
//
// 2) on linux x86: add -mcx16 flag for both clang and gcc to enable the cmpxchg16b instruction
//
// i.e.
//  g++- -std=c++23 -O3 -ffast-math -mcx16 -o cas128 ./cas128.cpp -latomic
//  clang++ -std=c++23 -mcx16 -O3 -ffast-math -o cas128 ./cas128.cpp

#include <atomic>
#include <cstddef>
#include <cstdint>
#include <new>
#include <print>
#include <string_view>

template <size_t align>
struct make_aligned_u128
{
	struct alignas(align) type
	{
		uint64_t hi;
		uint64_t lo;
	};
};

template <size_t min_align, size_t max_align>
constexpr void print_is_lock_free_helper()
{
	if constexpr (min_align <= max_align) {
		constexpr size_t align = (min_align);
		auto             b = std::atomic<typename make_aligned_u128<align>::type>::is_always_lock_free;
		std::print("  align {}\t {}\n", align, b);
	}

	if constexpr (min_align < max_align) {
		print_is_lock_free_helper<min_align << 1, max_align>();
	}
}

template <size_t min_align, size_t max_align>
constexpr void print_is_lock_free(std::string_view name)
{
	std::print("{} with alignments from {} to {}\n", name, min_align, max_align);
	print_is_lock_free_helper<min_align, max_align>();
	std::println();
}

int main()
{
	std::println("cache line size: {} bytes", std::hardware_destructive_interference_size);
	std::println("integral alignment: {} bytes", alignof(std::max_align_t));

	// expected true
	std::print("lockfree __uint128_t: {}\n", std::atomic<__uint128_t>::is_always_lock_free);

	print_is_lock_free<8, 4096>("lockfree my_uint128");

	// cas loop to increment a composite my uint128
	{
		std::println("increment a composite my_uint128");
		using type_t = make_aligned_u128<16>::type;
		using atomic_t = std::atomic<type_t>;
		atomic_t value{
		        type_t{1, 2}
        };

		type_t curr{}; // this is not equal to value so at least one CAS will fail, 2 iterations expected
		type_t curr_new{};
		do {
			std::println("  CAS loop, curr = {{ {}, {} }}", curr.hi, curr.lo);
			curr_new = {curr.hi, curr.lo + 1};
		} while (!value.compare_exchange_weak(curr, curr_new, std::memory_order_release,
		                                      std::memory_order_relaxed));

		curr = value.load(std::memory_order_relaxed);
		std::println("  final value = {{ {}, {} }}", curr.hi, curr.lo);
		std::println();
	}

	// incrementing builtin extension __uint128_t requires an explicit CAS in clang/gcc (except apple clang, hehe)
	{
		std::println("increment builtin __int128_t");

		auto const increment_multi = [](__int128_t initial, size_t iterations) {
			alignas(128) std::atomic<__int128_t> v{initial};

			__int128_t expected = v.load(std::memory_order_relaxed);
			for (size_t i = 0; i < iterations; i++) {
				while (!v.compare_exchange_weak(expected, expected + 1, std::memory_order_relaxed,
				                                std::memory_order_relaxed))
					;
			}

			std::println("  {} iterations\t {} -> {}", iterations, initial, v.load());
		};

		increment_multi(1, 1);
		increment_multi(1, 25);
		increment_multi(-1, 25);
	}

	return 0;
}
