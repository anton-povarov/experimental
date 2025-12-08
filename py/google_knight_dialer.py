# https://medium.com/hackernoon/google-interview-questions-deconstructed-the-knights-dialer-f780d516f029
#
# [1, 2, 3, 4, 5, 6, 7, 8, 9]
# [0] is a bit special
# dial
#
# [1] [2] [3]
# [4] [5] [6]
# [7] [8] [9]
#     [0]

# you can math it out or you can code it
# 1. how to calculate where the knight can go from a position X?
#  - we can hand map it
#  - with can matrix mult it (i.e. move to matrix coords, see below)
# 2. observe
#  - from [5] - you can't go anywhere (so only the initial one is "pressed")
#  - bounds check - can't go there

# version 1
# matrix coords
#   from position (x, y) -> you can go to (x+1, y+2) and (x+2, y+1), IIF they exist in the matrix
#   from position (x, y) -> you can go to (x+1, y-2) and (x+2, y-1), IIF they exist in the matrix
#   from position (x, y) -> you can go to (x-1, y+2) and (x-2, y+1), IIF they exist in the matrix
#   from position (x, y) -> you can go to (x-1, y-2) and (x-2, y-1), IIF they exist in the matrix
# account for 0
#   make the table not [3,3], but [3, 4] and just put sentinel values there (like -1)

# version 2 - see below the impl
# you can just enumerate all possible jumps by hand, this eliminates the need for the grid
# NEIGHBORS_MAP = {
#     1: (6, 8),
#     2: (7, 9),
#     3: (4, 8),
#     4: (3, 9, 0),
#     5: tuple(),  # 5 has no neighbors
#     6: (1, 7, 0),
#     7: (2, 6),
#     8: (1, 3),
#     9: (2, 4),
#     0: (4, 6),
# }

from collections import deque


dial = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9],
    [-1, 0, -1],
]


def is_position_jumpable(d: list[list[int]], x: int, y: int):
    if x < 0 or y < 0:
        return False
    if x >= 3 or y >= 4:
        return False
    return d[y][x] != -1


def assign_at_position(d: list[list[int]], x: int, y: int, value: int):
    if is_position_jumpable(d, x, y):
        d[y][x] = value


def get_jumps_from_position(x: int, y: int):
    jumps = []
    for dx in (+1, +2):
        dy = 3 - dx
        jumps.append((x + dx, y + dy))
        jumps.append((x + dx, y - dy))
        jumps.append((x - dx, y + dy))
        jumps.append((x - dx, y - dy))

    jumps = [j for j in jumps if is_position_jumpable(dial, j[0], j[1])]

    return jumps


def get_number_by_position(x: int, y: int):
    if not is_position_jumpable(dial, x, y):
        return None
    return dial[y][x]


def get_position_by_number(num: int):
    for y, row in enumerate(dial):
        for x, val in enumerate(row):
            if val == num:
                return (x, y)
    return None


print(get_jumps_from_position(1, 1))
print(get_number_by_position(1, 1))
print(get_position_by_number(5))


def get_max_visits_from_number(num: int):
    pos = get_position_by_number(num)
    if pos is None:
        return None

    visited = [[0, 0, 0], [0, 0, 0], [0, 0, 0], [-1, 0, -1]]

    n_visited = 0

    queue = deque()
    queue.append(pos)

    while queue:
        pos = queue.popleft()
        if not is_position_jumpable(visited, pos[0], pos[1]):  # already visited or invalid
            continue

        print(f"visiting: {pos} = {dial[pos[1]][pos[0]]}")

        # this node
        assign_at_position(visited, pos[0], pos[1], -1)
        n_visited += 1

        # children
        jumps = get_jumps_from_position(*pos)
        # print(f"jumps = {jumps}")
        for j in jumps:
            queue.append(j)

    return n_visited


print(get_max_visits_from_number(5))  # 1, only self
print(get_max_visits_from_number(6))  # 9, everything, except 5!
print(get_max_visits_from_number(0))  # 9, everything, except 5!


#### version2
NEIGHBORS_MAP: dict[int, list[int]] = {
    1: [6, 8],
    2: [7, 9],
    3: [4, 8],
    4: [3, 9, 0],
    5: [],  # 5 has no neighbors
    6: [1, 7, 0],
    7: [2, 6],
    8: [1, 3],
    9: [2, 4],
    0: [4, 6],
}


def neighbors(num: int):
    return NEIGHBORS_MAP[num]


def get_max_visits_from_number_v2_recursive(starting_number: int):
    VISITED_MAP = [False] * len(NEIGHBORS_MAP)

    def recursive(current_number: int):
        if VISITED_MAP[current_number]:
            return 0

        # self
        n_visited = 1
        VISITED_MAP[current_number] = True

        # let neighbors calculate their visits recursively
        for neighbor in neighbors(current_number):
            if not VISITED_MAP[neighbor]:
                n_visited += recursive(neighbor)

        return n_visited

    return recursive(starting_number)


def get_max_visits_from_number_v2_iterative(starting_number: int):
    VISITED_MAP = [False] * len(NEIGHBORS_MAP)

    queue = deque()
    queue.append(starting_number)

    n_visited = 0

    while queue:
        current_number = queue.popleft()
        if VISITED_MAP[current_number]:
            continue

        n_visited += 1
        VISITED_MAP[current_number] = True

        for neighbor in neighbors(current_number):
            if VISITED_MAP[neighbor]:
                continue
            queue.append(neighbor)

    return n_visited


print()
print("v2")
print(get_max_visits_from_number_v2_recursive(0))  # 9
print(get_max_visits_from_number_v2_iterative(0))  # 9


# actually implement the number SEQUENCES of numbers with length up to N


def number_of_sequences(starting_number: int, max_hops: int):
    if max_hops == 0:
        return 1

    n_sequences: int = 0

    for neighbor in neighbors(starting_number):
        n_sequences += number_of_sequences(neighbor, max_hops - 1)

    return n_sequences


def number_of_sequences_with_cache(starting_number: int, max_hops: int):
    cache: dict[tuple[int, int], int] = {}

    def recursive(starting_number: int, max_hops: int):
        if max_hops == 0:
            return 1

        if (starting_number, max_hops) in cache:
            return cache[(starting_number, max_hops)]

        n_sequences: int = 0

        for neighbor in neighbors(starting_number):
            neighbor_hops = recursive(neighbor, max_hops - 1)
            n_sequences += neighbor_hops

        cache[(starting_number, max_hops)] = n_sequences
        return n_sequences

    return recursive(starting_number, max_hops)


# note that our calculation at max_hops = N, depend only on numbers from max_hops = N-1
# so at "level N", the value each number is [N] = [sum of the numbers from its neighbors] at "level N-1"
# so we have an induction step, transforming level N to level N+1
def number_of_sequences_bottom_up(starting_number: int, max_hops: int):
    base_case = [1] * 10  # all func values at 0 max_hops are 1 (i.e. count self only)
    current_max_hops = 0

    current_case = base_case
    while current_max_hops < max_hops:
        next_case = [0] * 10
        for i in range(10):
            for neighbor in neighbors(i):
                next_case[i] += current_case[neighbor]
        current_case = next_case
        current_max_hops += 1

    return current_case[starting_number]


print()
print("v3")

# 0-6, 0-4
print(number_of_sequences(0, 1))  # 2
# 0-6-0, 0-6-1, 0-6-7, 0-4-0, 0-4-3, 0-4-9
print(number_of_sequences(0, 2))  # 6
print(number_of_sequences(0, 3))  # 12
print(number_of_sequences(0, 4))  # 32
print(number_of_sequences(0, 10))  # 4608
print(number_of_sequences(0, 15))  # hangs, too much
# print(number_of_sequences(0, 50))  # hangs, too much

print()
print(number_of_sequences_with_cache(0, 1))
print(number_of_sequences_with_cache(0, 2))
print(number_of_sequences_with_cache(0, 3))
print(number_of_sequences_with_cache(0, 4))
print(number_of_sequences_with_cache(0, 10))
print(number_of_sequences_with_cache(0, 15))
print(number_of_sequences_with_cache(0, 20))
print(number_of_sequences_with_cache(0, 50))
print(number_of_sequences_with_cache(0, 100))
print(number_of_sequences_bottom_up(0, 4))
print(number_of_sequences_bottom_up(0, 10))
print(number_of_sequences_bottom_up(0, 100))
