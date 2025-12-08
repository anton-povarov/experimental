# https://leetcode.com/problems/binary-search-tree-iterator/

# solved in online LC editor

import sys
from typing import List, Optional

sys.path.insert(0, "..")  # a hacky way, but whatever
from verbose_call import verbose_group


# Definition for a binary tree node.
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


class BSTIterator:
    parents: list[TreeNode]

    def __init__(self, root: Optional[TreeNode]):
        self.parents = []

        if not root:
            return

        while root:
            self.parents.append(root)
            root = root.left

    def next(self) -> int:
        if not self.parents:
            return -1

        curr = self.parents.pop()

        if curr.right:
            root = curr.right
            while root:
                self.parents.append(root)
                root = root.left

        return curr.val

    def hasNext(self) -> bool:
        return len(self.parents) > 0


# Your BSTIterator object will be instantiated and called as such:
# obj = BSTIterator(root)
# param_1 = obj.next()
# param_2 = obj.hasNext()


def run_test():
    pass


if __name__ == "__main__":
    with verbose_group("bst_iterator") as g:
        g.verbose_call(
            run_test,
            [["a", "b"], ["b", "c"]],
            [2.0, 3.0],
            [["a", "c"], ["b", "a"], ["a", "e"], ["a", "a"], ["x", "x"]],
            expected=[6.0, 1 / 2, -1, 1, -1],
        )
