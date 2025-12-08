# https://leetcode.com/problems/number-of-islands/

from collections import deque
import sys
from typing import List


sys.path.insert(0, "..")  # a hacky way, but whatever
from verbose_call import verbose_group


def print_grid(grid: List[List[str]]):
    print()
    for row in grid:
        for val in row:
            print(f" {val} ", end="")
        print()


class Solution:
    def numIslands(self, grid: List[List[str]]) -> int:
        return self._number_of_islands(grid)

    def _number_of_islands(self, grid: List[List[str]]) -> int:
        if not grid or not grid[0]:
            return 0

        grid_xn = len(grid[0])
        grid_yn = len(grid)

        kind_to_marked_kind = {
            "1": "x",
            "0": "_",
        }

        def mark(initial_position: tuple[int, int], kind: str, marked_kind: str):
            nonlocal grid

            queue = deque()
            queue.append(initial_position)

            # print_grid(grid)

            n_marked = 0
            adjacent_non_kind = set()  # adjacent nodes, that are not our kind

            while queue:
                point_x, point_y = queue.popleft()
                point_val = grid[point_y][point_x]

                if point_val in kind_to_marked_kind.values():  # visited terrain or water
                    continue

                if point_val == kind:  # terrain
                    grid[point_y][point_x] = marked_kind  # mark visited
                    n_marked += 1

                for x, y in [
                    (point_x + 1, point_y),
                    (point_x - 1, point_y),
                    (point_x, point_y - 1),
                    (point_x, point_y + 1),
                ]:
                    if (x < 0 or x >= grid_xn) or (y < 0 or y >= grid_yn):
                        continue

                    if grid[y][x] == kind:
                        queue.append((x, y))
                    elif grid[y][x] not in kind_to_marked_kind.values():
                        # print(f"adjacent_non_kind <-- ({x}, {y}) [{grid[y][x]}]")
                        adjacent_non_kind.add((x, y))

            return (n_marked, adjacent_non_kind)

        n_islands = 0
        unmarked_queue = set([(0, 0)])
        while unmarked_queue:
            # print(f"unmarked_queue = {unmarked_queue}")

            # queue for the next scan
            next_queue = set()
            while unmarked_queue:
                point = unmarked_queue.pop()
                # print(f"point = {point}")

                # ok, what kind of point we're marking now? (terrain/water or marked -//-)
                kind = grid[point[1]][point[0]]
                # ok, how do we mark it? if it's not here - we don't need to mark at all
                marked_kind = kind_to_marked_kind.get(kind)
                if marked_kind is None:
                    continue

                n_marked, nextq = mark(point, kind, marked_kind)
                next_queue = next_queue.union(nextq)

                # islands are terrain only
                # also filter on "has the marker actually marked anything"
                if n_marked > 0 and kind == "1":
                    n_islands += 1

            # print(f"loop_done, next_queue = {next_queue}")
            unmarked_queue = next_queue

        # print_grid(grid)

        return n_islands


if __name__ == "__main__":
    with verbose_group("_number_of_islands") as g:
        g.verbose_call(
            Solution()._number_of_islands,
            [
                ["1", "1", "1", "1", "0"],
                ["1", "1", "0", "1", "0"],
                ["1", "1", "0", "0", "0"],
                ["0", "0", "0", "0", "0"],
            ],
            expected=1,
        )
        g.verbose_call(
            Solution()._number_of_islands,
            [
                ["1", "1", "1", "1", "0"],
                ["1", "1", "0", "1", "0"],
                ["1", "1", "0", "0", "0"],
                ["0", "0", "0", "1", "0"],
            ],
            expected=2,
        )
        g.verbose_call(
            Solution()._number_of_islands,
            [["0", "1", "0"], ["1", "0", "1"], ["0", "1", "0"]],
            expected=4,
        )
