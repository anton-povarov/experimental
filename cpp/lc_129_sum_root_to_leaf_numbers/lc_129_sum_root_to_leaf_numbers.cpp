// original thread I started exploring from
// https://www.reddit.com/r/leetcode/comments/1nf8rcs/meta_ic5_interview_experience/
//
// the task itself
// https://leetcode.com/problems/sum-root-to-leaf-numbers/

#include <cmath>
#include <cstdint>
#include <cstdio>
#include <print>
#include <string>
#include <vector>

// Definition for a binary tree node.
struct TreeNode
{
	int val;
	TreeNode *left;
	TreeNode *right;
	TreeNode()
	    : val(0)
	    , left(nullptr)
	    , right(nullptr)
	{}
	TreeNode(int x)
	    : val(x)
	    , left(nullptr)
	    , right(nullptr)
	{}
	TreeNode(int x, TreeNode *left, TreeNode *right)
	    : val(x)
	    , left(left)
	    , right(right)
	{}
};

class Solution
{
public:
	int sumNumbers(TreeNode *root) { return sum_numbers_recursive(root, 0); }

	std::vector<int> listNumbers(TreeNode *root)
	{
		std::vector<int> v;
		list_numbers_recursive(root, 0, v);
		return v;
	}

private:
	int sum_numbers_recursive(TreeNode *root, unsigned int curr_number)
	{
		if (!root)
			return 0;

		// detect integer overflow, without using INT_MAX
		// unsigned int v = root->val; // make it unsigned
		// if (curr_number * 10 + v < curr_number)
		// {
		// 	// overflow detected
		// 	return 0;
		// }

		int value = curr_number * 10 + root->val;

		if (!root->left && !root->right) {
			// printf("got num: %d\n", value);
			return value;
		}

		int l = sum_numbers_recursive(root->left, value);
		int r = sum_numbers_recursive(root->right, value);

		// maybe add integer overflow detection?
		return l + r;
	}

	void list_numbers_recursive(TreeNode *root, int root_number, std::vector<int> &out)
	{
		if (!root)
			return;

		root_number = root_number * 10 + root->val;

		if (!root->left && !root->right) {
			out.push_back(root_number);
			return;
		}

		list_numbers_recursive(root->left, root_number, out);
		list_numbers_recursive(root->right, root_number, out);
	}
};

// ------------------------------------------------------------------------------------------------

constexpr int log2_constexpr(unsigned int n)
{
	int count = 0;
	while (n > 1) {
		n >>= 1; // Right shift by 1 is equivalent to division by 2
		count++;
	}
	return count;
}

// ------------------------------------------------------------------------------------------------

void dump_tree_array(int const *a, size_t len)
{
	int const levels = log2_constexpr(len) + 1;

	size_t num_items_last_level = 1 << (levels - 1);
	size_t max_print_width      = num_items_last_level * 2 + 1;
	// printf("levels: %d, num_items_last_level: %zu, max_print_width: %zu\n", levels, num_items_last_level, max_print_width);

	for (int level = 0; level < levels; level++) {
		size_t offset    = (1 << level) - 1;
		size_t num_items = 1 << level;

		// calculate padding
		int width = (max_print_width / num_items);
		int l_pad = ceil(width / 2);
		int r_pad = width - l_pad - 1;
		// printf("padding[%d]: %d, %d\n", level, l_pad, r_pad);

		for (size_t i = 0; i < num_items; i++) {
			for (int p = 0; p < l_pad; p++)
				printf(" ");

			if ((offset + i) < len)
				printf("%d", a[offset + i]);
			else
				printf("_");

			for (int p = 0; p < r_pad; p++)
				printf(" ");
		}
		printf("\n");
	}
}

// ------------------------------------------------------------------------------------------------

template <size_t N>
TreeNode *make_tree__dfs(int const (&arr)[N], int offset = 0)
{
	if (offset >= N)
		return nullptr;

	TreeNode *r = new TreeNode(arr[offset]);
	r->left     = make_tree__dfs(arr, 2 * offset + 1);
	r->right    = make_tree__dfs(arr, 2 * offset + 2);
	return r;
}

template <size_t N>
void make_tree__bfs_helper(int const (&arr)[N], size_t offset = 0, TreeNode *r = nullptr)
{
	if ((offset * 2 + 1) < N)
		r->left = new TreeNode(arr[offset * 2 + 1]);

	if ((offset * 2 + 2) < N)
		r->right = new TreeNode(arr[offset * 2 + 2]);

	if (r->left || r->right) {
		printf("node: %d  %d | ", r->left ? r->left->val : -1, r->right ? r->right->val : -1);

		if (r->left)
			make_tree__bfs_helper(arr, offset * 2 + 1, r->left);
		if (r->right)
			make_tree__bfs_helper(arr, offset * 2 + 2, r->right);
	}
	printf("\n");
}

template <size_t N>
TreeNode *make_tree__bfs(int const (&arr)[N], size_t offset = 0)
{
	TreeNode *r = new TreeNode(arr[offset]);
	printf("root: %d\n", arr[offset]);

	make_tree__bfs_helper(arr, offset, r);
	return r;
}

template <size_t N>
TreeNode *make_tree(int const (&arr)[N], size_t offset = 0)
{
	// auto *t = make_tree__bfs(arr, offset);
	auto *t = make_tree__dfs(arr, offset);
	return t;
}

template <size_t N>
std::string array_to_string(int const (&arr)[N])
{
	std::string s;
	s += '{';
	for (size_t i = 0; i < N; i++) {
		s += '0' + arr[i];
		if (i != (N - 1))
			s += ',';
	}
	s += '}';
	return s;
}

template <size_t N>
void run_test(int const (&arr)[N], int expected_sum)
{
	TreeNode *r = make_tree(arr, 0);

	Solution s;
	int sum = s.sumNumbers(r);

	printf("array: %s\n", array_to_string(arr).c_str());
	dump_tree_array(arr, N);
	printf("expected: %d, got: %d\n", expected_sum, sum);
	if (expected_sum == sum) {
		printf("  OK\n");
	}
	else {
		printf("  ERROR: sum does not match expected\n");
	}
	printf("\n");
}

template <size_t N>
void run_test_list(int const (&arr)[N])
{
	TreeNode *r = make_tree(arr, 0);

	Solution s;
	auto const nums_v = s.listNumbers(r);

	printf("array: %s\n", array_to_string(arr).c_str());
	dump_tree_array(arr, N);

	std::print("nums_v = {}\n", nums_v);
}

int main()
{
	// TreeNode *r = make_tree({1, 2, 3}, 0);

	// Solution s;
	// int sum = s.sumNumbers(r);

	// printf("sum: %d\n", sum);

	run_test({1, 2, 3}, 25);
	run_test({4, 9, 0, 5, 1}, 1026);
	run_test({4, 9, 0, 5, 1, 3}, 1389);
	run_test({1, 1, 1, 1, 1, 1, 1, 1}, 22);
	run_test({1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2}, 22);

	run_test_list({1, 2, 3});
	run_test_list({4, 9, 0, 5, 1});
	run_test_list({4, 9, 0, 5, 1, 3});
	run_test_list({1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2});

	return 0;
}
