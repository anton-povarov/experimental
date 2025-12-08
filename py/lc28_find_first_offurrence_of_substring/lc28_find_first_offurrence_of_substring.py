# https://leetcode.com/problems/find-the-index-of-the-first-occurrence-in-a-string/

# solved in online LC editor
# took me a surprisingly large amount of attempts
#  minor mistales everywhere! underestimating the code quirkiness


class Solution:
    # O(n * m)
    def strStr(self, haystack: str, needle: str) -> int:
        nlen = len(needle)
        hlen = len(haystack)

        for j in range(hlen - nlen + 1):
            i = 0
            while i < nlen:
                if needle[i] != haystack[j + i]:
                    break
                i += 1
            if i == nlen:
                return j

        return -1
