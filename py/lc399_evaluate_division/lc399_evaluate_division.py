# https://leetcode.com/problems/evaluate-division/
# ! the most important part is recognizing this as a graph problem
# just the grpah is presented in a matrix adjacency list form most likely

#
# let's look at the example
# equations = [["a","b"],["b","c"]], values = [2.0,3.0]
# questions = [["a","c"],["b","a"],["a","e"],["a","a"],["x","x"]]
# meaning:
# 1) a / b = 2.0
# 2) b / c = 3.0
# ! how do we calculate a/c ?
# step 1. a = 2.0/b
# step 2. b = 3.0/c
# step 3. a = 2.0 / (3.0 / c) = 2.0 * 1 / (3.0 / c) = 2.0 * c / 3.0
# step 4. a / c = (2.0 * c / 3.0) / c = 2.0 * 3.0 = 6.0 -- all variables disappear, this is valid for any such system.
# ! how do we turn this into a graph problem now?
#  we can represent this as multiplication over a graph path from a to c: a -> (weight 2) -> b -> (weight 3) -> c
# in case we need to calc c / a  -> we take a reverse path, multiplying, by reverse numbers 1/2 * 1/3 = 1/6
#  this can be represented by c -> (weight 1/3) -> b -> (weight 1/2) -> a
# ! we can represent this graph as a matrix (column - dividend, row - divisor)
# this matrix will be "division symmetrical" across the diagonal
#      a      b      c
# ----------------------
#  a |  1    1/2     ?
#  b | 2/1    1     1/3
#  c | ?     3/1     1
#
# to calculate we search for a path from a to c, and multiply over that path
# 1. take the edge a -> b = 2
# 2. take the edge b -> c = 3
# total = 6.0
#
# how do we know which edges exist from the matrix
# the self reference edge: row = col of `a`-s position, value is always 1 there
# outbound edges: all the numbers in column where `a` is (except the ? positions, can be represented by 0 probably)
# inbound edges: all the numbers in a row where `a` is (except the ? positions, can be represented by 0 probably)
#
# ! is the system self-consistent?
# yes, if all the paths from node_a to node_b, traversed in one direction (inbound/outbound) yield the same results
#
# expected outputs
# all ok           -> a float value of node_a / node_b (multiplied over the path as described)
# division by zero -> 0 (or -inf)
# no path          -> -1 (i.e. we're given a/b and c/d, and then asked for a/d)
# unknown nodes    -> -1 (i.e. a / x, when there is no x in equations)

from collections import defaultdict
from math import isinf
import sys
from typing import List

sys.path.insert(0, "..")  # a hacky way, but whatever
from verbose_call import verbose_group


def print_matrix(grid: List[List[float]]):
    print()
    for row in grid:
        for val in row:
            print(f" {val:.2f} ", end="")
        print()


class Solution:
    def calcEquation(
        self, equations: List[List[str]], values: List[float], queries: List[List[str]]
    ) -> List[float]:
        answers = self._calcEquation_antoxa(equations, values, queries)
        return [a if a is not None else -1 for a in answers]

    # this function supports negative numbers, so the return type is changed
    #  returns None if solution can't be found
    #  so -1 is a valid return now
    # NOTE: rounds resulting number to 5 digits after the decimal point
    def _calcEquation_antoxa(
        self, equations: List[List[str]], values: List[float], queries: List[List[str]]
    ) -> List[float | None]:

        # var_names is a translation from variable names into indexes
        var_names = dict[str, int]()  # name -> id
        for equation in equations:
            eq_v1, eq_v2 = equation
            if var_names.get(eq_v1) is None:
                var_names[eq_v1] = len(var_names)
            if var_names.get(eq_v2) is None:
                var_names[eq_v2] = len(var_names)

        # print()
        # print(var_names)

        def build_matrix():
            """
            build the matrix, its size == number of distinct variables
            elements that have no recorded connection contain -inf
            """
            matrix = [[float("-inf") for _ in range(len(var_names))] for _ in range(len(var_names))]
            for i in range(len(matrix)):
                matrix[i][i] = 1

            # print_matrix(matrix)

            for i, equation in enumerate(equations):
                v1, v2, value = *equation, values[i]
                # print(f"m[{var_names[v2]}][{var_names[v1]}] = {value} = m[{v2}][{v1}]")
                matrix[var_names[v2]][var_names[v1]] = value
                matrix[var_names[v1]][var_names[v2]] = 1.0 / value
            return matrix

        def matrix_dfs(
            from_id: int, target_id: int, path_mul: float, visited: list[bool]
        ) -> float | None:
            # print(f"dfs: {from_id}, {target_id}, {path_mul}")
            if from_id == target_id:
                return path_mul

            if visited[from_id]:
                return None

            visited[from_id] = True

            # outbound connections are in column with this id - and are not -inf (no link)
            # be careful to skip self link via loop indexes,
            # as there might be an equation, giving 1 in inputs, i.e. a/b = 1
            for i in range(0, len(matrix)):
                link_multiplier = matrix[i][from_id]
                if isinf(link_multiplier) or (i == from_id):
                    continue
                path_val = matrix_dfs(i, target_id, path_mul * link_multiplier, visited)
                if path_val is not None:
                    return path_val

            return None

        def find_solution(matrix: list[list[float]], v1: str, v2: str):
            id_1 = var_names.get(v1)
            id_2 = var_names.get(v2)
            if id_1 is None or id_2 is None:
                return None

            if id_1 == id_2:
                return 1.0

            # swap to always go on outbound connections from a smaller id
            # if swapped, we'll return 1/answer
            sign = 1
            if id_1 > id_2:
                sign = -1
                id_1, id_2 = id_2, id_1

            answer = matrix_dfs(id_1, id_2, 1, [False] * len(matrix))
            if answer is None:
                return None
            if sign < 0:
                answer = 1 / answer
            return round(answer, 5)

        matrix = build_matrix()
        # print_matrix(matrix)

        return [find_solution(matrix, q[0], q[1]) for q in queries]


if __name__ == "__main__":
    with verbose_group("calcEquation") as g:
        g.verbose_call(
            Solution().calcEquation,
            [["a", "b"], ["b", "c"]],
            [2.0, 3.0],
            [["a", "c"], ["b", "a"], ["a", "e"], ["a", "a"], ["x", "x"]],
            expected=[6.0, 1 / 2, -1, 1, -1],
        )
        g.verbose_call(
            Solution().calcEquation,
            [["a", "b"], ["b", "c"], ["bc", "cd"]],
            [1.5, 2.5, 5.0],
            [["a", "c"], ["c", "b"], ["bc", "cd"], ["cd", "bc"]],
            expected=[3.75000, 0.40000, 5.00000, 0.20000],
        )
        g.verbose_call(
            Solution().calcEquation,
            [["a", "b"]],
            [0.5],
            [["a", "b"], ["b", "a"], ["a", "c"], ["x", "y"]],
            expected=[0.50000, 2.00000, -1.00000, -1.00000],
        )
        g.verbose_call(
            Solution().calcEquation,
            [["x1", "x2"], ["x2", "x3"], ["x1", "x4"]],
            [3.0, 0.5, 3.4],
            [["x2", "x4"]],
            expected=[1.13333],
        )
        g.verbose_call(
            Solution().calcEquation,
            [["x1", "x2"], ["x2", "x3"], ["x1", "x4"], ["x2", "x5"]],
            [3.0, 0.5, 3.4, 5.6],
            [
                ["x2", "x4"],
                ["x1", "x5"],
                ["x1", "x3"],
                ["x5", "x5"],
                ["x5", "x1"],
                ["x3", "x4"],
                ["x4", "x3"],
                ["x6", "x6"],
                ["x0", "x0"],
            ],
            expected=[
                1.13333,
                16.80000,
                1.50000,
                1.00000,
                0.05952,
                2.26667,
                0.44118,
                -1.00000,
                -1.00000,
            ],
        )
    with verbose_group("_calcEquation_antoxa") as g:
        g.verbose_call(
            Solution()._calcEquation_antoxa,
            [["a", "b"], ["b", "c"]],
            [2.0, 3.0],
            [["a", "c"], ["b", "a"], ["a", "e"], ["a", "a"], ["x", "x"]],
            expected=[6.0, 1 / 2, None, 1, None],
        )
        g.verbose_call(
            Solution()._calcEquation_antoxa,
            [["a", "b"], ["b", "c"], ["bc", "cd"]],
            [1.5, 2.5, 5.0],
            [["a", "c"], ["c", "b"], ["bc", "cd"], ["cd", "bc"]],
            expected=[3.75000, 0.40000, 5.00000, 0.20000],
        )
        g.verbose_call(
            Solution()._calcEquation_antoxa,
            [["a", "b"]],
            [0.5],
            [["a", "b"], ["b", "a"], ["a", "c"], ["x", "y"]],
            expected=[0.50000, 2.00000, None, None],
        )
        g.verbose_call(
            Solution()._calcEquation_antoxa,
            [["x1", "x2"], ["x2", "x3"], ["x1", "x4"]],
            [3.0, 0.5, 3.4],
            [["x2", "x4"]],
            expected=[1.13333],
        )
        g.verbose_call(
            Solution()._calcEquation_antoxa,
            [["x1", "x2"], ["x2", "x3"], ["x1", "x4"]],
            [3.0, 0.5, -3.4],
            [["x2", "x4"]],
            expected=[-1.13333],
        )
        g.verbose_call(
            Solution()._calcEquation_antoxa,
            [["x1", "x2"], ["x2", "x3"], ["x1", "x4"], ["x2", "x5"]],
            [3.0, 0.5, 3.4, 5.6],
            [
                ["x2", "x4"],
                ["x1", "x5"],
                ["x1", "x3"],
                ["x5", "x5"],
                ["x5", "x1"],
                ["x3", "x4"],
                ["x4", "x3"],
                ["x6", "x6"],
                ["x0", "x0"],
            ],
            expected=[
                1.13333,
                16.80000,
                1.50000,
                1.00000,
                0.05952,
                2.26667,
                0.44118,
                None,
                None,
            ],
        )
