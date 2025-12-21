package main

import (
	tu "antoxa/leetcode/testutil"
	"testing"
)

func generate_openclose_with_return_step(open int, close int) (result []string) {
	// fmt.Printf("generateParenthesis_bits_step: %d %d\n", open, close)

	if open == 0 && close == 0 { // recursion terminator
		result = []string{""}
		// don't return here, useful when debug print is uncommented before return at the bottom
	} else {
		if open > 0 {
			for _, sp := range generate_openclose_with_return_step(open-1, close) {
				result = append(result, "("+sp)
			}
		}
		if close > open {
			for _, sp := range generate_openclose_with_return_step(open, close-1) {
				result = append(result, ")"+sp)
			}
		}
	}

	// fmt.Printf(" (%d, %d) -> %#v\n", open, close, result)

	return
}

func generate_openclose_with_return(n int) (result []string) {
	return generate_openclose_with_return_step(n, n)
}

func generate_openclose_step(result *[]string, prefix string, open int, close int) {
	// fmt.Printf("generateParenthesis_bits_step: %d %d\n", open, close)

	if open == 0 && close == 0 { // recursion terminator
		(*result) = append((*result), prefix)
		// don't return here, useful when debug print is uncommented before return at the bottom
	} else {
		if open > 0 {
			generate_openclose_step(result, prefix+"(", open-1, close)
		}
		if close > open {
			generate_openclose_step(result, prefix+")", open, close-1)
		}
	}

	// fmt.Printf(" (%d, %d) -> %#v\n", open, close, result)
}

func generate_openclose(n int) (result []string) {
	generate_openclose_step(&result, "", n, n)
	return
}

// generates duplicates around the ()+x and x+() paths
func generateParenthesis_with_dups(n int) (result []string) {
	switch n {
	case 0:
		return nil
	case 1:
		return []string{"()"}
	default:
		for _, sp := range generateParenthesis_with_dups(n - 1) {
			result = append(result, "("+sp+")")
			result = append(result, "()"+sp)
			result = append(result, sp+"()")
		}
	}
	return
}

var testData = []tu.TestData[int, []string]{
	{
		Input: 4,
		Expected: []string{
			"(((())))", "((()()))", "((())())", "((()))()",
			"(()(()))", "(()()())", "(()())()", "(())(())",
			"(())()()", "()((()))", "()(()())", "()(())()",
			"()()(())", "()()()()",
		},
	},
	{Input: 3, Expected: []string{"((()))", "(()())", "(())()", "()(())", "()()()"}},
	{Input: 2, Expected: []string{"(())", "()()"}},
	{Input: 1, Expected: []string{"()"}},
}

func TestRecursive(t *testing.T) {
	tu.RunTest(t, generateParenthesis_with_dups, testData)
}

func TestOpenCloseWithReturn(t *testing.T) {
	tu.RunTest(t, generate_openclose_with_return, testData)
}

func TestOpenClose(t *testing.T) {
	tu.RunTest(t, generate_openclose, testData)
}
