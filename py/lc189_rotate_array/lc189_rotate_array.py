# https://leetcode.com/problems/rotate-array/
# Given an integer array nums, rotate the array to the right by k steps, where k is non-negative.

import sys
from typing import Callable, List

sys.path.insert(0, "..")  # a hacky way, but whatever
from verbose_call import verbose_group


class Solution:
    def rotate(self, nums: List[int], k: int) -> None:
        """
        Do not return anything, modify nums in-place instead.
        """
        # new_nums = self._rotate_with_copy(nums, k)
        new_nums = self._rotate_with_copy_extend(nums, k)

        for i, n in enumerate(new_nums):
            nums[i] = n

    def _rotate_with_copy(self, nums: List[int], k: int):
        nums_copy = []
        nums_len = len(nums)

        for i in range(nums_len):
            nums_copy.append(nums[(len(nums) - k + i) % nums_len])

        return nums_copy

    def _rotate_with_copy_extend(self, nums: List[int], k: int):
        nums_copy = []
        nums_copy.extend(nums[len(nums) - k :])
        nums_copy.extend(nums[: len(nums) - k])
        return nums_copy

    # O(k) to copy k elts + O(len-k) to top remaining + O(k) to copy k elts back
    # O(k) extra mem
    def _rotate_with_copy_o_of_k_space(self, nums: List[int], k: int):
        nums_len = len(nums)
        k %= nums_len

        # todo: can reduce the copy, by chosing the smallest array of k and len-k
        k_copy = nums[nums_len - k :].copy()
        for i in reversed(range(nums_len)):
            nums[i] = nums[i - k]
        for i in range(k):
            nums[i] = k_copy[i]
        return nums

    # found here
    # https://leetcode.com/problems/rotate-array/solutions/7184902/brute-force-to-optimised-approach-java-p-z4yy/
    # the idea is to reverse the array in full, and then reverse the two parts back _independently_
    # not sure if this will actually be faster than copying, given the very linear copy pattern
    def _rotate_with_reverse(self, nums: List[int], k: int):
        n = len(nums)
        k %= n

        def reverse(left_i, right_i):
            while left_i < right_i:
                nums[left_i], nums[right_i] = nums[right_i], nums[left_i]
                left_i += 1
                right_i -= 1

        reverse(0, n - 1)
        reverse(0, k - 1)
        reverse(k, n - 1)
        return nums


def rotate(nums: List[int], k: int):
    Solution().rotate(nums, k)
    return nums


def rotate_inplace_wrapper(func: Callable):
    def wrap(*args, **kwargs):
        func(*args, **kwargs)
        return args[0]

    return wrap


if __name__ == "__main__":
    with verbose_group("rotate_with_copy_extend") as g:
        g.verbose_call(
            Solution()._rotate_with_copy_extend,
            [1, 2, 3, 4, 5, 6, 7],
            k=3,
            expected=[5, 6, 7, 1, 2, 3, 4],
        )

    with verbose_group("rotate_with_copy") as g:
        g.verbose_call(
            Solution()._rotate_with_copy,
            [1, 2, 3, 4, 5, 6, 7],
            k=3,
            expected=[5, 6, 7, 1, 2, 3, 4],
        )

    with verbose_group("_rotate_with_copy_o_of_k_space") as g:
        g.verbose_call(
            Solution()._rotate_with_copy_o_of_k_space,
            [1, 2, 3, 4, 5, 6, 7],
            k=3,
            expected=[5, 6, 7, 1, 2, 3, 4],
        )
        g.verbose_call(
            Solution()._rotate_with_copy_o_of_k_space,
            [1, 2, 3, 4, 5, 6, 7],
            k=7,
            expected=[1, 2, 3, 4, 5, 6, 7],
        )
        g.verbose_call(
            Solution()._rotate_with_copy_o_of_k_space,
            [1, 2, 3, 4, 5, 6, 7],
            k=50,  # large k here, normalized internally
            expected=[7, 1, 2, 3, 4, 5, 6],
        )

    with verbose_group("_rotate_with_reverse") as g:
        g.verbose_call(
            Solution()._rotate_with_reverse,
            [1, 2, 3, 4, 5, 6, 7],
            k=3,
            expected=[5, 6, 7, 1, 2, 3, 4],
        )
