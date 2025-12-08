class DynamicArray:
    cap: int
    size: int
    data: list[int]  # O(1) access by index

    def __init__(self, capacity: int):
        if capacity <= 0:
            raise ValueError("bad capacity, must be > 0")

        self.cap = capacity
        self.size = 0
        self.data = [0] * capacity

    def get(self, i: int) -> int:
        if i < 0 or i >= self.size:
            raise ValueError("get: index out of bounds")

        return self.data[i]

    def set(self, i: int, n: int) -> None:
        if i < 0 or i >= self.size:
            raise ValueError("set: index out of bounds")

        self.data[i] = n

    def pushback(self, n: int) -> None:
        if self.size >= self.cap:
            self.resize()

        self.data[self.size] = n
        self.size += 1

    def popback(self) -> int:
        if self.size == 0:
            raise ValueError("popback: array is already empty")

        val = self.data[self.size - 1]
        self.size -= 1

        # reduce capacity if size is 2x smaller than cap
        if self.size < self.cap // 2:
            self.data = self.data[0 : self.cap // 2]

        return val

    def resize(self) -> None:
        # no explicit resize in list, simulate by adding zeroes
        # we control what's visible with `size` anyway
        self.data += [0] * self.cap
        self.cap *= 2

    def getSize(self) -> int:
        return self.size

    def getCapacity(self) -> int:
        return self.cap


def test_1():
    arr = DynamicArray(1)
    print(f"size: {arr.getSize()}, cap: {arr.getCapacity()}")


def test_2():
    print()
    arr = DynamicArray(1)
    print(f"size: {arr.getSize()}, cap: {arr.getCapacity()}")
    arr.pushback(1)
    print(f"size: {arr.getSize()}, cap: {arr.getCapacity()}")


def test_3():
    print()
    arr = DynamicArray(1)
    print(f"size: {arr.getSize()}, cap: {arr.getCapacity()}")
    arr.pushback(1)
    print(f"size: {arr.getSize()}, cap: {arr.getCapacity()}")
    arr.pushback(2)
    print(f"size: {arr.getSize()}, cap: {arr.getCapacity()}")

    v = arr.get(1)
    print(f"val: {v}")

    arr.set(1, 3)

    v = arr.get(1)
    print(f"val: {v}")

    arr.popback()
    print(f"size: {arr.getSize()}, cap: {arr.getCapacity()}")


def test_4():
    print()
    arr = DynamicArray(3)
    print(f"size: {arr.getSize()}, cap: {arr.getCapacity()}")
    arr.pushback(1)
    print(f"size: {arr.getSize()}, cap: {arr.getCapacity()}")
    arr.pushback(2)
    print(f"size: {arr.getSize()}, cap: {arr.getCapacity()}")
    arr.pushback(3)
    print(f"size: {arr.getSize()}, cap: {arr.getCapacity()}")
    print(f"{arr.get(0)}, {arr.get(1)}, {arr.get(2)}")


if __name__ == "__main__":
    test_1()
    test_2()
    test_3()
    test_4()
