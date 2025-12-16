#include <algorithm>
#include <functional>
#include <print>
#include <random>
#include <string>
#include <vector>

#include "meow/stopwatch.hpp"

template <class T, class CompareF>
struct bench_data_t
{
	std::string                 name;
	std::vector<std::vector<T>> inputs;
	CompareF                    compare;
};

template <class T, class CompareF, class GenFunc>
auto generate_benchmark_data(GenFunc gen_item_func, CompareF compare)
        -> std::vector<bench_data_t<T, CompareF>>
{
	struct rnd_settings_t
	{
		std::string name;
		size_t      n_lists;
		size_t      list_len;
	};
	auto rnd_settings = std::vector<rnd_settings_t>{
	        {"single",     1,    10  }, // single list
	        {"few_short",  10,   20  }, // a few short lists
	        {"few_long",   10,   500 }, // a few long lists
	        {"many_short", 1000, 10  }, // many short lists
	        {"many_long",  1000, 1000}  // many long lists
	};

	std::vector<bench_data_t<T, CompareF>> bdata = {};

	for (auto const settings : rnd_settings) {
		auto bd = bench_data_t<T, CompareF>{
		        .name = settings.name,
		        .inputs = {},
		        .compare = compare,
		};
		bd.inputs.reserve(settings.n_lists);

		for (size_t i = 0; i < settings.n_lists; i++) {
			std::vector<T> input;
			input.reserve(settings.list_len);
			for (int j = 0; j < settings.list_len; j++) {
				input.emplace_back(gen_item_func());
			}
			std::sort(input.begin(), input.end(), compare);
			bd.inputs.push_back(std::move(input));
		}

		bdata.push_back(std::move(bd));
	}

	return bdata;
}

auto generate_benchmark_data_ints()
{
	std::mt19937_64 rnd_gen{std::random_device{}()};
	auto const      gen_random_int = [&]() -> uint64_t { return rnd_gen(); };
	return generate_benchmark_data<uint64_t>(gen_random_int, std::less<uint64_t>{});
}

struct blob_t
{
	int64_t v[8];

	inline bool operator<(blob_t const &other) const { return v[0] < other.v[0]; }
};

auto generate_benchmark_data_blobs()
{
	std::mt19937 rnd_gen{std::random_device{}()};
	auto const   gen_random_blob = [&]() {
        blob_t b{};
        b.v[0] = rnd_gen();
        return b;
	};
	return generate_benchmark_data<blob_t>(gen_random_blob, std::less<blob_t>{});
}

// hand coded (take from Go source) algorithm to push the updated head down the heap
template <class Cont, class CompareF>
bool down(Cont &heap, CompareF compare, ssize_t i0, ssize_t n)
{
	ssize_t i = i0;
	while (true) {
		ssize_t j1 = 2 * i + 1;
		if (j1 >= n || j1 < 0) { // j1 < 0 after int overflow
			break;
		}
		ssize_t j = j1; // left child
		ssize_t j2 = j1 + 1;
		if (j2 < n && !compare(heap[j2], heap[j1])) {
			j = j2; // = 2*i + 2  // right child
		}
		if (compare(heap[j], heap[i])) {
			break;
		}
		std::swap(heap[i], heap[j]);
		i = j;
	}
	return i > i0;
}

template <class T, class CompareF>
    requires(std::is_nothrow_copy_assignable_v<T>,    // for caching the value
             std::is_nothrow_copy_constructible_v<T>) // for pushing back into result
auto merge_sorted_lists_value_copy(std::vector<std::vector<T>> const &inputs, CompareF compare)
        -> std::vector<T>
{
	struct head_t
	{
		union {
			T        value;
			uint64_t __dummy;
		};
		struct
		{
			uint32_t input_idx;
			uint32_t input_pos;
		};
	};

	std::vector<head_t> heads;
	heads.reserve(inputs.size());

	auto const head_compare = [&compare](head_t const &l, head_t const &r) {
		return !compare(l.value, r.value);
	};

	size_t total_len = 0;
	for (size_t i = 0; i < inputs.size(); i++) {
		auto const &inp = inputs[i];
		if (!inp.empty()) {
			heads.push_back(head_t{inp[0], uint32_t(i), 0});
			total_len += inp.size();
		}
	}

	std::vector<T> result;
	result.reserve(total_len);

	std::make_heap(heads.begin(), heads.end(), head_compare);
	while (!heads.empty()) {
		auto &head = heads[0];

		result.push_back(head.value);

		if ((head.input_pos + 1) == uint32_t(inputs[head.input_idx].size())) {
			std::pop_heap(heads.begin(), heads.end(), head_compare);
			heads.pop_back();
		}
		else {
			head.input_pos++;
			head.value = inputs[head.input_idx][head.input_pos];
			down(heads, head_compare, 0, ssize_t(heads.size()));

			// std::pop_heap(heads.begin(), heads.end(), head_compare);
			// auto &update_head = heads.back();
			// update_head.input_pos++;
			// update_head.value = inputs[update_head.input_idx][update_head.input_pos];
			// std::push_heap(heads.begin(), heads.end(), head_compare);
		}
	}

	return result;
}

template <class T, class CompareF>
    requires std::is_nothrow_copy_constructible_v<T> // for pushing back into result
std::vector<T> merge_sorted_lists_value_ptr(std::vector<std::vector<T>> const &inputs, CompareF compare)
{
	struct head_t
	{
		T const *curr;
		T const *end;
	};

	std::vector<head_t> heads;
	heads.reserve(inputs.size());

	auto const head_compare = [&compare](head_t const &l, head_t const &r) {
		return !compare(*l.curr, *r.curr);
	};

	size_t total_len = 0;
	for (auto const &inp : inputs) {
		if (!inp.empty()) {
			heads.push_back(head_t{&*inp.begin(), &*inp.end()});
			total_len += inp.size();
		}
	}

	std::vector<T> result;
	result.reserve(total_len);

	std::make_heap(heads.begin(), heads.end(), head_compare);
	while (!heads.empty()) {
		auto &[curr, end] = heads[0];

		result.push_back(*curr);

		if ((curr + 1) < end) {
			curr++;
			down(heads, head_compare, 0, ssize_t(heads.size()));
			// std::pop_heap(heads.begin(), heads.end(), head_compare);
			// heads[heads.size() - 1].curr++;
			// std::push_heap(heads.begin(), heads.end(), head_compare);
		}
		else {
			std::pop_heap(heads.begin(), heads.end(), head_compare);
			heads.pop_back();
		}
	}

	return result;
}

template <class T, class CompareF, class F>
void run_benchmark(std::string name, F merge_f, std::vector<bench_data_t<T, CompareF>> const &bdata)
{
	meow::stopwatch_t sw;

	std::print("{}\n", name);
	for (auto const &bd : bdata) {
		std::print("bd {}_{}_{}\t\t", bd.name, bd.inputs.size(), bd.inputs[0].size());

		size_t total_size = 0;
		for (auto const &inp : bd.inputs) {
			total_size += inp.size();
		}

		size_t const n_iterations = std::max<size_t>(1, (10 * 1000 * 1000) / total_size);
		for (size_t i = 0; i < n_iterations; i++) {
			auto const res = merge_f(bd.inputs, bd.compare);
			(void)res;
		}

		auto const elapsed = uint64_t(timeval_to_double(sw.stamp()) * 1000 * 1000 * 1000);
		std::print("{} iterations, {} ns/iter\n", n_iterations, elapsed / n_iterations);
	}
	std::print("\n");
}

template <class F>
void run_test(std::string name, F merge_f)
{
	std::vector<std::vector<int>> inputs = {
	        {1, 2, 5},
	        {-1},
	        {4, 8, 9},
	};
	std::vector<int> expected = {-1, 1, 2, 4, 5, 8, 9};
	auto const       res = merge_f(inputs, std::less<int>{});

	if (expected == res) {
		std::print("{}: test ok\n", name);
	}
	else {
		std::print("{}: test failed\n", name);
		std::print("expected: {}\n", expected);
		std::print("res: {}\n", res);
	}
}

int main()
{
	auto const value_f = [](auto v, auto comp) { return merge_sorted_lists_value_copy(v, comp); };
	auto const ptrs_f = [](auto v, auto comp) { return merge_sorted_lists_value_ptr(v, comp); };

	run_test("value", value_f);
	run_test("ptrs", ptrs_f);

	run_benchmark("value_ints", value_f, generate_benchmark_data_ints());
	run_benchmark("value_blobs", value_f, generate_benchmark_data_blobs());

	run_benchmark("ptrs_ints", ptrs_f, generate_benchmark_data_ints());
	run_benchmark("ptrs_blobs", ptrs_f, generate_benchmark_data_blobs());
	return 0;
}