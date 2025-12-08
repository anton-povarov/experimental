# https://leetcode.com/problems/insert-interval/

from math import exp
from typing import List
import bisect


class Solution:
    def insert(self, intervals: List[List[int]], newInterval: List[int]) -> List[List[int]]:
        # find the interval we're adjacent to by start_i offset
        # after: newInterval[0] <= intervals[begin][0]
        begin = bisect.bisect(intervals, newInterval[0], key=lambda x: x[0])

        # now fight the right bound
        # after: newInterval[1] <= intervals[end][1]
        end = bisect.bisect(intervals, newInterval[1], key=lambda x: x[1])

        # print(f"begin: {begin}, end: {end}")

        # maybe merge to the left
        if begin > 0:
            if newInterval[0] <= intervals[begin - 1][1]:  # do we overlap with prev interval end
                newInterval[0] = intervals[begin - 1][0]
                begin -= 1

        # maybe merge to the right
        if end < len(intervals):
            if newInterval[1] >= intervals[end][0]:  # do we overlap with prev interval start?
                newInterval[1] = intervals[end][1]
                end += 1

        return intervals[:begin] + [newInterval] + intervals[end:]


def run_test(intervals: List[List[int]], newInterval: List[int], expected: List[List[int]]):
    print(f"input: {intervals} + {newInterval}")
    print(f"expected {expected}")
    s = Solution()
    res = s.insert(intervals, newInterval)
    print(f"result:  {res}")
    print(f"{'OK' if res == expected else 'ERROR'}")
    pass


if __name__ == "__main__":
    run_test(intervals=[[1, 3], [6, 9]], newInterval=[2, 5], expected=[[1, 5], [6, 9]])

    run_test(
        intervals=[[1, 2], [3, 5], [6, 7], [8, 10], [12, 16]],
        newInterval=[4, 8],
        expected=[[1, 2], [3, 10], [12, 16]],
    )
