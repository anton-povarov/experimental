#include <algorithm>
#include <array>
#include <print>
#include <unordered_map>
#include <vector>

class Solution
{
public:
	int firstUniqueFreq(std::vector<int> &nums)
	{
		return with_hash_tables_3(nums);
		return with_hash_tables_2(nums);
		return with_hash_tables(nums);
	}

	int with_hash_tables(std::vector<int> const &nums)
	{
		// num -> frequency
		std::unordered_map<int, int> freq;
		for (auto const num : nums) {
			freq[num] += 1;
		}

		// frequency -> [nums with this frequency]
		std::unordered_map<int, std::vector<int>> freq_to_numbers;
		for (auto const [num, count] : freq) {
			freq_to_numbers[count].push_back(num);
		}

		// scan [nums] to find the first one with unique frequency
		for (auto const num : nums) {
			if (freq_to_numbers[freq[num]].size() == 1) {
				return num;
			}
		}

		return -1;
	}

	// same as [with_hash_tables], but just count the frequencies, without storing numbers
	int with_hash_tables_2(std::vector<int> const &nums)
	{
		// num -> frequency
		std::unordered_map<int, int> freq;
		for (auto const num : nums) {
			freq[num] += 1;
		}

		// frequency -> [count of nums with this frequency]
		std::unordered_map<int, int> freq_to_numbers;
		for (auto const [num, count] : freq) {
			freq_to_numbers[count] += 1;
		}

		// scan [nums] to find the first one with unique frequency
		for (auto const num : nums) {
			if (freq_to_numbers[freq[num]] == 1) {
				return num;
			}
		}

		return -1;
	}

	// same as [with_hash_tables], but just use arrays instead of hashes,
	int with_hash_tables_3(std::vector<int> const &nums)
	{
		if (nums.size() == 0) {
			return -1;
		}

		int const        max_val = *std::max_element(nums.begin(), nums.end());
		std::vector<int> num_to_freq(max_val + 1, 0);

		// num -> frequency
		for (auto const num : nums) {
			num_to_freq[num] += 1;
		}

		// frequency -> [count of nums with this frequency]
		std::vector<int> freq_counts(nums.size() + 1, 0);
		for (size_t i = 0; i < num_to_freq.size(); i++) {
			if (num_to_freq[i] != 0) {
				freq_counts[num_to_freq[i]] += 1;
			}
		}

		// scan [nums] to find the first one with unique frequency
		for (auto const num : nums) {
			if (freq_counts[num_to_freq[num]] == 1) {
				return num;
			}
		}

		return -1;
	}
};

void run_test(std::vector<int> nums, int expected)
{
	Solution  s;
	int const res = s.firstUniqueFreq(nums);

	std::println(                                         //
	        "[{}] min_freq_elt: {} -> {}, expected: {} ", //
	        (res == expected) ? "OK" : "ERROR", nums, res, expected);
}

int main()
{
	run_test({20, 10, 30, 30}, 30);
	run_test({20, 20, 10, 30, 30, 30}, 20);
	run_test({10, 10, 20, 20}, -1);

	return 0;
}