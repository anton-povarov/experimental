// https://leetcode.com/problems/find-median-from-data-stream/
/**
 * Your MedianFinder object will be instantiated and called as such:
 * MedianFinder* obj = new MedianFinder();
 * obj->addNum(num);
 * double param_2 = obj->findMedian();
 */

// the idea is to keep 2 heaps
// 1. max heap - items less than the median
// 2. min heap - items greater than the median
//
// in addition keep an optional<int> - the current median
//  it's present if the number of elts is odd and merged into one of the heaps when new one is added after that
//
// calculating median is simple
// median present - return
// median not present - get heap heads, avg them
//
// inserting elts
//  find which heap the element goes to between left median right
//  it should be based on keeping the heaps equal size (!)
//  which might involve evacuating heap heads into median, median into heaps, etc.
//
// possible optimization (not tested):
//  do not store full heaps, bucketise beyond certain limit (bucket->count),
//  if the stream is more of less uniform - pull from buckets, will give an approximation

// solutions on leetcode let the heaps unbalance by 1
// and move elements from larger to smaller if unbalanced by more than 1
// LC solution is faster, less push/pop operations, less ifs

#include <cassert>
#include <optional>
#include <print>
#include <queue>

class MedianFinder
{
	std::priority_queue<int, std::vector<int>, std::less<int>> left_heap;     // max heap
	std::priority_queue<int, std::vector<int>, std::greater<int>> right_heap; // min heap
	std::optional<int> median;

public:
	MedianFinder() {}

	void addNum(int num)
	{
		assert(left_heap.size() == right_heap.size());

		// std::print("[{}] ",
		//            (left_heap.empty()) ? std::string("") : std::format("{}", left_heap.top()));
		// std::print("[{}] ", median ? std::format("{}", *median) : std::string("-"));
		// std::print("[{}] ",
		//            (right_heap.empty()) ? std::string("") : std::format("{}", right_heap.top()));
		// std::print("\n");

		if (!median) {
			if (right_heap.empty()) { // both heaps are empty, just initialized
				median = num;
				return;
			}

			if (num >= right_heap.top()) {
				// std::print("no median rpush [{}]->\n", num);
				median = right_heap.top();
				right_heap.pop();
				right_heap.push(num);
			}
			else if (num < left_heap.top()) {
				// std::print("no median lpush <-[{}]\n", num);
				median = left_heap.top();
				left_heap.pop();
				left_heap.push(num);
			}
			else {
				median = num;
			}
			return;
		}

		if (num >= *median) {
			// std::print("median rpush <-[{}] [{}]->\n", *median, num);
			right_heap.push(num);
			left_heap.push(*median);
		}
		else {
			// std::print("median lpush <-[{}] [{}]->\n", num, *median);
			left_heap.push(num);
			right_heap.push(*median);
		}
		median = std::nullopt;
	}

	void add_number_multi(std::vector<int> const &nums)
	{
		for (auto const &num : nums)
			this->addNum(num);
	}

	double findMedian()
	{
		if (median) {
			return *median;
		}

		auto const m = double(left_heap.top() + right_heap.top()) / 2.0;
		return m;
	}
};

class MedianFinder_no_median_as_member
{
	std::priority_queue<int, std::vector<int>, std::less<int>> left_heap;     // max heap
	std::priority_queue<int, std::vector<int>, std::greater<int>> right_heap; // min heap

public:
	MedianFinder_no_median_as_member() {}

	void addNum(int num)
	{
		// std::print("[{}] ",
		//            (left_heap.empty()) ? std::string("") : std::format("{}", left_heap.top()));
		// std::print("[{}] ",
		//            (right_heap.empty()) ? std::string("") : std::format("{}", right_heap.top()));
		// std::print("\n");

		if (!right_heap.empty() && num >= right_heap.top()) {
			right_heap.push(num);
		}
		else {
			left_heap.push(num);
		}

		// balance
		if (right_heap.size() > (left_heap.size() + 1)) {
			left_heap.push(right_heap.top());
			right_heap.pop();
		}
		if (left_heap.size() > (right_heap.size() + 1)) {
			right_heap.push(left_heap.top());
			left_heap.pop();
		}
	}

	void add_number_multi(std::vector<int> const &nums)
	{
		for (auto const &num : nums)
			this->addNum(num);
	}

	double findMedian()
	{
		if (left_heap.size() > right_heap.size())
			return left_heap.top();
		else if (left_heap.size() < right_heap.size())
			return right_heap.top();
		else {
			auto const m = double(left_heap.top() + right_heap.top()) / 2.0;
			return m;
		}
	}
};

int main()
{
	{
		MedianFinder m;
		m.addNum(1);
		m.addNum(2);
		std::print("median = {}\n", m.findMedian());
		m.addNum(3);
		std::print("median = {}\n", m.findMedian());
	}

	{
		MedianFinder m;
		m.add_number_multi({-1, -2, -3, -4, -5});
		std::print("median = {}\n", m.findMedian());
	}

	// {
	// 	MedianFinder m;
	// 	m.add_number_multi({1, 2, 3, 4, 5});
	// 	std::print("median = {}\n", m.findMedian());
	// }

	{
		MedianFinder m;
		m.add_number_multi({40, 12, 16});
		std::print("median = {}\n", m.findMedian());
		m.add_number_multi({14});
		std::print("median = {}\n", m.findMedian());
		m.add_number_multi({35});
		std::print("median = {}\n", m.findMedian());
	}

	{
		MedianFinder_no_median_as_member m;
		m.add_number_multi({40, 12, 16});
		std::print("median = {}\n", m.findMedian());
		m.add_number_multi({14});
		std::print("median = {}\n", m.findMedian());
		m.add_number_multi({35});
		std::print("median = {}\n", m.findMedian());
	}

	return 0;
}