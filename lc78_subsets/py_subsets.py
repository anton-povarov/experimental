from typing import List


class Solution:
    def subsets(self, nums: List[int]) -> List[List[int]]:
        result: List[List[int]] = []
        max = 1 << len(nums)
        for subset_id in range(0, max):
            subset_list = [nums[n] for n in range(len(nums)) if (subset_id & (1 << n))]
            # for n in range(0, len(nums)):
            #     if subset_id & (1 << n):
            #         subset_list.append(nums[n])
            result.append(subset_list)
        return result


def run_tests():
    # Helper function to compare two lists of lists,
    # where the order of sublists and order of elements within sublists do not matter.
    def are_equal_sets_of_lists(list1, list2):
        if len(list1) != len(list2):
            return False

        # Sort elements within each sublist and convert sublist to tuple for comparison
        # This makes comparisons like ([1,2] vs [2,1]) and ([[1],[2]] vs [[2],[1]]) consistent.
        processed_list1 = sorted([tuple(sorted(sublist)) for sublist in list1])
        processed_list2 = sorted([tuple(sorted(sublist)) for sublist in list2])

        return processed_list1 == processed_list2

    solution = Solution()

    # Test Case 1: Standard case from problem description
    nums1 = [1, 2, 3]
    # Expected output for [1,2,3] is all 2^3 = 8 subsets.
    # The order produced by the solution is: [[], [1], [2], [1,2], [3], [1,3], [2,3], [1,2,3]]
    # The canonical expected output (sorted sublists, then sorted list of sublists):
    expected1 = [[], [1], [2], [3], [1, 2], [1, 3], [2, 3], [1, 2, 3]]
    actual1 = solution.subsets(nums1)
    assert are_equal_sets_of_lists(actual1, expected1), (
        f"Test Case 1 Failed: nums = {nums1}\nExpected (canonical): {expected1}\nActual: {actual1}"
    )

    # Test Case 2: Larger list
    nums2 = [1, 2, 3, 4]
    expected2 = [
        [],
        [1],
        [2],
        [3],
        [4],
        [1, 2],
        [1, 3],
        [1, 4],
        [2, 3],
        [2, 4],
        [3, 4],
        [1, 2, 3],
        [1, 2, 4],
        [1, 3, 4],
        [2, 3, 4],
        [1, 2, 3, 4],
    ]
    actual2 = solution.subsets(nums2)
    assert are_equal_sets_of_lists(actual2, expected2), (
        f"Test Case 2 Failed: nums = {nums2}\nExpected: {expected2}\nActual: {actual2}"
    )

    # Test Case 3: Empty list
    nums3 = []
    expected3 = [[]]
    actual3 = solution.subsets(nums3)
    assert are_equal_sets_of_lists(actual3, expected3), (
        f"Test Case 3 Failed: nums = {nums3}\nExpected: {expected3}\nActual: {actual3}"
    )

    # Test Case 4: Single element list
    nums4 = [0]
    expected4 = [[], [0]]
    actual4 = solution.subsets(nums4)
    assert are_equal_sets_of_lists(actual4, expected4), (
        f"Test Case 4 Failed: nums = {nums4}\nExpected: {expected4}\nActual: {actual4}"
    )

    # Test Case 5: Unsorted input list
    nums5 = [3, 1, 2]
    # The set of subsets should be the same as for [1,2,3]
    expected5 = [[], [1], [2], [3], [1, 2], [1, 3], [2, 3], [1, 2, 3]]
    actual5 = solution.subsets(nums5)
    assert are_equal_sets_of_lists(actual5, expected5), (
        f"Test Case 5 Failed: nums = {nums5}\nExpected (canonical): {expected5}\nActual: {actual5}"
    )

    # Test Case 6: List with negative numbers
    nums6 = [-1, -2]
    # solution.subsets([-1,-2]) -> [[], [-1], [-2], [-1,-2]]
    # Canonical expected:
    expected6 = [[], [-2], [-1], [-2, -1]]  # Sublists sorted, then list of sublists sorted
    actual6 = solution.subsets(nums6)
    assert are_equal_sets_of_lists(actual6, expected6), (
        f"Test Case 6 Failed: nums = {nums6}\nExpected (canonical): {expected6}\nActual: {actual6}"
    )

    # Test Case 7: List with duplicate numbers
    # The current algorithm treats elements by their index.
    # For nums = [1,1]:
    # Indices are 0, 1. Values are nums[0]=1, nums[1]=1.
    # Subsets of indices: {}, {0}, {1}, {0,1}
    # Corresponding value subsets: [], [nums[0]], [nums[1]], [nums[0],nums[1]]
    # This results in: [[], [1], [1], [1,1]]
    nums7 = [1, 1]
    expected7 = [[], [1], [1], [1, 1]]
    actual7 = solution.subsets(nums7)
    assert are_equal_sets_of_lists(actual7, expected7), (
        f"Test Case 7 Failed: nums = {nums7}\nExpected: {expected7}\nActual: {actual7}"
    )

    # Test Case 8: Another single element list
    nums8 = [7]
    expected8 = [[], [7]]
    actual8 = solution.subsets(nums8)
    assert are_equal_sets_of_lists(actual8, expected8), (
        f"Test Case 8 Failed: nums = {nums8}\nExpected: {expected8}\nActual: {actual8}"
    )

    # Test Case 9: List with mixed positive and negative numbers
    nums9 = [1, -1]
    # solution.subsets([1,-1]) -> [[], [1], [-1], [1,-1]]
    # Canonical expected:
    expected9 = [[], [-1], [1], [-1, 1]]
    actual9 = solution.subsets(nums9)
    assert are_equal_sets_of_lists(actual9, expected9), (
        f"Test Case 9 Failed: nums = {nums9}\nExpected (canonical): {expected9}\nActual: {actual9}"
    )

    print("All tests passed successfully.")


if __name__ == "__main__":
    solution = Solution()
    print(solution.subsets([1, 2, 3]))
    # Expected output: [[], [1], [2], [3], [1, 2], [1, 3], [2, 3], [1, 2, 3]]

    print(solution.subsets([1, 2, 3, 4]))
    # Expected output: [[], [1], [2], [3], [1, 2], [1, 3], [2, 3], [1, 2, 3]]

    run_tests()
