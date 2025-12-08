# https://leetcode.com/problems/clone-graph/

from collections import deque
import sys
from typing import Callable, Optional


sys.path.insert(0, "..")  # a hacky way, but whatever
from verbose_call import verbose_group


# Definition for a Node.
class Node:
    def __init__(self, val: int = 0, neighbors: list["Node"] | None = None):
        self.val = val
        self.neighbors = neighbors if neighbors is not None else []


class Solution:
    def cloneGraph(self, node: Optional["Node"]) -> Optional["Node"]:
        return self._clone_graph_dfs(node)[0]
        # return self._clone_graph_bfs(node)[0]

    # the easier solution and should also work for directed graphs
    # the idea is to recursively clone nodes with their links and then attach the cloned ones to current node
    # if we're seing the already cloned node - we just return from "cache" (which also serves as the "visited" set)
    def _clone_graph_dfs(self, node: Optional["Node"]):
        if node is None:
            return (None, [])

        new_nodes = dict[Node, Node]()

        def recursive_dfs(old_node: Node):
            if old_node in new_nodes:
                return new_nodes[old_node]

            new_node = Node(old_node.val)
            new_nodes[old_node] = new_node

            for old_link in old_node.neighbors:
                new_link = recursive_dfs(old_link)
                new_node.neighbors.append(new_link)
            return new_node

        return (recursive_dfs(node), new_nodes)

    # BFS is harder than DFS because you need to add bidirectional links at each iteration
    #  and need to be careful around new node creation - not to re-create nodes with multiple incoming links
    #  especially if they come from multiple levels
    def _clone_graph_bfs(self, node: Optional["Node"]):
        if node is None:
            return (None, [])

        new_nodes = dict[Node, Node]()  # old -> new

        def clone_node(n: Node):
            return Node(n.val)

        queue = deque()
        queue.append((node, clone_node(node)))  # [old, new]

        while queue:
            old_node, new_node = queue.popleft()

            if old_node in new_nodes:
                continue

            if new_node is None:
                new_node = clone_node(old_node)

            new_nodes[old_node] = new_node

            for old_link in old_node.neighbors:
                new_link = new_nodes.get(old_link)
                if new_link is None:
                    queue.append((old_link, None))
                else:
                    new_node.neighbors.append(new_link)
                    new_link.neighbors.append(new_node)
                    queue.append((old_link, new_link))

        return (next(iter(new_nodes.values())), new_nodes.values())


class Graph:
    nodes: dict[int, Node]

    def __init__(self):
        self.nodes = dict[int, Node]()


def make_graph_from_neighbors(nodes: list[list[int]]):
    g = Graph()

    for src_node_id, links in enumerate(nodes):
        src_node_id += 1  # start from 1
        if src_node_id not in g.nodes:
            g.nodes[src_node_id] = Node(src_node_id)
        for link_node_id in links:
            if link_node_id not in g.nodes:
                g.nodes[link_node_id] = Node(link_node_id)
            g.nodes[src_node_id].neighbors.append(g.nodes[link_node_id])
            # don't create the reverse link, it's expected in the data
            # g.nodes[link_node_id].neighbors.append(g.nodes[src_node_id])

    return g


def print_graph(g: Graph):
    print("graph:")
    for n in g.nodes.values():
        print(f"  gn[{n.val}] -> {[link.val for link in n.neighbors]}")


def graph_to_neighbors(g: Graph):
    pass


def run_test(func: Callable, nodes: list[list[int]]):
    g = make_graph_from_neighbors(nodes)
    print_graph(g)
    print(f"g_nodes = {g.nodes}")

    def run_func():
        if not g.nodes.values():
            return []

        print()

        old_node = next(iter(g.nodes.values()))
        print(f"old_node: {old_node} {old_node.val}")

        new_node, new_node_list = func(old_node)  # [new_node, new_node_list]
        print(f"new_node: {new_node} {new_node.val}")
        print(f"new_nodes: {new_node_list}, {[n.val for n in new_node_list]}")

        res = []
        for n in sorted(new_node_list, key=lambda x: x.val):
            print(f"node links: {[(link.val, link) for link in n.neighbors]}")
            res.append([link.val for link in n.neighbors])
        return res

    return run_func


if __name__ == "__main__":
    with verbose_group("_clone_depth") as g:
        g.verbose_call(
            run_test(Solution()._clone_graph_dfs, [[2, 4], [1, 3], [2, 4], [1, 3]]),
            expected=[[2, 4], [1, 3], [2, 4], [1, 3]],
        )
    with verbose_group("_clone_breadth") as g:
        g.verbose_call(
            run_test(Solution()._clone_graph_bfs, [[2, 4], [1, 3], [2, 4], [1, 3]]),
            expected=[[2, 4], [1, 3], [2, 4], [1, 3]],
        )
        g.verbose_call(
            run_test(Solution()._clone_graph_bfs, [[]]),
            expected=[[]],
        )
        g.verbose_call(
            run_test(Solution()._clone_graph_bfs, []),
            expected=[],
        )
