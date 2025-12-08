// https://leetcode.com/problems/string-to-integer-atoi/

#include <string>
#include <cstdio>

using std::string;

class Solution
{
public:
	int myAtoi(string s)
	{
		int result = 0;
		int sign = 1;

		char const *p = s.c_str();

		// skip whitespace
		while (*p && isspace(*p))
			++p;

		// determine sign, only one sign character is permitted
		switch (*p)
		{
		case '-':
			sign = -1;
			++p;
			break;
		case '+':
			++p;
			break;
		default: // some other character
			break;
		}

		// skip leading zeroes
		while (*p && (*p == '0'))
			++p;

		for (; '0' <= *p && *p <= '9'; ++p)
		{
			int const digit = (*p - '0');

			// Overflow check

			if (result > (INT_MAX / 10))
				return INT_MAX;

			if (result < (INT_MIN / 10))
				return INT_MIN;

			result *= 10;

			if ((INT_MAX - digit) < result)
				return INT_MAX;

			if ((INT_MIN + digit) > result)
				return INT_MIN;

			result += sign * digit;
		}

		return result;
	}
};

void run_test(string str, int expected)
{
	Solution s;
	int result = s.myAtoi(str);

	printf("[%s] string: '%s', expected: %d, result: %d\n",
		   (result == expected) ? "OK" : "ERROR", str.c_str(), expected, result);
}

int main()
{
	run_test("-+12", 0);
	run_test("42", 42);
	run_test(" -0042", -42);
	run_test("1073741823", 1073741823);
	run_test("1073741824", 1073741824);

	run_test("  +00004294967296", 2147483647); // clamped up
	run_test("  -4294967295", -2147483648);	   // clamped down
	run_test("  -2147483648", -2147483648);	   // should fit precicely
	run_test("   2147483648", 2147483647);	   // clamped up at the boundary
}
