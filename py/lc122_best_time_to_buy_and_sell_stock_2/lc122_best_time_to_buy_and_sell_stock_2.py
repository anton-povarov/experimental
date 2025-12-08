# https://leetcode.com/problems/best-time-to-buy-and-sell-stock-ii/
#
# This is similar to LC 121. Best time to buy and sell stock
# The difference as i understand it - we should return all such subarrays with max profits
#

import sys
from typing import List

sys.path.insert(0, "..")  # a hacky way, but whatever
from verbose_call import verbose_group


class Solution:
    def maxProfit(self, prices: List[int]) -> int:
        return self._max_profit_all_kadane(prices)[0]

    def _max_profit_all_kadane(self, prices: List[int]) -> tuple[int, list[int]]:
        if not prices:
            return (0, [])

        n = len(prices)

        # last elt of this array is our latest max profit in a kadane's subarray
        # this avoids code duplication after we've exited the loop and need to handle the last subarray
        profits = [0]

        curr_start = 0
        curr_profit = 0

        # remember to start from index 1, as we need to buy somewhere (and we buy at 0 initially)
        for i in range(1, n):
            curr_profit = prices[i] - prices[curr_start]

            # if we're increasing our profit at this step - all good, use that
            if curr_profit > profits[-1]:
                profits[-1] = curr_profit

            # if the profit would decrease - start a new interval of buy/sell, fixing the current profit
            else:
                # reuse the subarray profit if it contained no profit in the first place
                # this avoids zeroes in the output
                if profits[-1] > 0:
                    profits.append(0)
                curr_start = i

        # trim the last elt of profit, if it doesn't add anything
        if profits[-1] <= 0:
            profits = profits[:-1]

        return (sum(profits), profits)


if __name__ == "__main__":
    with verbose_group("_max_profit_all_kadane") as g:
        g.verbose_call(Solution()._max_profit_all_kadane, [7, 1, 5, 3, 6, 4], expected=(7, [4, 3]))
        g.verbose_call(
            Solution()._max_profit_all_kadane, [1, 7, 1, 5, 3, 6, 4], expected=(13, [6, 4, 3])
        )
        g.verbose_call(Solution()._max_profit_all_kadane, [1, 2, 3, 4, 5], expected=(4, [4]))
