# https://leetcode.com/problems/majority-element/

from math import exp
from typing import List


class Solution:
    def majorityElement(self, nums: List[int]) -> int:
        m: dict[int, int] = {}

        for v in nums:
            if v in m:
                m[v] += 1
            else:
                m[v] = 1

        nmajority = len(nums) // 2
        for k, v in m.items():
            if v > nmajority:
                return k

        return -1


def run_test(nums: List[int], expected: int):
    s = Solution()

    val = s.majorityElement(nums)
    print(f"input: {nums} --> {val}, expected: {expected}")
    print(f"{'OK' if val == expected else 'ERROR'}")


if __name__ == "__main__":
    run_test([3, 2, 3], 3)
    run_test([2, 2, 1, 1, 1, 2, 2], 2)
