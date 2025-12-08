from typing import List


class Solution:
    def removeElement(self, nums: List[int], val: int) -> int:
        return self.removeElement_list(nums, val)
        return self.removeElement_loop(nums, val)

    # this is a list comprehension
    # HOWEVER - it does not change the list IN PLACE as required by the task
    def removeElement_list(self, nums: List[int], val: int) -> int:
        nums = [i for i in nums if i != val]
        return len(nums)

    # working hand rolled solution
    # should prob be more efficient in the absence of simd, cache prefetch, etc. (?)
    def removeElement_loop(self, nums: List[int], val: int) -> int:
        # position to swap _from_
        i: int = 0

        # past-the-position to swap _to_, helps distinguish empty vs single elt case
        last: int = len(nums)

        while True:
            # find past-the-position where we swap TO
            while last > i and nums[last - 1] == val:
                last -= 1

            # find where we swap FROM
            while i < last and nums[i] != val:
                i += 1

            # have we already converged?
            if i >= last:
                break

            nums[i], nums[last - 1] = nums[last - 1], nums[i]

        return i


def run_test(nums: List[int], val: int):
    print()
    s = Solution()
    list_copy = nums.copy()
    list_len = s.removeElement_list(list_copy, val)
    loop_copy = nums.copy()
    loop_len = s.removeElement_loop(loop_copy, val)
    print(f"nums: {nums}, len: {len(nums)} --> [list] len: {list_len}, nums: {list_copy}")
    print(f"nums: {nums}, len: {len(nums)} --> [loop] len: {loop_len}, nums: {loop_copy}")

    lists_equal = list_copy[:list_len].sort() == loop_copy[:loop_len].sort()
    print(f"{'OK' if list_len == loop_len and lists_equal else 'ERROR'}")


if __name__ == "__main__":
    run_test([2, 2, 2, 2], 2)
    run_test([3, 2, 2, 2, 2], 2)
    run_test([3, 2, 2, 3], 2)
    run_test([3, 2, 2, 3], 3)
    run_test([3, 2, 2, 5, 3], 3)
    run_test([0, 1, 2, 2, 3, 0, 4, 2], 2)
