// https://leetcode.com/problems/product-of-array-except-self/

#include <vector>
#include <print>
#include <cstdlib>

using std::vector;

class Solution
{
public:
	//
	// A B C D
	// prefix = [ 1, A, AB, ABC ] -- product of everything up to this element
	// suffix = [ CDB, DC, D, 1 ] -- product of everything past this element, reversed (to compute in one loop)
	// result = prefix * suffix = [ CDB, A*DC, AB*D, ABC ]
	//
	// to save memory - split into two passes
	// 1. allocate result array (is not counted as "space complexity" as per leetcode)
	// 2. forward pass - write prefix sums to result array
	// 3. backward pass - multiply directly into the result array
	//

	vector<int> productExceptSelf(vector<int> &nums)
	{
		return productExceptSelf_less_memory(nums);
		// return productExceptSelf_simple(nums);
	}

	vector<int> productExceptSelf_less_memory(vector<int> &nums)
	{
		int const nums_size = nums.size();

		vector<int> result(nums_size);

		result[0] = 1;
		for (int i = 1; i < nums_size; ++i)
			result[i] = result[i - 1] * nums[i - 1];

		int prod = 1;
		for (int i = 1; i < nums_size; ++i)
		{
			prod *= nums[nums_size - i];
			result[nums_size - 1 - i] *= prod;
		}

		return std::move(result);
	}

	vector<int> productExceptSelf_simple(vector<int> &nums)
	{
		int const nums_size = nums.size();

		// vector<int> prefix_prods(nums_size);
		// vector<int> suffix_prods(nums_size);

		int *prefix_prods = (int *)alloca(sizeof(int) * nums_size);
		int *suffix_prods = (int *)alloca(sizeof(int) * nums_size);

		prefix_prods[0] = 1;
		suffix_prods[nums_size - 1] = 1;
		for (int i = 1; i < nums_size; ++i)
		{
			prefix_prods[i] = prefix_prods[i - 1] * nums[i - 1];
			suffix_prods[nums_size - 1 - i] = suffix_prods[nums_size - i] * nums[nums_size - i];
		}

		// std::print("p: {}\n", prefix_prods);
		// std::print("s: {}\n", suffix_prods);

		for (int i = 0; i < nums_size; i++)
		{
			nums[i] = prefix_prods[i] * suffix_prods[i];
		}

		return std::move(nums);
	}
};

void run_test(std::vector<int> nums, std::vector<int> expected)
{
	Solution s;
	auto const result = s.productExceptSelf(nums);

	std::print("nums: {}, expected: {}\n", nums, expected);
	std::print("result: {}\n", result);
	std::print("{}\n\n", (expected == result) ? "OK" : "ERROR");
}

int main()
{
	run_test({2, 3, 4, 5}, {60, 40, 30, 24});
	run_test({1, 2, 3, 4}, {24, 12, 8, 6});
	run_test({-1, 1, 0, -3, 3}, {0, 0, 9, 0, 0});
}
