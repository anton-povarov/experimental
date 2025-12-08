# https://leetcode.com/problems/find-k-pairs-with-smallest-sums/

from typing import List
import heapq


class Solution:
    def kSmallestPairs(self, nums1: List[int], nums2: List[int], k: int) -> List[List[int]]:
        result = []
        heap = [(nums1[0] + nums2[0], 0, 0)]
        visited = set()

        while k > 0 and heap:
            print(f"heap: {heap}")

            # grab the smallest sum and it's indexes
            # CRITICAL KEY POINT:
            #   we need the indexes from the min item -> then advance to next elts from them
            #   otherwise we're not going to visit all possible pairs
            #
            #   this approach might produce duplicates, so we need a visited set to avoid them
            #   should be a hashtable with O(1) amortized, but extra space around O(n1+n2)
            (min_sum, i, j) = heapq.heappop(heap)

            if i + 1 < len(nums1):
                if (i + 1, j) not in visited:
                    visited.add((i + 1, j))
                    heapq.heappush(heap, (nums1[i + 1] + nums2[j], i + 1, j))

            if j + 1 < len(nums2):
                if (i, j + 1) not in visited:
                    visited.add((i, j + 1))
                    heapq.heappush(heap, (nums1[i] + nums2[j + 1], i, j + 1))

            result.append([nums1[i], nums2[j]])
            k -= 1

        return result


def run_test(nums1: List[int], nums2: List[int], k: int, expected: List[List[int]]):
    print(f"nums1: {nums1}, nums2: {nums2}, k = {k}")
    print(f"expected: {expected}")

    s = Solution()
    res = s.kSmallestPairs(nums1, nums2, k)

    print(f"result: {res}")
    print(f"{'OK' if res == expected else 'ERROR'}")


if __name__ == "__main__":
    run_test(nums1=[1, 7, 11], nums2=[2, 4, 6], k=3, expected=[[1, 2], [1, 4], [1, 6]])
    run_test(nums1=[1, 1, 2], nums2=[1, 2, 3], k=2, expected=[[1, 1], [1, 1]])
