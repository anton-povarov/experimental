// https://leetcode.com/problems/minimum-remove-to-make-valid-parentheses/

package main

import (
	tu "antoxa/leetcode/testutil"
	"fmt"
	"slices"

	"testing"
)

func minRemoveToMakeValid_forward_backward(s string) string {

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

// double backward iteration
// allows to avoid reversing the string, as it's reversed naturally during the backward pass
// but does not allow to opimize copy in multiple chunks (reverse works per character)
func minRemoveToMakeValid_backward_forward(s string) string {
	strip_backward := func(s []byte, open, close byte) []byte {
		out := make([]byte, len(s)) // should be on stack with any sort of good escape analysis
		out_i := 0
		counter := 0
		for i := len(s) - 1; i >= 0; i-- {
			switch s[i] {
			case close:
				if counter == 0 {
					continue
				}
				counter--
			case open:
				counter++
			}
			out[out_i] = s[i] // this is noticeably faster than appending
			out_i++
		}
		return out[:out_i]
	}

	// 1st pass, strip extra '('-s
	out := strip_backward([]byte(s), ')', '(')

	// 2nd pass, strip extra ')'-s
	out2 := strip_backward(out, '(', ')')

	// this allocates, as strings are immutable
	return string(out2)
}

// this is faster, but there is a problem
// we need to keep track of "bad" parens
// and this stack takes memory, so if the nesting is deep - this will grow
// = use a much more memory than needed
// at some point with nesting - it becomes slower than the double backward pass version
func minRemoveToMakeValid_single_pass(s string) string {
	stack := make([]int, 0, 5)

	out := make([]byte, len(s))
	out_i := 0
	start_i := 0

	for i := range len(s) {
		switch s[i] {
		case '(':
			stack = append(stack, i)
		case ')':
			if len(stack) == 0 {
				copy(out[out_i:], s[start_i:i])
				out_i += i - start_i
				start_i = i + 1
				continue
			}
			stack = stack[:len(stack)-1]
		}
	}

	for len(stack) > 0 {
		copy(out[out_i:], s[start_i:stack[0]])
		out_i += stack[0] - start_i
		start_i = stack[0] + 1
		stack = stack[1:]
	}
	copy(out[out_i:], s[start_i:])
	out_i += len(s) - start_i

	return string(out[:out_i])
}

// optimistic optimization of the backward_forward pass
// first tries to find and copy all the valid substrings
// the remainder is a tail with N opening parens >= N closed parens
// from there - we backward pass the tail and then another pass to reverse it
// this approach should always be faster than backward_forward (but sometimes, by about 0)
func minRemoveToMakeValid_optimistic(s string) string {
	out := make([]byte, len(s))
	out_i := 0
	start_i := 0
	counter := 0

	// copy all correct substrings, skipping bad closing parens
	for i := range len(s) {
		switch s[i] {
		case '(':
			counter++
		case ')':
			if counter == 0 {
				out_i += copy(out[out_i:], s[start_i:i])
				start_i = i + 1
				continue
			}
			counter--
		}
	}

	if counter == 0 {
		// just copy the tail if we don't have any more imbalances
		out_i += copy(out[out_i:], s[start_i:])

	} else {

		// at this point s[start_i:] has a counter >= 0 (i.e. there is a bunch of unmatched opening parens)
		// so here comes the slower part
		// 1. sweep backwards, skipping bad opening parens
		// 2. this will produce correct bytes but in a reversed order
		// 3. reverse it back in place before returning

		tmp_out_i := out_i
		counter = 0
		for i := len(s) - 1; i >= start_i; i-- {
			switch s[i] {
			case ')':
				counter++
			case '(':
				if counter == 0 {
					continue
				}
				counter--
			}
			out[out_i] = s[i]
			out_i++
		}

		slices.Reverse(out[tmp_out_i:out_i])
	}
	return string(out[:out_i])
}

// same as optimistic, but eagerly copy on forward pass and only go to the latest unmatched '(' on backward
// this is good if the mismatched ')' are at the end, as is usually the case in programming
func minRemoveToMakeValid_optimistic_by_bytes(s string) string {
	out := make([]byte, len(s))
	out_i := 0

	skipped := 0
	counter := 0
	start_i := 0

	for i := range len(s) {
		switch s[i] {
		case '(':
			if counter == 0 {
				start_i = i
			}
			counter++
		case ')':
			if counter == 0 {
				skipped++
				continue
			}
			counter--
		}
		out[out_i] = s[i]
		out_i++
	}

	if counter == 0 {
		start_i = len(s)
	}

	// fmt.Printf("[%d]%q start_i = %d, skipped = %d, counter = %d, out_i = %d, out = %q\n",
	// 	len(s), s, start_i, skipped, counter, out_i, out)

	remaining_len := len(s) - start_i - counter
	out_end_i := start_i - skipped + remaining_len
	out_i = out_end_i

	// fmt.Printf("remaining = %d, out_i = %d\n", remaining_len, out_i)

	counter = 0
	for i := len(s) - 1; i >= start_i; i-- {
		switch s[i] {
		case '(':
			if counter == 0 {
				continue
			}
			counter--
		case ')':
			counter++
		}
		out_i--
		out[out_i] = s[i]
	}

	return string(out[:out_end_i])
}

// same as optimistic, but backward pass first
// this allows to be faster (no reverses required) unless there is a bunch of closing parens at the end
// unfortunately - the situation with a lot of extra closing parens
// is much more common than the situation with a lot of opening parens!
func minRemoveToMakeValid_optimistic_backward(s string) string {
	out := make([]byte, len(s))
	out_end_i := len(out)
	end_i := len(s)
	counter := 0

	// copy all correct substrings, skipping bad opening parens
	for i := len(s) - 1; i >= 0; i-- {
		switch s[i] {
		case ')':
			counter++
		case '(':
			if counter == 0 {
				src := s[i+1 : end_i]
				out_end_i -= copy(out[out_end_i-len(src):], src)
				end_i = i
				continue
			}
			counter--
		}
	}

	// at this point s[:end_i] has a counter >= 0 (i.e. there is `counter` of unmatched closing parens)
	// we're writing forward now, writing (end_i - counter) bytes
	// because we know we're going to be removing `counter` opening parens
	out_i := out_end_i - (end_i - counter) // reserve space in the output buffer
	out_begin_i := out_i                   // save, need this for return
	counter = 0
	for i := range end_i {
		switch s[i] {
		case '(':
			counter++
		case ')':
			if counter == 0 {
				continue
			}
			counter--
		}
		out[out_i] = s[i]
		out_i++
	}

	// allocates, copies
	return string(out[out_begin_i:])
}

// similar to stack, but don't remember positions, just zero the bytes
// would be funky as fuck to adapt for utf-8 strings
// none of the other functions are adapted, so just for fun
// apparently - this is almost never faster than the others
// i guess we're traversing/copying the string more times than the other algos
func minRemoveToMakeValid_zeroit_non_utf8(s string) string {
	tmp := []byte(s) // this will copy the string as we're going to mutate `tmp`

	// forward pass, zero all the extra ')'
	counter := 0
	for i := range len(s) {
		switch s[i] {
		case '(':
			counter++
		case ')':
			if counter == 0 {
				tmp[i] = 0x0
				continue
			}
			counter--
		}
	}

	// backward pass, zero all the extra '('
	counter = 0
	for i := len(s) - 1; i >= 0; i-- {
		switch s[i] {
		case ')':
			counter++
		case '(':
			if counter == 0 {
				tmp[i] = 0x0
				continue
			}
			counter--
		}
	}

	// copy out all the nonzero parts
	out := make([]byte, len(s))
	out_i := 0

	for i := range len(tmp) {
		if tmp[i] != 0x0 {
			out[out_i] = tmp[i]
			out_i++
		}
	}

	return string(out[:out_i])
}

var testData_normal = []tu.TestData[string, string]{
	{Input: "lee(t(c)o)de)2aaa()a)", Expected: "lee(t(c)o)de2aaa()a"},
	{Input: "lee(t(c)o)de)", Expected: "lee(t(c)o)de"},
	{Input: "a)b(c)d", Expected: "ab(c)d"},
	{Input: "))((", Expected: ""},
	{Input: "", Expected: ""},
}

var testData_large = []tu.TestData[string, string]{
	{
		Input:    "aaaa(aadknasl)d((kasn;dnqdknasd())qadlqns dad()))))))))))))))))))))))(())))))))))))))",
		Expected: "aaaa(aadknasl)d((kasn;dnqdknasd())qadlqns dad())(())",
	},
	{
		Input:    "aaaa(aadknasl)d((kasn;dnqdknasd())qadlqns dad()",
		Expected: "aaaa(aadknasl)d(kasn;dnqdknasd())qadlqns dad()",
	},
}

var testData_deep = []tu.TestData[string, string]{
	{
		Input:    "aaaa(aadknasl)d((kasn;dn(((((((((qdknasd())qadlqns dad()",
		Expected: "aaaa(aadknasl)dkasn;dn(qdknasd())qadlqns dad()",
	},
}

var testData_cringe = []tu.TestData[string, string]{
	{
		Input:    "))))))()))))(((((((((((((aa((((((((aa(aadknasl)d((kasn;dn(((((((((qdknasd())qadlqns dad()",
		Expected: "()aaaa(aadknasl)dkasn;dn(qdknasd())qadlqns dad()",
	},
}

func TestMain(t *testing.T) {
	var testData = testData_normal
	testData = append(testData, testData_large...)
	testData = append(testData, testData_deep...)
	testData = append(testData, testData_cringe...)

	t.Run("forward_backward", func(t *testing.T) { tu.RunTest(t, minRemoveToMakeValid_forward_backward, testData) })
	t.Run("backward_forward", func(t *testing.T) { tu.RunTest(t, minRemoveToMakeValid_backward_forward, testData) })
	t.Run("single_pass", func(t *testing.T) { tu.RunTest(t, minRemoveToMakeValid_single_pass, testData) })
	t.Run("optimistic", func(t *testing.T) { tu.RunTest(t, minRemoveToMakeValid_optimistic, testData) })
	t.Run("optimistic_bytes", func(t *testing.T) { tu.RunTest(t, minRemoveToMakeValid_optimistic_by_bytes, testData) })
	t.Run("optimistic_back", func(t *testing.T) { tu.RunTest(t, minRemoveToMakeValid_optimistic_backward, testData) })
	t.Run("zeroit", func(t *testing.T) { tu.RunTest(t, minRemoveToMakeValid_zeroit_non_utf8, testData) })
}

func BenchmarkLengthOfLastWord(b *testing.B) {

	run_for_str := func(name string, test_str string) {
		b.Run(fmt.Sprintf("%s/f_b", name), func(b *testing.B) {
			for b.Loop() {
				minRemoveToMakeValid_forward_backward(test_str)
			}
		})
		b.Run(fmt.Sprintf("%s/b_f", name), func(b *testing.B) {
			for b.Loop() {
				minRemoveToMakeValid_backward_forward(test_str)
			}
		})
		b.Run(fmt.Sprintf("%s/one", name), func(b *testing.B) {
			for b.Loop() {
				minRemoveToMakeValid_single_pass(test_str)
			}
		})
		b.Run(fmt.Sprintf("%s/opti", name), func(b *testing.B) {
			for b.Loop() {
				minRemoveToMakeValid_optimistic(test_str)
			}
		})
		b.Run(fmt.Sprintf("%s/opti_bb", name), func(b *testing.B) {
			for b.Loop() {
				minRemoveToMakeValid_optimistic_by_bytes(test_str)
			}
		})
		b.Run(fmt.Sprintf("%s/opti_back", name), func(b *testing.B) {
			for b.Loop() {
				minRemoveToMakeValid_optimistic_backward(test_str)
			}
		})
		b.Run(fmt.Sprintf("%s/zero", name), func(b *testing.B) {
			for b.Loop() {
				minRemoveToMakeValid_zeroit_non_utf8(test_str)
			}
		})
	}

	run_for_str("normal", testData_normal[0].Input)
	run_for_str("large", testData_large[0].Input)
	run_for_str("deep", testData_deep[0].Input)
	run_for_str("cringe", testData_cringe[0].Input)
}
