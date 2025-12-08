# https://leetcode.com/problems/two-sum-ii-input-array-is-sorted/

import bisect
from typing import List


class Solution:
    def twoSum(self, numbers: List[int], target: int) -> List[int]:
        return self._two_pointers(numbers, target)
        # return self._hash(numbers, target)
        # return self._bisect(numbers, target)

    def _two_pointers(self, numbers: List[int], target: int) -> List[int]:
        l = 0
        r = len(numbers) - 1

        while l < r:
            l_v, r_v = numbers[l], numbers[r]
            two_sum = l_v + r_v
            if two_sum == target:
                return [l + 1, r + 1]

            # we need to increase the sum, move left ptr
            if two_sum < target:
                l += 1
                while l < r and numbers[l] == l_v:
                    l += 1
            # we need to decrease the sum, move right ptr
            else:
                r -= 1
                while l < r and numbers[r] == r_v:
                    r -= 1
        return []

    def _hash(self, numbers: List[int], target: int) -> List[int]:
        # the same as with the unsorted "two numbers" problem
        # turns out to be faster than two pointers :)
        # as measured by LC itself

        d = dict[int, int]()  # number -> index
        for i in range(len(numbers)):
            v = numbers[i]
            other = target - v
            if other in d:
                return [d[other], i + 1]
            d[v] = i + 1
        return []

    def _bisect(self, numbers: List[int], target: int) -> List[int]:
        # can't just bisect the upper bound of search
        # this function needs to support negative numbers and targets
        # consider target = -2, numbers could be 5 and -7
        # i.e. [-7, 1, 2, 3, 5]
        # the hard part comes if there is
        #   a zillion large negatives at the start
        # large positives at the end are elimited by bisect naturally
        begin = 0
        if target < 0:
            begin = bisect.bisect_left(numbers, target)
        for i in range(begin, len(numbers)):
            v = target - numbers[i]
            upper = bisect.bisect_right(numbers, v)
            if upper < i + 1:
                continue
            if numbers[upper - 1] == v:
                return [i + 1, upper]
        return []
