from hmac import new
from typing import Optional


# Definition for singly-linked list.
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


class Solution:
    def reverseList(self, head: Optional[ListNode]) -> Optional[ListNode]:
        return self.reverseList_inplace(head)
        return self.reverseList_createnew(head)

    def reverseList_inplace(self, head: Optional[ListNode]) -> Optional[ListNode]:
        out = None

        while head:
            new_head = head.next
            head.next = out
            out = head
            head = new_head

        return out

    def reverseList_createnew(self, head: Optional[ListNode]) -> Optional[ListNode]:
        # if not head or not head.next:
        #     return head

        out = None

        while head:
            new_head = ListNode(val=head.val, next=out)
            out = new_head
            head = head.next

        return out


def array_to_linked_list(arr: list[int]):
    if len(arr) == 0:
        return None

    head = None
    tail = None
    for v in arr:
        new_node = ListNode(v)
        if not tail:
            tail = new_node
            head = tail
        else:
            tail.next = new_node
            tail = tail.next

    return head


def linked_list_to_array(head: Optional[ListNode]) -> list[int]:
    result = []
    while head:
        result.append(head.val)
        head = head.next
    return result


def run_test(input: list[int], expected: list[int]):
    input_list = array_to_linked_list(input)
    s = Solution()
    result = s.reverseList(input_list)
    print(f"input: {input}")
    print(f"expected: {expected}")
    print(f"result: {linked_list_to_array(result)}")
    print()


if __name__ == "__main__":
    run_test([0, 1, 2, 3], [3, 2, 1, 0])
    run_test([], [])
    # run_test([0, 1, 2, 3], [3, 2, 1, 0])
