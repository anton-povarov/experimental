#include <cstdio>
#include <print>

class Solution
{
public:
	int getSum(int a, int b)
	{
		while (b != 0)
		{
			int const carry = a & b;
			a = a ^ b;
			b = carry << 1;
		}

		return a;
	}
};

void run_test(int a, int b, int expected)
{
	std::print("a = {:08b}, b = {:08b}, exp = {:08b}\n", a, b, expected);
	Solution s;
	int res = s.getSum(a, b);
	std::print("{1} res = {0:08b}\n", res, (res == expected) ? "OK" : "ERROR");
}

int main()
{
	run_test(8, 9, 17);
	run_test(-1, -2, -3);
	run_test(-1, 1, 0);
	run_test(-1, 0, -1);
}
