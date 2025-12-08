#include <vector>
#include <iostream>
#include <string>
#include <format>

using std::vector;

struct Solution
{
	vector<vector<int>> subsets(vector<int> nums)
	{
		vector<vector<int>> res = {{}}; // this is crucial, start with an empty subset

		for (int num : nums)
		{
			int size = res.size();
			for (int i = 0; i < size; i++)
			{
				vector<int> subset = res[i];
				subset.push_back(num);
				res.push_back(subset);
			}
		}

		return res;
	}
};

int main()
{
	Solution s;
	{
		auto const subsets = s.subsets({1, 2, 3});
		std::cout << std::format("{}", subsets) << std::endl;
		// std::print("{}\n", subsets);
		// std::cout << std::format("{}\n", subsets[0]) << std::endl;
		// {
		//     std::cout << "[";
		//     for (size_t i = 0; i < s.size(); ++i)
		//     {
		//         if (i > 0)
		//             std::cout << ",";
		//         std::cout << s[i];
		//     }
		//     std::cout << "]";
		// }
		// std::cout << std::endl;
	}

	return 0;
}