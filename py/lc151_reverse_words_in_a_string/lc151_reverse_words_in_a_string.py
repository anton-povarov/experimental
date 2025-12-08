# https://leetcode.com/problems/reverse-words-in-a-string/

import sys
from typing import List


sys.path.insert(0, "..")  # a hacky way, but whatever
from verbose_call import verbose_group


class Solution:
    def reverseWords(self, s: str) -> str:
        return self._reverse_pythonic(s)

    def _reverse_hardcore(self, s: str) -> str:
        # iterate back to front, split off words, skip whitespace, add words to res
        # remember trailing whitespace as well

        result = ""

        ws = False  # are we in whitespace mode
        word_e = len(s)  # end of the latest word

        for i in reversed(range(len(s))):
            if s[i] == " ":  # entering whitespace skipping mode
                if ws:
                    word_e = i  # important if this is leading whitespace
                    continue

                ws = True
                if word_e - (i + 1) > 0:
                    if result:
                        result += " "
                    result += s[i + 1 : word_e]
                    word_e = i
            else:
                if ws:  # changing ws mode -> word mode
                    ws = False
                    word_e = i + 1

        if word_e > 0:
            if result:
                result += " "
            result += s[:word_e]

        return result

    # it's funny, but this solution run on LC beats 100% time and 98% memory :)
    # got lucky, probably!
    def _reverse_pythonic(self, s: str) -> str:
        return " ".join(reversed([w.strip() for w in s.split(" ") if w.strip()]))


if __name__ == "__main__":
    with verbose_group("_reverse_pythonic") as g:
        g.verbose_call(Solution()._reverse_pythonic, "mama myla ramu", expected="ramu myla mama")
        g.verbose_call(
            Solution()._reverse_pythonic, "  mama myla ramu  ", expected="ramu myla mama"
        )
        g.verbose_call(
            Solution()._reverse_pythonic, "   mama    myla ramu", expected="ramu myla mama"
        )

    with verbose_group("_reverse_hardcore") as g:
        g.verbose_call(Solution()._reverse_hardcore, "mama myla ramu", expected="ramu myla mama")
        g.verbose_call(Solution()._reverse_hardcore, "mama myla ramu  ", expected="ramu myla mama")
        g.verbose_call(Solution()._reverse_hardcore, "mama  myla ramu  ", expected="ramu myla mama")
        g.verbose_call(
            Solution()._reverse_hardcore, " mama   myla ramu  ", expected="ramu myla mama"
        )
        g.verbose_call(
            Solution()._reverse_hardcore, " a mama   myla ramu  ", expected="ramu myla mama a"
        )
        g.verbose_call(Solution()._reverse_hardcore, "  hello world  ", expected="world hello")
