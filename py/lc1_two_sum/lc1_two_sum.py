from collections import defaultdict
import sys
from typing import List


sys.path.insert(0, "..")  # a hacky way, but whatever
from verbose_call import verbose_group


class Solution:
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        # return self._twoSum_dict(nums, target)
        return self._twoSum_dict2(nums, target)

    def _twoSum_dict(self, nums: List[int], target: int) -> List[int]:
        # need a list as numbers can be duplicated, i.e. [4,4], target = 8
        d = defaultdict(list)
        for i, v in enumerate(nums):
            d[v].append(i)

        for i, v in enumerate(nums):
            lst = d[target - v]
            for idx in lst:
                if idx != i:
                    return [i, idx]

        return []

    def _twoSum_dict2(self, nums: List[int], target: int) -> List[int]:
        # the task allows to assume that there is exactly one solution always
        # so we can just store index of the first element
        # and then if they're duplicated, the loop will find the second one
        d = dict[int, int]()
        for i, v in enumerate(nums):
            d[v] = i

        for i, v in enumerate(nums):
            other_idx = d.get(target - v)
            if other_idx is None:
                continue

            if i != other_idx:
                return [i, other_idx]

        return []


if __name__ == "__main__":
    with verbose_group("two_sum_dict") as g:
        g.verbose_call(Solution()._twoSum_dict, [1, 2, 3, 4, 5], target=3, expected=[0, 1])
        g.verbose_call(Solution()._twoSum_dict, [4, 4, 4, 5], target=8, expected=[0, 1])
        g.verbose_call(Solution()._twoSum_dict, [4, 4, 4, 5], target=9, expected=[0, 3])

    with verbose_group("two_sum_dict_2") as g:
        g.verbose_call(Solution()._twoSum_dict2, [1, 2, 3, 4, 5], target=3, expected=[0, 1])
        g.verbose_call(
            Solution()._twoSum_dict2, [4, 4, 4, 5], target=8, expected=[0, 2]
        )  # dict catches the last elt
        g.verbose_call(Solution()._twoSum_dict2, [4, 4, 4, 5], target=9, expected=[0, 3])
