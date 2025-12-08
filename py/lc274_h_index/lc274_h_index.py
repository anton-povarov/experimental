# https://leetcode.com/problems/h-index/
# the h-index is "max number H that there are more than H citations with rating >= H"
# According to the definition of h-index on Wikipedia:
#   The h-index is defined as the maximum value of h such that the given researcher
#   has published at least h papers that have each been cited at least h times.
# (I did the sorting approach without hints)
# Hint_1: An easy approach is to sort the array first.
# hint_2: What are the possible values of h-index?
# Hint_3: A faster approach is to use extra space.

import sys
from typing import List


sys.path.insert(0, "..")  # a hacky way, but whatever
from verbose_call import verbose_group


class Solution:
    def hIndex(self, citations: List[int]) -> int:
        # return self._hIndex_sorting(citations)
        return self._hIndex_counting(citations)

    def _hIndex_counting(self, citations: List[int]) -> int:
        if not citations:
            return 0

        # n_citations => publications_count
        # the limit given is: 0 <= citations[i] <= 1000
        # but we'll use max value from citations, as it's likely lower
        counts = [0] * (max(citations) + 1)
        for cit in citations:
            counts[cit] += 1

        # print()
        # print(f"counts = {counts}")

        sum = 0
        cit_i = len(counts) - 1
        while cit_i >= 0:
            # print(f"cit_i = {cit_i}, sum = {sum}, inc = {counts[cit_i]}")
            sum += counts[cit_i]
            if sum >= cit_i:
                return cit_i
            cit_i -= 1

        return 0

    def _hIndex_sorting(self, citations: List[int]) -> int:
        citations = sorted(citations)

        n = len(citations)
        hirch: int = 0

        for i in range(n):
            this_cit = citations[i]

            # this has turned out to be not needed as
            # 1. all numbers are >= 0
            # 2. numbers are sorted
            # 3. we start at 0
            #
            # if this_cit < hirch:
            #     return hirch

            # the next (n-i) publications have received >= `hirch` citations
            # actually, they have received >= this_cit citations
            # but it remains to be seen that we can satisfy "at least H publications must exist"

            # the remaining publications are highly rated, but there's few of them
            if (n - i) <= this_cit:
                return n - i

            # there is a lot more publications, need to look at them
            else:
                hirch = this_cit

        return hirch


if __name__ == "__main__":
    with verbose_group("_hindex_sorting") as g:
        g.verbose_call(Solution()._hIndex_sorting, [], expected=0)
        g.verbose_call(Solution()._hIndex_sorting, [0, 0, 0], expected=0)
        g.verbose_call(Solution()._hIndex_sorting, [0, 0, 1], expected=1)
        g.verbose_call(Solution()._hIndex_sorting, [3, 0, 6, 1, 5], expected=3)
        g.verbose_call(Solution()._hIndex_sorting, [0, 1, 1, 5, 6, 7], expected=3)
        g.verbose_call(Solution()._hIndex_sorting, [0, 1, 1, 5, 5, 6, 7], expected=4)
        g.verbose_call(Solution()._hIndex_sorting, [100], expected=1)
        g.verbose_call(Solution()._hIndex_sorting, [2, 100], expected=2)
        g.verbose_call(Solution()._hIndex_sorting, [2, 2], expected=2)
        g.verbose_call(Solution()._hIndex_sorting, [2, 2, 3, 3, 3], expected=3)

    with verbose_group("_hindex_counts") as g:
        g.verbose_call(Solution()._hIndex_counting, [], expected=0)
        g.verbose_call(Solution()._hIndex_counting, [0, 0, 0], expected=0)
        g.verbose_call(Solution()._hIndex_counting, [0, 0, 1], expected=1)
        g.verbose_call(Solution()._hIndex_counting, [3, 0, 6, 1, 5], expected=3)
        g.verbose_call(Solution()._hIndex_counting, [0, 1, 1, 5, 6, 7], expected=3)
        g.verbose_call(Solution()._hIndex_counting, [0, 1, 1, 5, 5, 6, 7], expected=4)
        g.verbose_call(Solution()._hIndex_counting, [10], expected=1)
        g.verbose_call(Solution()._hIndex_counting, [2, 10], expected=2)
        g.verbose_call(Solution()._hIndex_counting, [2, 2], expected=2)
        g.verbose_call(Solution()._hIndex_counting, [2, 2, 3, 3, 3], expected=3)
