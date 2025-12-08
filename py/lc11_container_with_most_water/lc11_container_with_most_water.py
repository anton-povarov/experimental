# https://leetcode.com/problems/container-with-most-water/

# written in LC online editor
# harder than I expected, went the wrong way initially (left/right prefix volumes)
# solved with two pointers (looked at solutions)


class Solution:
    def maxArea(self, height: List[int]) -> int:
        n = len(height)

        best_vol = 0

        l = 0
        r = n - 1

        while l < r:
            hl, hr = height[l], height[r]
            vol = (r - l) * min(hl, hr)
            best_vol = max(best_vol, vol)

            if hl < hr:
                l += 1
            else:
                r -= 1

        return best_vol
