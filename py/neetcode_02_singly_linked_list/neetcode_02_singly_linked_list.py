from dataclasses import dataclass
from typing import Any, Optional, List


@dataclass
class ListNode:
    val: Any
    next: Optional["ListNode"] = None


class LinkedList:
    head: Optional[ListNode] = None

    def __init__(self):
        self.head = None  # kinda redundant to assign here as well as in declaration above

    def get(self, index: int) -> int:
        node = self.head
        while node:
            if index == 0:
                return node.val

            index -= 1
            node = node.next

        return -1

    def insertHead(self, val: int) -> None:
        node = ListNode(val)
        node.next = self.head
        self.head = node

    def insertTail(self, val: int) -> None:
        new_node = ListNode(val)

        if not self.head:
            self.head = new_node
            return

        node = self.head
        while node.next:
            node = node.next

        node.next = new_node

    def remove(self, index: int) -> bool:
        if index == 0:
            if self.head:
                self.head = self.head.next
                return True
            return False

        node = self.head
        while node:
            if index == 1:  # next node is the one to remove
                ret = node.next is not None
                if node.next:
                    node.next = node.next.next
                return ret
            else:
                index -= 1
                node = node.next
                continue

        return False

    def getValues(self) -> List[int]:
        result = []
        node = self.head
        while node:
            result.append(node.val)
            node = node.next
        return result


def remove_and_print(l: LinkedList, index: int):
    print(f"removing index {index} from {l.getValues()}")
    r = l.remove(index)
    print(f"r: {r}, list: {l.getValues()}")


def test_1():
    l = LinkedList()
    l.insertHead(1)
    l.insertHead(2)
    print(f"{l.get(0)}")
    print(f"{l.get(1)}")
    remove_and_print(l, 2)
    print(f"{l.getValues()}")


def test_2():
    print()
    lst = LinkedList()
    lst.insertTail(1)
    lst.insertTail(2)
    lst.insertHead(3)
    print(f"{lst.getValues()}")
    remove_and_print(lst, 0)


if __name__ == "__main__":
    test_1()
    test_2()
