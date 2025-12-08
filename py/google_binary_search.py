# https://www.linkedin.com/pulse/my-simple-coding-interview-question-wil-wen/
# Given a positive sorted array
#
# a = [ 3, 4, 6, 9, 10, 12, 14, 15, 17, 19, 21 ];
#
# Define a function f(a, x) that returns x, the next smallest number, or -1 for errors.
#
# i.e.
# f(a, 12) = 12
# f(a, 13) = 12

from typing import List


def find_x_or_next_smallest__binsearch(a: List[int], x: int) -> int:
    if len(a) == 0:
        return -1

    begin = 0
    end = len(a)

    MAX_SIZE_FOR_LINEAR_SCAN = 4

    while (end - begin) > MAX_SIZE_FOR_LINEAR_SCAN:
        pivot = begin + (end - begin) // 2

        if a[pivot] <= x:  # x is in [pivot, end)
            begin = pivot
            continue
        else:  # x is in [begin, pivot)
            end = pivot

    # linear search when the array is sufficiently small
    for i in reversed(range(begin, end)):
        if a[i] <= x:
            return a[i]

    # if exact item was not found with liear search, return one to the left if there is anything
    return a[begin] - 1 if begin > 0 else -1


def run_test(a, x, expected):
    print(f"running {a}, {x}", end="")
    res = find_x_or_next_smallest__binsearch(a, x)
    print(f" -> {res}, expected {expected} {'OK' if res == expected else 'ERROR'}")


if __name__ == "__main__":
    a = [3, 4, 6, 9, 10, 12, 14, 15, 17, 19, 21]

    run_test(a, 12, 12)
    run_test(a, 13, 12)
    run_test(a, 2, -1)
    run_test(a, 300, 21)
    run_test(a, -1, -1)
    run_test(a, 3, 3)
    run_test(a, 5, 4)
    run_test([], 5, -1)
    run_test([1, 2, 3], 5, 3)
