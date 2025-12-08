class Solution:
    def _get_sum(self, a: int, b: int, bits: int = 32):
        MASK = (1 << bits) - 1  # 0xFFFFFFFF
        IS_NEGATIVE_MASK = 1 << (bits - 1)  # 80000000

        print(f"\ninputs\n {(a & MASK):>0{bits}b} <- a\n {(b & MASK):>0{bits}b} <- b")

        carry: int = 0

        while b:
            # print()
            carry = (a & b) & MASK
            # print(f"1: {a:>0{bits}b}, {b:>0{bits}b}, {carry:>0{bits}b}")
            a = (a ^ b) & MASK
            # print(f"2: {a:>0{bits}b}, {b:>0{bits}b}, {carry:>0{bits}b}")
            b = (carry << 1) & MASK

            if a < -100:
                break

        print(f"a: {(a & MASK):>0{bits}b}")
        print(f"nm: {(IS_NEGATIVE_MASK & MASK):>0{bits}b}")
        print(f"ms: {(MASK):>0{bits}b}")

        if a & IS_NEGATIVE_MASK:
            print("neg")
            a = a - (1 << bits)
            # a = ~a + 1  # negative two's complement to positive, i.e. abs value
            # a = -a  # remember to negate

        print(f" {(a & MASK):>0{bits}b} <- res")
        return a

    def getSum(self, a: int, b: int) -> int:
        return self._get_sum(a, b, 8)


def run_test(a: int, b: int, expected: int):
    s = Solution()
    sum = s.getSum(a, b)
    print(f"{'OK' if sum == expected else 'ERROR'} sum = {sum}")


if __name__ == "__main__":
    run_test(3, 5, 8)
    run_test(9, 8, 17)
    run_test(-5, -7, -12)
    run_test(-1, 1, 0)
    run_test(-1, 0, -1)
