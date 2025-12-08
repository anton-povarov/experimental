import sys
from typing import List


sys.path.insert(0, "..")  # a hacky way, but whatever
from verbose_call import verbose_group

# [-2, 0, -1]
# zero_cnt = [0, 0, 1, 1]
# prefix_noz [1, -2, 1, -1]
# prefix_min [(1,0), (-2,1), (-2, 2), (-1, 3)]
# prefix_max [(1,0), (1,1), (1, 2), (1, 3)]

# [-2, 0, -1] ->  0
#     [0, -1] ->  0
#        [-1] -> -1


class Solution:
    def maxProduct(self, nums: List[int]) -> int:
        return self._max_product_val(nums)

    def _max_product_val(self, nums: List[int]):
        return self._max_product_interval(nums)[0]

    def _max_product_interval(self, nums: List[int]):
        if not nums:
            return (0, [])

        min_product = nums[0]  # can't put 0 here, we're multiplying after all
        min_interval = (0, 1)

        max_product = nums[0]
        max_interval = (0, 1)

        best_product = max_product
        best_interval = max_interval

        def maybe_update_best(prod: int, iv: tuple[int, int]):
            nonlocal best_product, best_interval

            # print(f"best: {best_product} {best_interval} <- {prod} {iv}")

            if best_product is None or best_product < prod:
                best_product = prod
                best_interval = iv

            if best_product is None or best_product == prod:
                if best_interval is None or len(iv) < len(best_interval):
                    best_interval = iv

        # print()

        for i in range(1, len(nums)):
            val = nums[i]

            # print(f"i = {i}, val = {val}")
            # print(f"min: {min_product}, iv = {min_interval}")
            # print(f"max: {max_product}, iv = {max_interval}")

            # zero ends current intervals, maybe updates best
            if val == 0:
                # we should check the max_product up to this point
                # maybe_update_best(max_product, max_interval)

                # it makes no sense to extend the min_product
                # just throw it away

                # and now new interval is started
                # print("updating intervals on zero")
                max_product = 0
                min_product = 0
                max_interval = (i, i + 1)
                min_interval = (i, i + 1)

                # explicitly try the [0] subarray as best
                # when next extension happens, this will be shorter if zero is the max
                maybe_update_best(max_product, max_interval)
                continue

            # swap the tracking as negative mul will flip positive->negative and vice versa
            # note that we're not yet doing the multiplication yet, see below
            if val < 0:
                # print("swapping")
                min_product, max_product = max_product, min_product
                min_interval, max_interval = max_interval, min_interval

            #        |  max < 0  |   max > 0
            #       ---------------------------
            #  val>0 |  max < 0  |   max > 0   # keeps the sign of max
            #  val<0 |  max > 0  |   max < 0   # flips the sign of max
            #
            if max_product * val < val:  # this will reduce the maximum, need new interval
                # print(f"max resetting to new subarray: mp {max_product}, v: {val}")
                max_product = val
                max_interval = (i, i + 1)
            else:  # extend the interval
                # print(f"max extending: mp {max_product}, v: {val}")
                max_product *= val
                max_interval = (max_interval[0], max_interval[1] + 1)

            #        |  min < 0  |   min > 0
            #       ---------------------------
            #  val>0 |  min < 0  |   min > 0   # keeps the sign of min
            #  val<0 |  min > 0  |   min < 0   # flips the sign of min
            #
            if min_product * val > val:  # this will increase the minimum, need new interval
                # print(f"min creating new subarray: mp {min_product}, v: {val}")
                min_product = val
                min_interval = (i, i + 1)
            else:  # extend the interval
                # print(f"min extending: mp {max_product}, v: {val}")
                min_product *= val
                min_interval = (min_interval[0], min_interval[1] + 1)

            maybe_update_best(max_product, max_interval)

        return (best_product, nums[best_interval[0] : best_interval[1]])


def chatgpt_max_product_subarray(nums: List[int]):
    if not nums:
        return (int(0), nums)

    max_ending_here = nums[0]
    min_ending_here = nums[0]

    # start indices for the subarrays that form current max/min products
    max_start = 0
    min_start = 0

    # best found so far
    best_product = nums[0]
    best_start = 0
    best_end = 0

    print()

    for i in range(1, len(nums)):
        x = nums[i]

        print(f"min = {min_ending_here}, iv = {nums[min_start : i + 1]}")
        print(f"max = {max_ending_here}, iv = {nums[max_start : i + 1]}")

        # Because max/min may swap when multiplied by negative
        if x < 0:
            # swap both values and their start indices
            max_ending_here, min_ending_here = min_ending_here, max_ending_here
            max_start, min_start = min_start, max_start

        # Choose whether to start new subarray at i or extend
        if x > max_ending_here * x:
            print(f"x > max_ending_here * x; {x} > {max_ending_here * x}, new_iv={nums[i : i + 1]}")
            max_ending_here = x
            max_start = i
        else:
            max_ending_here *= x

        if x < min_ending_here * x:
            print(f"x < max_ending_here * x; {x} < {max_ending_here * x}, new_iv={nums[i : i + 1]}")
            min_ending_here = x
            min_start = i
        else:
            min_ending_here *= x

        # Update global best
        print(f"checking new best: {max_ending_here} > {best_product}")
        if max_ending_here > best_product:
            best_product = max_ending_here
            best_start = max_start
            best_end = i

    return (best_product, nums[best_start : best_end + 1])


if __name__ == "__main__":
    with verbose_group("_max_product_interval") as g:
        # g.verbose_call(
        #     Solution()._max_product_interval,
        #     [-1, 2, 3, 2, 4, -5],
        #     expected=(240, [-1, 2, 3, 2, 4, -5]),
        # )
        # g.verbose_call(
        #     Solution()._max_product_interval, [-1, 2, 3, 2, 4], expected=(48, [2, 3, 2, 4])
        # )
        # g.verbose_call(Solution()._max_product_interval, [2, 3, -2, 4], expected=(6, [2, 3]))
        # g.verbose_call(Solution()._max_product_interval, [2, 3], expected=(6, [2, 3]))
        # g.verbose_call(Solution()._max_product_interval, [2, 3, 2, 4], expected=(48, [2, 3, 2, 4]))
        g.verbose_call(Solution()._max_product_interval, [-2], expected=(-2, [-2]))
        g.verbose_call(Solution()._max_product_interval, [-2, 0, 1], expected=(1, [1]))
        g.verbose_call(Solution()._max_product_interval, [-2, 0, 1, 1], expected=(1, [1]))
        g.verbose_call(
            Solution()._max_product_interval, [-2, 0, 1, 1, 5], expected=(5, [1, 1, 5])
        )  # not ideal, [1,5] or even [5], prob need a backward pass for this ?
        g.verbose_call(Solution()._max_product_interval, [-2, 0, -1], expected=(0, [0]))
        g.verbose_call(Solution()._max_product_interval, [0, -1, -1], expected=(1, [-1, -1]))
        g.verbose_call(Solution()._max_product_interval, [-2, 0, -1, -20], expected=(20, [-1, -20]))

    with verbose_group("chatgpt_max_product_subarray") as g:
        g.verbose_call(chatgpt_max_product_subarray, [-2, 0, -1], expected=(0, [0]))
        # g.verbose_call(chatgpt_max_product_subarray, [-2, 0, 1], expected=(1, [1]))
        # g.verbose_call(chatgpt_max_product_subarray, [2, 0, -1], expected=(2, [2]))
        # g.verbose_call(chatgpt_max_product_subarray, [2, 3, -2, 4], expected=(6, [2, 3]))
        # g.verbose_call(
        #     chatgpt_max_product_subarray, [-1, 2, 3, 2, 4, -5], expected=(240, [-1, 2, 3, 2, 4, -5])
        # )
