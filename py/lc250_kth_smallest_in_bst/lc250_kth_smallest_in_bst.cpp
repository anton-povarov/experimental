#include <print>
#include <vector>

// Definition for a binary tree node.
struct TreeNode
{
	int val;
	TreeNode *left;
	TreeNode *right;
	TreeNode() : val(0), left(nullptr), right(nullptr) {}
	TreeNode(int x) : val(x), left(nullptr), right(nullptr) {}
	TreeNode(int x, TreeNode *left, TreeNode *right) : val(x), left(left), right(right) {}
};

class Solution
{
public:
	int kthSmallest(TreeNode *root, int k)
	{
		int result = -1;
		step_to_kth(result, root, k);
		return result;

		// std::vector<int> to;
		// enumerate_to_k(to, root, k);
		// std::print("to: {}\n", to);
		// return to[k - 1];
	}

	// puts elements up to and including k-th into the provided vector
	static void enumerate_to_k(std::vector<int> &to, TreeNode *root, int k)
	{
		if (!root || to.size() >= k)
			return;

		enumerate_to_k(to, root->left, k);
		to.push_back(root->val);
		enumerate_to_k(to, root->right, k);
	}

	// this function does not try to store any elements before k-th
	static void step_to_kth(int &res, TreeNode *root, int &k)
	{
		if (!root)
			return;

		step_to_kth(res, root->left, k);
		if (--k == 0)
		{
			res = root->val;
			return;
		}
		step_to_kth(res, root->right, k);
	}
};

TreeNode *build_tree(std::vector<int> const &v, int offset = 0)
{
	auto *root = new TreeNode(v[offset]);
	if (int off = offset * 2 + 1; off < v.size())
	{
		if (v[off] >= 0)
			root->left = build_tree(v, off);
	}
	if (int off = offset * 2 + 2; off < v.size())
	{
		if (v[off] >= 0)
			root->right = build_tree(v, off);
	}
	return root;
}

void fill_tree_levels(TreeNode *root, auto &levels, int l)
{
	if (levels.size() <= l)
		for (int i = levels.size(); i <= l; i++)
			levels.push_back({});

	levels[l].push_back(root->val);

	if (root->left)
		fill_tree_levels(root->left, levels, l + 1);
	if (root->right)
		fill_tree_levels(root->right, levels, l + 1);
}

auto print_tree(TreeNode *root)
{
	std::vector<std::vector<int>> levels;
	fill_tree_levels(root, levels, 0);

	for (auto const &l : levels)
		std::print("{}\n", l);
}

void print_tree_weird(TreeNode *root, int layer, int offset)
{
	std::print("node: {}, level: {}, offset: {}\n", root->val, layer, offset);

	if (root->left || root->right)
	{
		if (root->left)
			print_tree_weird(root->left, layer + 1, 2 * offset + 1 - (1 << offset));
		if (root->right)
			print_tree_weird(root->right, layer + 1, 2 * offset + 2 - (1 << offset));
		else
			std::print("_\n");
	}

	std::print("{}\n", root->val);
}

void run_test(std::vector<int> &&v, int k, int expected)
{
	TreeNode *root = build_tree(v);
	print_tree(root);
	print_tree_weird(root, 0, 0);

	Solution s;
	int ret = s.kthSmallest(root, k);
	std::print("[{}] ret = {}, expected = {}\n",
			   (ret == expected) ? "OK" : "ERROR",
			   ret, expected);
}

int main()
{
	run_test({3, 1, 4, 10, 2, 20, 30}, 1, 1);
	// run_test({3, 1, 4, -1, 2}, 1, 1);
	// run_test({5, 3, 6, 2, 4, -1, -1, 1}, 3, 3);
}