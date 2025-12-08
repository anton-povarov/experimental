// https://leetcode.com/problems/rotate-image/description/
// matrix transposes + mirrors
// see end of file for an example

#include <vector>
#include <string>
#include <cstdio>
#include <sstream>

using std::vector;

using matrix_t = vector<vector<int>>;

void matrix_transpose_inplace(matrix_t &m)
{
	int const matrix_dim = m.size();

	for (int i = 0; i < matrix_dim; i++)
	{
		for (int j = i + 1; j < matrix_dim; j++)
		{
			std::swap(m[i][j], m[j][i]);
		}
	}
}

void matrix_mirror_horizontal(matrix_t &m)
{
	int const matrix_dim = m.size();

	for (int i = 0; i < matrix_dim; i++)
	{
		for (int j = 0; j < matrix_dim / 2; j++)
		{
			std::swap(m[i][j], m[i][matrix_dim - j - 1]);
		}
	}
}

std::string matrix_to_string(matrix_t const &m)
{
	std::stringstream ss;
	// ss << "[ ";
	for (auto const &row : m)
	{
		ss << "[";
		for (int i = 0; i < row.size(); i++)
		{
			if (i)
				ss << ", ";
			ss << row[i];
		}
		ss << "]\n";
	}
	// ss << "]";
	return ss.str();
}

class Solution
{
public:
	void rotate(vector<vector<int>> &matrix)
	{
		matrix_transpose_inplace(matrix);
		matrix_mirror_horizontal(matrix);
	}
};

void run_test(matrix_t const &matrix, matrix_t const &expected)
{
	matrix_t copy = matrix;
	Solution s;
	s.rotate(copy);

	printf("input\n%s\n", matrix_to_string(matrix).c_str());
	printf("output\n%s\n", matrix_to_string(copy).c_str());
	printf("expected\n%s\n", matrix_to_string(expected).c_str());
	printf("%s\n", (copy == expected) ? "OK" : "ERROR");
}

int main()
{
	run_test({{1, 2, 3}, {4, 5, 6}, {7, 8, 9}},
			 {{7, 4, 1}, {8, 5, 2}, {9, 6, 3}});
}

// source
// [1, 2, 3]
// [4, 5, 6]
// [7, 8, 9]

// transpose over the main diagonal
// [1, 4, 7]
// [2, 5, 8]
// [3, 6, 9]

// transpose over the other diagonal
// [9, 6, 3]
// [8, 5, 2]
// [7, 4, 1]

// (-90 deg -> right): transpose -> mirror horizontal (aka reverse row)
// [7, 4, 1]
// [8, 5, 2]
// [9, 6, 3]

// (+90 deg -> left): transpose -> mirror vertical (aka reverse column)
// [3, 6, 9]
// [2, 5, 8]
// [1, 4, 7]

// (-180 deg -> left): mirror vertical -> mirror horizontal
// [9, 8, 7]
// [6, 5, 4]
// [3, 2, 1]

// (+180 deg -> left): mirror horizontal -> mirror vertical
// [9, 8, 7]
// [6, 5, 4]
// [3, 2, 1]
