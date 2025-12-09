package main

import (
	tu "antoxa/leetcode/testutil"

	"strings"
	"testing"
	"unicode"
)

func lengthOfLastWord_handmade(s string) int {
	if len(s) == 0 {
		return 0
	}

	rs := []rune(s)

	i := len(rs) - 1
	for i >= 0 && unicode.IsSpace(rs[i]) {
		i--
	}

	j := i
	for j >= 0 && !unicode.IsSpace(rs[j]) {
		j--
	}

	return i - j
}

func lengthOfLastWord_builtin_funcs(s string) int {
	words := strings.Split(strings.TrimRight(s, " \t\n\r"), " ")
	return len(words[len(words)-1])
}

func TestLengthOfLastWord(t *testing.T) {
	data := []tu.TestData[string, int]{
		{Input: "Hello World", Expected: 5},
		{Input: "Hello    World   ", Expected: 5},
		{Input: "Hello    World   -", Expected: 1},
		{Input: "   ", Expected: 1},
	}

	t.Run("with_builtins", func(t *testing.T) { tu.RunTest(t, lengthOfLastWord_builtin_funcs, data) })
	t.Run("with_handmade", func(t *testing.T) { tu.RunTest(t, lengthOfLastWord_handmade, data) })
}
