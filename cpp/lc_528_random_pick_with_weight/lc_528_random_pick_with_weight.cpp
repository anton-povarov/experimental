#include <vector>
#include <string>
#include <cstdio>
#include <algorithm>

using std::vector;

class Solution
{
	std::vector<int> prefix_sums;
	int total_sum;

public:
	Solution(vector<int> &w)
	{
		int prefix_sum = 0;
		prefix_sums.resize(w.size());

		for (size_t i = 0; i < w.size(); i++)
		{
			prefix_sum += w[i];
			prefix_sums[i] = prefix_sum;
		}

		total_sum = prefix_sum;
		srandom(time(NULL));
	}

	int pickIndex()
	{
		int r = random() % total_sum;
		auto const it = std::upper_bound(prefix_sums.begin(), prefix_sums.end(), r);
		return std::distance(prefix_sums.begin(), it);
	}
};

/**
 * Your Solution object will be instantiated and called as such:
 * Solution* obj = new Solution(w);
 * int param_1 = obj->pickIndex();
 */

std::string array_to_string(int const *arr, size_t size)
{
	std::string s;
	s += '{';
	for (size_t i = 0; i < size; i++)
	{
		s += '0' + arr[i];
		if (i != (size - 1))
			s += ',';
	}
	s += '}';
	return s;
}

void run_test(vector<int> const &v, int iterations)
{
	vector<int> picks;
	picks.resize(v.size());

	auto v_lvalue = v;
	Solution s(v_lvalue);
	for (int i = 0; i < iterations; i++)
	{
		int pick = s.pickIndex();
		// printf("pickIndex() -> %d\n", pick);
		picks[pick] += 1;
	}

	printf("vector: %s\n", array_to_string(v.data(), v.size()).c_str());
	printf("iterations: %d\n", iterations);
	for (size_t i = 0; i < picks.size(); i++)
	{
		printf("[%zu] %d\n", i, picks[i]);
	}
}

int main()
{
	run_test({1, 3}, 1000);
}