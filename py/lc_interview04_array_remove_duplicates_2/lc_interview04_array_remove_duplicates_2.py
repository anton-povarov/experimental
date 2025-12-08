from typing import List


class Solution:
    def removeDuplicates(self, nums: List[int]) -> int:
        nlen = len(nums)

        if nlen <= 1:
            return nlen

        i = 0
        out = 0
        while i < nlen:
            elt = nums[i]

            # just copy an element on first occurrence
            nums[out] = elt
            out += 1

            # advance: recheck if there are more elements
            i += 1
            if i >= nlen:
                break

            # advance: recheck if we're collapsing or this is a new number
            if elt != nums[i]:
                continue

            # can now proceed with collapsing the rest
            elt = nums[i]
            while i < nlen and nums[i] == elt:
                i += 1

            nums[out] = elt
            out += 1

        return out


def run_test(nums: List[int], expected: List[int]):
    s = Solution()
    nums_copy = nums.copy()
    nums_copy_len = s.removeDuplicates(nums_copy)
    print(
        f"input: {nums} --> len: {nums_copy_len}, nums: {nums_copy[:nums_copy_len]}, nums_raw: {nums_copy}"
    )

    lists_equal = nums_copy[:nums_copy_len] == expected
    print(f"{'OK' if lists_equal else 'ERROR'}")


if __name__ == "__main__":
    run_test([1, 1, 2], [1, 1, 2])
    run_test([1, 1, 1, 2, 2, 3], [1, 1, 2, 2, 3])
    run_test([0, 0, 1, 1, 1, 1, 2, 3, 3], [0, 0, 1, 1, 2, 3, 3])
