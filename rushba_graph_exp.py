from collections import defaultdict, deque
from dataclasses import dataclass
from typing import List, Tuple
import pprint


class Graph:
    inputs = defaultdict(set)
    outputs = defaultdict(list)
    nodes = set()

    def __init__(self, nodes: List[Tuple[int, int]]):
        for a, b in nodes:
            self.inputs[b].add(a)
            self.outputs[a].append(b)
            self.nodes |= {a, b}


# 300 \
#      1 -> 2 -> 3 \        / -> 10
# 200 /             \      /
# 25 ------------>   7 -> 8
# 5 -> 6 -----------/      \ -> 9 -> 100
graph_nodes = [
    (300, 1),
    (200, 1),
    (1, 2),
    (2, 3),
    (3, 7),
    (5, 6),
    (6, 7),
    (7, 8),
    (8, 10),
    (8, 9),
    (9, 100),
    (25, 7),
    (29, 8),
    (10, 101),
    (100, 101),
]

g = Graph(graph_nodes)


def execution_order_kahns_algorithm(g: Graph):
    # Compute in-degrees
    in_degree = {n: len(g.inputs[n]) for n in g.nodes}

    # result
    nodes_by_level = []  # each level can be run in parallel

    queue = [n for n in g.nodes if in_degree[n] == 0]

    while queue:
        this_level = queue.copy()
        nodes_by_level.append(this_level)
        queue.clear()

        for node in this_level:
            # all nodes this node links to
            # aka, all nodes that depend on this node
            output_nodes = g.outputs[node]
            for out_node in output_nodes:
                in_degree[out_node] -= 1
                if in_degree[out_node] == 0:
                    queue.append(out_node)

    return nodes_by_level


def collapse_single_item_chains(levels: List[List[int]]):
    i = 0
    out = 0

    while i < len(levels):
        # copy while we're looking for a single-item list
        while i < len(levels) and len(levels[i]) != 1:
            levels[out] = levels[i]
            out += 1
            i += 1

        # i found it, init output with whatever is in there
        levels[out] = levels[i]

        # merge into out, wile we're seeing single-item lists
        j = i + 1
        while j < len(levels) and len(levels[j]) == 1:
            levels[out] += levels[j]
            j += 1

        # finished merging
        out += 1

        # ok, we've found a longer list now with j
        # start searching for the next one with i
        i = j

    return levels[:out]


if __name__ == "__main__":
    levels = execution_order_kahns_algorithm(g)
    print(f"Execution stages: {pprint.pformat(list(enumerate(levels)))}")
    levels = collapse_single_item_chains(levels)
    # levels = collapse_single_item_chains([[1], [2], [5, 5], [5], [6], [7]])
    print(f"Execution stages collapsed:")
    for i, lvl in enumerate(levels):
        print(f" Level {i}: {lvl}")
