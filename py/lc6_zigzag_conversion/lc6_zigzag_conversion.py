# https://leetcode.com/problems/zigzag-conversion/
# The string "PAYPALISHIRING" is written in a zigzag pattern on a given number of rows like this:
# (you may want to display this pattern in a fixed font for better legibility)
# numRows = 3
# P   A   H   N
# A P L S I I G
# Y   I   R
# numRows = 4
# P     I     N
# A   L S   I G
# Y A   H R
# P     I
# ! And then read line by line: "PAHNAPLSIIGYIR"
# i.e. they side step the spaces thing, just join by virtual lines
#
#
# Conversion visualised [NR=1]
# |   |   |   |

# Conversion visualised [NR=2]
# |   |   |   |
# | / | / | / |

# Conversion visualised [NR=3]
# |   |   |   |
# | / | / | / |
# |   |   |   |

# Conversion visualised [NR=4]
# |     |     |     |
# |   / |   / |   / |
# | /   | /   | /   |
# |     |     |     |

# Conversion visualised [NR=5]
# |       |       |       |
# |     / |     / |     / |
# |   /   |   /   |   /   |
# | /     | /     | /     |
# |       |       |       |

#
# thought process
#  1. go k chars "down"
#  2. go k-2 chars "zag upwards"
#    -1 - do not include the bottom row again
#    -1 - do not include the top row, that's a new loop
#
# numRows = 1 -> loop_len = 0 (clamp this to 1)
# v = 0 | 0 | 0 | 0
# numRows = 2 -> loop_len = 2
# v = 0 1 | 0 1 | 0 1 | 0 1
# numRows = 3 -> loop_len = 4
# v = 0 1 2 1 | 0 1 2 1 | 0 1 2 1 | 0 1 2 1
# numRows = 4 -> loop_len = 6
# v = 0 1 2 3 2 1 | 0 1 2 3 2 1 | 0 1 2 3 2 1
# numRows = 5 -> loop_len = 8
# v = 0 1 2 3 4 3 2 1 | 0 1 2 3 2 1 | 0 1 2 3 2 1
#
# the mapping index -> row offset is oscilating
# num_rows = 4
# loop_len = L*2-2 = 6
# off: 0  1  2  3  4  5
# val: 0, 1, 2, 3, 2, 1
#
# val = off            (for off <  num_rows)
# val = loop_len - off (for off >= num_rows)


import sys


sys.path.insert(0, "..")  # a hacky way, but whatever
from verbose_call import verbose_group


class Solution:
    def convert(self, s: str, numRows: int) -> str:
        return self._convert_levels_loop(s, numRows)

    def _convert_levels_loop(self, s: str, numRows: int) -> str:
        levels = [""] * len(s)
        loop_len = max(2 * numRows - 2, 1)
        for i, sym in enumerate(s):
            off = i % loop_len
            to_lvl = off if off < numRows else loop_len - off
            levels[to_lvl] += sym
        return "".join(levels)

    def _convert_levels_nomath(self, s: str, numRows: int) -> str:
        # remove boundary conditions early, code below can't work with numRows == 1
        # generally numRows 1 and 2 are weird
        # 1 - it's just the same string
        # 2 - there is no space to place the diagonal "between" the 0th and 1st row
        # at least for 2 rows - there is space to step at least (i.e. row is never simulatenously == 0 and >= numRows-1)
        if numRows == 1 or numRows >= len(s):
            return s

        levels = ["" for _ in range(numRows)]
        row = 0
        direction = 1  # 1 down, -1 up
        for c in s:
            levels[row] += c

            if direction == 1:
                if (row + 1) >= numRows:
                    direction = -1
            else:
                if row == 0:
                    direction = 1

            row += direction

        return "".join(levels)


if __name__ == "__main__":
    with verbose_group("_convert_levels_loop") as g:
        g.verbose_call(
            Solution()._convert_levels_loop,
            "PAYPALISHIRING",
            numRows=1,
            expected="PAYPALISHIRING",
        )
        g.verbose_call(
            Solution()._convert_levels_loop,
            "PAYPALISHIRING",
            numRows=3,
            expected="PAHNAPLSIIGYIR",
        )
        g.verbose_call(
            Solution()._convert_levels_loop,
            "PAYPALISHIRING",
            numRows=4,
            expected="PINALSIGYAHRPI",
        )

    with verbose_group("_convert_levels_nomath") as g:
        g.verbose_call(
            Solution()._convert_levels_nomath,
            "PAYPALISHIRING",
            numRows=1,
            expected="PAYPALISHIRING",
        )
        # PAYPALISHIRING
        # P Y A I H R N
        # A P L S I I G
        g.verbose_call(
            Solution()._convert_levels_nomath,
            "PAYPALISHIRING",
            numRows=2,
            expected="PYAIHRNAPLSIIG",
        )
        g.verbose_call(
            Solution()._convert_levels_nomath,
            "PAYPALISHIRING",
            numRows=3,
            expected="PAHNAPLSIIGYIR",
        )
        g.verbose_call(
            Solution()._convert_levels_nomath,
            "PAYPALISHIRING",
            numRows=4,
            expected="PINALSIGYAHRPI",
        )
