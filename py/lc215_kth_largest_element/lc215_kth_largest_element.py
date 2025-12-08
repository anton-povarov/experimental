# https://leetcode.com/problems/kth-largest-element-in-an-array/

from typing import List
import heapq


class Solution:
    def findKthLargest(self, nums: List[int], k: int) -> int:
        heap = []

        for i, v in enumerate(nums):
            if len(heap) < k:
                heapq.heappush(heap, v)
            elif heap[0] < v:
                heapq.heapreplace(heap, v)

        return heap[0]


def run_test(nums: List[int], k: int, expected: int):
    print(f"nums1: {nums}, k = {k}")
    print(f"expected: {expected}")

    s = Solution()
    res = s.findKthLargest(nums, k)

    print(f"result: {res}")
    print(f"{'OK' if res == expected else 'ERROR'}")


if __name__ == "__main__":
    run_test([3, 2, 1, 5, 6, 4], 2, 5)
    run_test([3, 2, 3, 1, 2, 4, 5, 5, 6], 4, 4)
