# https://leetcode.com/problems/rotate-list

import sys
from typing import Optional

sys.path.insert(0, "..")  # a hacky way, but whatever
from verbose_call import verbose_group


# Definition for singly-linked list.
class ListNode:
    val: int
    next: Optional["ListNode"]

    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


class Solution:
    def rotateRight(self, head: Optional[ListNode], k: int) -> Optional[ListNode]:
        return self._linear(head, k)
        # return self._recursive(head, k)

    def _linear(self, head: Optional[ListNode], k: int) -> Optional[ListNode]:
        if not head or not head.next:
            return head

        # calculate list length and last element
        list_len = 1  # count head
        last = head
        while last.next:
            list_len += 1
            last = last.next

        # the idea here is to rotate the other way (!)
        #  knowing head and last
        #  move elements one by one from current head to after last
        # here's the idea comparison:
        #  not "find last and make it new head" -> need to find a new last
        #  but "move head to after last" -> we still know head.next (!)
        # consequences:
        #  1. number of rotations becomes (len-k)
        #  2. each rotation goes forward
        # for example:
        #   from [1,2,3,4,5]
        #         H       L
        #   to   [2,3,4,5,1]
        #         H       L

        # make sure we don't over-rotate
        # i.e. if k = 10000, we just take a remainder over list_len
        n_rotations = list_len - k % list_len

        # now the optimized idea is
        # 1. make a cycle in the list temporarily
        # 2. this would allow us to
        #  - move head/last pointers as many times as needed
        #    (this can happen forever if we need to, circular list :-])
        #  - head and last end up in correct positions
        # 3. break the cycle at the last elt, we don't need it anymore

        last.next = head  # make a cycle last -> head
        for _ in range(n_rotations):
            head = head.next  # advance head
            last = last.next  # advance last
        last.next = None  # break the cycle at last elt

        return head

    def _recursive(self, head: Optional[ListNode], k: int) -> Optional[ListNode]:
        # idea: after exiting recursion we know:
        #  1. global head
        #  2. self (and self.next)
        #  3. do we need to rotate
        # rotation needed? -> move self.next to be the new global head
        #
        # input: global head, my node, k
        # output: new global head, k remaining
        def recursive(head, me, k):
            if not me.next:
                return [head, k]

            head, new_k = recursive(head, me.next, k)
            if new_k > 0:
                new_head = me.next
                new_head.next = head
                me.next = None
                return [new_head, new_k - 1]
            return [head, new_k]

        def get_len_and_last(head, list_len=1):
            while head.next:
                list_len += 1
                head = head.next
            return (list_len, head)

        if not head or not head.next:
            return head

        list_len, last = get_len_and_last(head)
        return recursive(head, head, k)[0]


if __name__ == "__main__":
    # todo: this will not run, as i was lazy to write code, transforming an array to linked list
    with verbose_group("_linear") as g:
        g.verbose_call(Solution()._linear, [1, 2, 3, 4, 5], expected=[4, 5, 1, 2, 3])

    with verbose_group("_recursive") as g:
        g.verbose_call(Solution()._recursive, [1, 2, 3, 4, 5], expected=[4, 5, 1, 2, 3])
