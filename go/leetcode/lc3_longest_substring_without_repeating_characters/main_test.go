package main

import (
	tu "antoxa/leetcode/testutil"
	"testing"
)

func longestSubstring(s string) string {
	rs := []rune(s)

	max_substr := ""

	begin := 0
	counters := map[rune]int{} // rune -> offset

	for i := range len(rs) {
		dup_pos, ok := counters[rs[i]]
		if ok { // duplicate found at position dup_pos
			for j := begin; j <= dup_pos; j++ {
				delete(counters, rs[j])
			}
			begin = dup_pos + 1
		}
		counters[rs[i]] = i
		if i+1-begin > len(max_substr) {
			max_substr = s[begin : i+1]
		}
	}
	return max_substr
}

func longestSubstringLength(s string) int {
	return len(longestSubstring(s))
}

var testData = []tu.TestData[string, int]{
	{Input: "abcabcbb", Expected: 3}, // abc or bca or cab - all valid
	{Input: "bbbb", Expected: 1},
	{Input: " ", Expected: 1},
	{Input: "pwwkew", Expected: 3},
	{Input: "jxdlnaaij", Expected: 6},
	{Input: "dvdf", Expected: 3},
}

func TestLongestSubstring(t *testing.T) {
	tu.RunTest(t, longestSubstringLength, testData)
}
