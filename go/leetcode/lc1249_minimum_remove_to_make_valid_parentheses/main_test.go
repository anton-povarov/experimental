// https://leetcode.com/problems/minimum-remove-to-make-valid-parentheses/

package main

import (
	tu "antoxa/leetcode/testutil"
	"slices"

	"testing"
)

func minRemoveToMakeValid(s string) string {

	// forward iteration, removing extra close parens
	out := make([]byte, 0, len(s))
	counter := 0
	for i := 0; i < len(s); i++ {
		switch s[i] {
		case '(':
			counter++
		case ')':
			if counter == 0 { // remove this paren
				continue
			}
			counter--
		}
		out = append(out, s[i])
	}
	s = string(out)

	// backward iteration, removing extra open parens
	out = out[:0]
	counter = 0
	for i := len(s) - 1; i >= 0; i-- {
		switch s[i] {
		case ')':
			counter++
		case '(':
			if counter == 0 { // remove this paren
				continue
			}
			counter--
		}
		out = append(out, s[i])
	}

	slices.Reverse(out)
	return string(out)
}

var testData = []tu.TestData[string, string]{
	{Input: "lee(t(c)o)de)", Expected: "lee(t(c)o)de"},
	{Input: "a)b(c)d", Expected: "ab(c)d"},
	{Input: "))((", Expected: ""},
	{Input: "", Expected: ""},
}

func TestMain(t *testing.T) {
	t.Run("two_scans", func(t *testing.T) { tu.RunTest(t, minRemoveToMakeValid, testData) })
}

func BenchmarkLengthOfLastWord(b *testing.B) {
	for b.Loop() {
		minRemoveToMakeValid(testData[0].Input)
	}
}
