# https://leetcode.com/problems/jump-game-ii/
# the idea is traverse depth(?) first and cache the number of jumps for each position


import heapq
import sys
from typing import List


sys.path.insert(0, "..")  # a hacky way, but whatever
from verbose_call import verbose_group


class Solution:
    def jump(self, nums: List[int]) -> int:
        # return self._jumps_recursive(nums)
        # return self._jumps_dijkstra(nums)
        return self._jumps_bfs_on_ranges(nums)

    def _jumps_recursive_with_memoization(self, nums: List[int]) -> int:
        if not nums:
            return -1

        # needed for a huge and very link-dense arrays that LC tests with
        sys.setrecursionlimit(10000)

        n = len(nums)
        target = n - 1

        cache = [-1] * len(nums)

        # print()

        def recursive(nums: List[int], position: int):
            nonlocal n, target

            # print(f"cache = {cache}, position = {position} (num: {nums[position]})")

            if position == target:
                return 0

            if cache[position] < 0:
                cache[position] = 0  # we're touching it, don't jump there

                if nums[position] != 0:  # we can't jump from 0, so it stays 0 forever
                    min_jumps = None

                    for i in range(-nums[position], nums[position] + 1):
                        jump_to = position + i
                        if (jump_to > 0 and jump_to < n) and cache[jump_to] != 0:
                            jumps_from_here = recursive(nums, jump_to)
                            if jumps_from_here < 0:
                                continue
                            if min_jumps is None or jumps_from_here < min_jumps:
                                min_jumps = jumps_from_here

                    if min_jumps is not None:
                        min_jumps += 1  # count self
                        # print(f"cache[{position}] <- {min_jumps}")
                        # print(f"before return [pos: {position}] = {cache}")
                        cache[position] = min_jumps
                    else:
                        cache[position] = -1  # reset back, can enter here again
                        return -1  # come in later
                else:
                    # keep cache[position] == 0
                    return -1  # simulate unreachability from nums[i] == 0, won't come in as cache[] will prevent

            return cache[position]

        min_jumps = recursive(nums, 0)
        # print(f"before return = {cache}")
        return min_jumps

    # these nums are like a graph, so we can use breadth first + heap, a-la dijkstra
    # but we need to prepare the graph first
    # maybe not, but it's easier to reason if we do
    #
    # this is quite slow for dense graphs - O(N^2 * log n)
    #   and LC provides very dense ones in tests for this
    # immediately obvious - they expect a different (prolly dynamic programming) solution :)
    def _jumps_dijkstra(self, nums: List[int]) -> int:
        if not nums:
            return -1

        distances = [-1 for i, _ in enumerate(nums)]  # id -> distance to node
        out_links = [[] for i in nums]  # id -> list of outbound links

        for node_index, distance in enumerate(nums):
            # do not link to self
            out_links[node_index].extend(list(range(max(0, node_index - distance), node_index)))
            out_links[node_index].extend(
                list(range(node_index + 1, min(node_index + distance + 1, len(nums))))
            )

        search_from_id = 0
        heap = [(0, search_from_id)]  # distance, node_id

        while heap:
            distance, node_id = heapq.heappop(heap)

            if distances[node_id] >= 0:  # already calculated
                continue

            distances[node_id] = distance

            for child_node_id in out_links[node_id]:
                if distances[child_node_id] > 0:
                    continue
                heapq.heappush(heap, (distance + 1, child_node_id))

        # print()
        # print(f"out_links = {out_links}")
        # print(f"distances = {distances}")
        return distances[-1]

    # this algorithm is discussed in
    # https://leetcode.com/problems/jump-game-ii/solutions/1192401/easy-solutions-w-explanation-optimizatio-c678/
    # further discussed with ChatGPT to understand it better
    # CharGPT calls it
    #  A greedy level-by-level range expansion algorithm that mimics the layer expansion of BFS, but without using a queue.
    #
    # Here is the key insight that makes the O(n) greedy algorithm work
    #  You don’t need to explore all edges or all paths.
    #  You only need to maintain:
    #      •	current_end (end of the current BFS level)
    #      •	farthest (farthest we can reach from anywhere in this level)
    # That’s it.
    # antoxa: I've rewritten it more explicitly and commented
    def _jumps_bfs_on_ranges(self, nums: List[int]) -> int:
        if not nums:
            return -1

        # cpp version
        # int jump(vector<int>& nums) {
        # 	int n = size(nums), i = 0, maxReachable = 0, lastJumpedPos = 0, jumps = 0;
        #
        #   # loop till last jump hasn't taken us till the end
        # 	while(lastJumpedPos < n - 1)
        #   {
        #       # furthest index reachable on the next level from current level
        # 		maxReachable = max(maxReachable, i + nums[i]);
        #
        #       # current level has been iterated & maxReachable position on next level has been finalised
        # 		if(i == lastJumpedPos) {
        # 			lastJumpedPos = maxReachable;     // so just move to that maxReachable position
        # 			jumps++;                          // and increment the level
        #
        # 	# NOTE: jump^ only gets updated after we iterate all possible jumps from previous level
        # 	#        This ensures jumps will only store minimum jump required to reach lastJumpedPos
        # 		}
        # 		i++;
        # 	}
        # 	return jumps;
        # }

        jumps = 0  # how many layers have we scanned fully

        # the interval we're currently scanning
        begin_i = 0
        end_i = 1

        print()

        # scaning a BFS reachability level, we need to find
        # the furthest reachable index
        while begin_i < end_i:
            # print(f"scanning BFS layer [{begin_i}, {end_i}) = {nums[begin_i:end_i]}")

            # the upper bound for the next layer of the scan
            # i.e. the max index we can reach from the current layer
            furthest_reachable_i = end_i
            for i in range(begin_i, end_i):
                furthest_reachable_i = max(furthest_reachable_i, i + nums[i] + 1)

            # layer scan done, we can update for the next one
            begin_i = end_i
            end_i = min(furthest_reachable_i, len(nums))

            # print(f"++jumps = {jumps + 1}")
            jumps += 1

        # how many layers have we scanned fully
        # subtract 1 as we count the very first layer of one element (the starting elt) as 1 layer
        return jumps - 1


if __name__ == "__main__":
    with verbose_group("_jumps_recursive_with_memoization") as g:
        g.verbose_call(Solution()._jumps_recursive_with_memoization, [1, 1], expected=1)
        g.verbose_call(Solution()._jumps_recursive_with_memoization, [2, 3, 1, 1, 4], expected=2)
        g.verbose_call(Solution()._jumps_recursive_with_memoization, [2, 3, 0, 1, 4], expected=2)
        g.verbose_call(
            Solution()._jumps_recursive_with_memoization, [2, 4, 0, 1, 1, 1, 6], expected=3
        )
        g.verbose_call(
            Solution()._jumps_recursive_with_memoization, [2, 5, 0, 1, 1, 1, 6], expected=2
        )
        g.verbose_call(
            Solution()._jumps_recursive_with_memoization,
            [9, 8, 2, 2, 0, 2, 2, 0, 4, 1, 5, 7, 9, 6, 6, 0, 6, 5, 0, 5],
            expected=3,  # 0(v:8) -> 8(v:4) -> 12(v:9) -> 19(v:5) == end
        )

    with verbose_group("_jumps_dijkstra") as g:
        g.verbose_call(Solution()._jumps_dijkstra, [1, 1], expected=1)
        g.verbose_call(Solution()._jumps_dijkstra, [2, 3, 1, 1, 4], expected=2)
        g.verbose_call(Solution()._jumps_dijkstra, [2, 3, 0, 1, 4], expected=2)
        g.verbose_call(Solution()._jumps_dijkstra, [2, 4, 0, 1, 1, 1, 6], expected=3)
        g.verbose_call(Solution()._jumps_dijkstra, [2, 5, 0, 1, 1, 1, 6], expected=2)
        g.verbose_call(
            Solution()._jumps_dijkstra,
            [9, 8, 2, 2, 0, 2, 2, 0, 4, 1, 5, 7, 9, 6, 6, 0, 6, 5, 0, 5],
            expected=3,  # 0(v:8) -> 8(v:4) -> 12(v:9) -> 19(v:5) == end
        )

    with verbose_group("_jumps_bfs_on_ranges") as g:
        g.verbose_call(Solution()._jumps_bfs_on_ranges, [1, 1], expected=1)
        g.verbose_call(Solution()._jumps_bfs_on_ranges, [2, 3, 1, 1, 4], expected=2)
        g.verbose_call(Solution()._jumps_bfs_on_ranges, [2, 3, 0, 1, 4], expected=2)
        g.verbose_call(Solution()._jumps_bfs_on_ranges, [2, 4, 0, 1, 1, 1, 6], expected=3)
        g.verbose_call(Solution()._jumps_bfs_on_ranges, [2, 5, 0, 1, 1, 1, 6], expected=2)
        g.verbose_call(
            Solution()._jumps_bfs_on_ranges,
            [9, 8, 2, 2, 0, 2, 2, 0, 4, 1, 5, 7, 9, 6, 6, 0, 6, 5, 0, 5],
            expected=3,  # 0(v:8) -> 8(v:4) -> 12(v:9) -> 19(v:5) == end
        )
