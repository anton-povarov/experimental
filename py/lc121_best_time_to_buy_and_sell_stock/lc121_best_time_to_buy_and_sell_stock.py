# https://leetcode.com/problems/best-time-to-buy-and-sell-stock/
#
# the idea is to run a 3 scans
# 1. for each index i - find the index of the max value in the [i, len) subinterval, we need to scan backwards
# 2. for each index i - find the index of the min valuein the [0, i) subinterval, scan forward
# 3. for each index i - calculate max_elts[i] - min_elts[i] -> finding the maximum in these diffs
# the index of the maximum found is the answer

import sys
from typing import List

sys.path.insert(0, "..")  # a hacky way, but whatever
from verbose_call import verbose_group


class Solution:
    def maxProfit(self, prices: List[int]) -> int:
        return self._max_profit_3_scans(prices)[0]

    # returns (max_profit, (index_buy, index_sell))
    # the task itself does not ask for indexes, this is my enhancement
    #  (because i'm stupid and misread the task)
    def _max_profit_3_scans(self, prices: List[int]) -> tuple[int, tuple[int, int]]:
        if not prices:
            return (0, (0, 0))

        n = len(prices)

        # scan1 - find max values in [i, len)
        max_prices = [0] * n
        max_prices[n - 1] = n - 1
        for i in reversed(range(0, n - 1)):
            if prices[i] > prices[max_prices[i + 1]]:
                max_prices[i] = i
            else:
                max_prices[i] = max_prices[i + 1]

        # scan2 - find min values in [0, i)
        min_prices = [0] * n
        min_prices[0] = 0
        for i in range(1, n):
            if prices[i] < prices[min_prices[i - 1]]:
                min_prices[i] = i
            else:
                min_prices[i] = min_prices[i - 1]

        # scan3 - find the max diff in price
        max_indexes = (min_prices[0], max_prices[0])
        abs_max = 0
        for i in range(1, n):
            curr_max = prices[max_prices[i]] - prices[min_prices[i]]
            if curr_max > abs_max:
                abs_max = curr_max
                max_indexes = (min_prices[i], max_prices[i])

        return (abs_max, max_indexes)

    # adaptation of Kadane's algorithm for max sum subarray
    # but we track max profit, instead of the max sum
    # resetting the start when profit goes below 0 (as this means we can buy lower now)
    def _max_profit_kadane(self, prices: List[int]) -> int:
        if not prices:
            return 0

        n = len(prices)
        best_profit = 0

        curr_start = 0
        curr_profit = 0
        for i in range(1, n):
            curr_profit = prices[i] - prices[curr_start]
            if curr_profit > best_profit:
                best_profit = curr_profit

            if curr_profit < 0:
                curr_start = i
                best_profit = 0

        return best_profit


if __name__ == "__main__":
    with verbose_group("_max_profit_3_scans") as g:
        g.verbose_call(Solution()._max_profit_3_scans, [7, 1, 5, 3, 6, 4], expected=(5, (1, 4)))
        g.verbose_call(Solution()._max_profit_3_scans, [7, 1, 5, 3, 0, 6, 4], expected=(6, (4, 5)))
        g.verbose_call(Solution()._max_profit_3_scans, [7, 6, 4, 3, 1], expected=(0, (0, 0)))

    with verbose_group("_max_profit_kadane") as g:
        g.verbose_call(Solution()._max_profit_kadane, [7, 1, 5, 3, 6, 4], expected=5)
        g.verbose_call(Solution()._max_profit_kadane, [7, 1, 5, 3, 0, 6, 4], expected=6)
        g.verbose_call(Solution()._max_profit_kadane, [7, 6, 4, 3, 1], expected=0)
        g.verbose_call(Solution()._max_profit_kadane, [7, 6, 4, 3, 1, 4], expected=3)
        g.verbose_call(Solution()._max_profit_kadane, [7, 6, 4, 3, 1, 3], expected=2)
