// https://www.reddit.com/r/leetcode/comments/1nf8rcs/meta_ic5_interview_experience/
// A variation that combined aspects of LC-23 and LC-215.
// I believe the question was to find the smallest K elements from a list of sorted lists.

#include <algorithm>
#include <deque>
#include <print>
#include <queue>
#include <vector>

std::vector<int> find_smallest_k(std::vector<std::deque<int>> &lists, int k)
{
	std::vector<int> result;
	std::vector<int> heap;
	// heap.resize(k, 0);

	while (k > 0) {
		if (!heap.empty()) {
			std::pop_heap(heap.begin(), heap.end());
			result.push_back(heap.back());
			heap.pop_back();

			if (--k == 0)
				break;
		}

		int min_index = -1;
		for (int i = 0; i < lists.size(); i++) {
			if (lists[i].empty())
				continue;

			if ((min_index < 0) ||
			    (!lists[min_index].empty() && (lists[i].front() < lists[min_index].front())))
				min_index = i;
		}

		heap.push_back(lists[min_index].front());
		lists[min_index].pop_front();
		std::push_heap(heap.begin(), heap.end());
	}

	return result;
}

std::vector<int> find_smallest_k_vectors(std::vector<std::vector<int>> &lists, int k)
{
	std::vector<int> result;

	size_t const lists_size = lists.size();
	std::vector<int> list_offsets(lists_size, 0); // offsets of the items to be taken from lists[i]
	using queue_item_t = std::tuple<int, int>;    // [number, list_index]
	using queue_t      = std::priority_queue<queue_item_t, std::vector<queue_item_t>,
	                                         std::greater<queue_item_t>>;
	queue_t queue;

	for (int i = 0; i < lists_size; i++) {
		if (lists[i].empty())
			continue;

		if (queue.size() < k) {
			queue.push({lists[i].front(), i});
			list_offsets[i]++;
			continue;
		}

		auto const &[queue_smallest, _] = queue.top();
		if (queue_smallest < lists[i].front()) {
			queue.pop();
			// `queue_smallest` lifetime ends here!
			queue.push({lists[i].front(), i});
			list_offsets[i]++;
			continue;
		}
	}

	while (!queue.empty()) {

		auto const &[top_number, tlist_index] = queue.top();

		result.push_back(top_number);
		queue.pop();

		if (--k == 0)
			break;

		int min_index = -1;

		// can we take an item from the just popped list?
		int tlist_offset = list_offsets[tlist_index];
		if (tlist_offset < lists[tlist_index].size()) {
			min_index = tlist_index;
		}

		// find `min_index` = index of the list with smallest elt at the top
		// current list tops are stored in `list_offsets`
		if (min_index < 0) {
			// take the smallest item from any list
			for (int i = 0; i < lists_size; i++) {

				// is there more items to take from i-th list?
				if (list_offsets[i] >= lists[i].size())
					continue;

				if (min_index < 0) { // no current minimum
					min_index = i;
					continue;
				}

				int const min_item  = lists[min_index][list_offsets[min_index]];
				int const candidate = lists[i][list_offsets[i]];
				if (candidate < min_item) {
					min_index = i;
				}
			}
		}

		if (min_index >= 0) {
			queue.push({lists[min_index][list_offsets[min_index]], min_index});
			list_offsets[min_index]++;
		}
	}

	return result;
}

int main()
{
	{
		std::vector<std::deque<int>> lists = {{1, 3, 4}, {-1, 2}};
		auto result                        = find_smallest_k(lists, 3);
		std::print("res = {}\n", result);
	}

	{
		std::vector<std::vector<int>> lists = {{1, 3, 4}, {-1, 2}, {-20}};
		auto result                         = find_smallest_k_vectors(lists, 3);
		std::print("res = {}\n", result);
	}
	return 0;
}