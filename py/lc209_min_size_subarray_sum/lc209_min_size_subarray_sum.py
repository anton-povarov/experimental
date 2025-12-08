# https://leetcode.com/problems/minimum-size-subarray-sum/

from typing import List


class Solution:
    def minSubArrayLen(self, target: int, nums: List[int]) -> int:
        nlen = len(nums)
        if nlen < 1:
            return 0

        min_length = 0

        def maybe_update_min_length(new_length: int):
            nonlocal min_length
            if min_length == 0 or new_length < min_length:
                min_length = new_length
                # print(f"b min_len = {min_length}")

        begin = 0
        end = 0
        curr_sum = 0  # running sum of [begin, end)

        while True:
            # print(f"\nE: {begin} {end} -> {curr_sum}")

            # advance end to find the sum
            while end < nlen and curr_sum < target:
                curr_sum += nums[end]
                end += 1
                # print(f"b: {begin} {end} -> {curr_sum}")

            # no way to extend further, return what we've got
            if curr_sum < target:
                return min_length

            # maybe got something
            maybe_update_min_length(end - begin)

            # advance front to reduce the length if possible
            while begin < end and curr_sum >= target:
                curr_sum -= nums[begin]
                begin += 1
                # print(f"a: {begin} {end} -> {curr_sum}")

            maybe_update_min_length(end - begin + 1)


def run_test(target: int, nums: List[int], expected: int) -> None:
    s = Solution()
    r = s.minSubArrayLen(target, nums)
    print(f"nums: {nums}, target: {target} --> {r}")
    print(f"{'OK' if expected == r else 'ERROR'}")


if __name__ == "__main__":
    run_test(7, [2, 3, 1, 2, 4, 3], 2)
    run_test(4, [1, 4, 4], 1)
    run_test(11, [1, 1, 1, 1, 1, 1, 1, 1], 0)
