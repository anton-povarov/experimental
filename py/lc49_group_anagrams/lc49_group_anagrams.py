# https://leetcode.com/problems/group-anagrams/

# solved in online LC editor


class Solution:
    def groupAnagrams(self, strs: List[str]) -> List[List[str]]:
        d = defaultdict(list)

        for s in strs:
            d[str(sorted(s))].append(s)

        return [v for v in d.values()]
