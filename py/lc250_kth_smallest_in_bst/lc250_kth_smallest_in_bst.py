# https://leetcode.com/problems/kth-smallest-element-in-a-bst/


from typing import Optional
import itertools


# Definition for a binary tree node.
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


class Solution:
    def kthSmallest(self, root: Optional[TreeNode], k: int) -> int:
        # just walk the tree left to right and return n-th element
        # do it in style with a generator
        def walk(root: TreeNode):
            # print(f"walk: root = {root.val}")

            if root.left:
                yield from walk(root.left)

            yield root

            # visit the right subtree
            if root.right:
                yield from walk(root.right)

        if not root:
            return -1

        # nodes = list(walk(root))
        # return nodes[k - 1].val
        for i, node in enumerate(walk(root)):
            if i + 1 == k:
                return node.val

        return -1


def build_tree(nodes: list[int]) -> TreeNode:
    def add_children(root: TreeNode, nodes: list[int], i: int):
        # if len(nodes[i * 2 :]) < 2:
        #     return

        if (i * 2 + 1) < len(nodes) and nodes[i * 2 + 1] >= 0:
            root.left = TreeNode(nodes[i * 2 + 1])
            add_children(root.left, nodes, i * 2 + 1)

        if (i * 2 + 2) < len(nodes) and nodes[i * 2 + 2] >= 0:
            root.right = TreeNode(nodes[i * 2 + 2])
            add_children(root.right, nodes, i * 2 + 2)

    if len(nodes) < 1:
        raise ValueError("bad tree definition")

    root = TreeNode(nodes[0])
    add_children(root, nodes, 0)

    return root


def print_bst(node, prefix="", is_left=True, level=0):
    l2center_prefix = "─ " if level == 0 else "└── "
    r2center_prefix = "─ " if level == 0 else "┌── "
    l2r_prefix = "│   " if level != 0 else "  "
    l2l_prefix = "  " if level == 0 else "    "
    r2r_prefix = "  " if level == 0 else "    "
    r2l_prefix = "  " if level == 0 else "│   "

    if node is not None:
        if node.left or node.right:
            # print(f"node = {node.val}, prefix = {prefix}")
            print_bst(
                node.right, prefix + (l2r_prefix if is_left else r2r_prefix), False, level + 1
            )
            print(prefix + (l2center_prefix if is_left else r2center_prefix) + str(node.val))
            print_bst(node.left, prefix + (l2l_prefix if is_left else r2l_prefix), True, level + 1)
        else:
            print(prefix + (l2center_prefix if is_left else r2center_prefix) + str(node.val))
    else:
        print(prefix + (l2center_prefix if is_left else r2center_prefix) + "<>")


def print_tree(root: TreeNode):
    def add_to_layer(root: TreeNode, layers: list[list[int | None]], index: int):
        if not root.left and not root.right:
            return

        if index not in layers:
            layers.append([])
        this_node_list = layers[index]
        this_node_list.append(root.left.val if root.left else None)
        this_node_list.append(root.right.val if root.right else None)

        if root.left:
            add_to_layer(root.left, layers, index + 1)

        if root.right:
            add_to_layer(root.right, layers, index + 1)

    # [index] -> [ [v1, v2], ... ]
    layers: list[list[int | None]] = [[root.val]]
    add_to_layer(root, layers, 1)

    for l in layers:
        print(l)


def run_test(nodes: list[int], k: int, expected: int):
    print()
    root = build_tree(nodes)
    print_bst(root)
    print_tree(root)
    s = Solution()
    res = s.kthSmallest(root, k)
    print(f"[{'OK' if res == expected else 'ERR'}] res: {res}, expected: {expected}")


if __name__ == "__main__":
    run_test([3, 1, 4, -1, 2, -1, 5, -1, -1, 50], 1, 1)
    # run_test([3, 1, 4, -1, 2], 1, 1)
    # run_test([5, 3, 6, 2, 4, -1, -1, 1], 3, 3)
