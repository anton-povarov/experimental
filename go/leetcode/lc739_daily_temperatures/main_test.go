// https://leetcode.com/problems/daily-temperatures/

package main

import (
	tu "antoxa/leetcode/testutil"
	"antoxa/leetcode/util/heap"
	"testing"
)

func dailyTemperatures_heap(temperatures []int) []int {
	type day struct {
		idx  int
		temp int
	}
	hh := *heap.New(func(l, r day) bool { return l.temp < r.temp })

	result := make([]int, len(temperatures))

	for i, temp := range temperatures {
		for !hh.Empty() && hh.Top().temp < temp {
			top := hh.Pop()
			result[top.idx] = i - top.idx
		}
		hh.Push(day{i, temp})
	}
	for !hh.Empty() {
		top := hh.Pop()
		result[top.idx] = 0
	}

	return result
}

func dailyTemperatures_multistack(temperatures []int) []int {
	const min_temp = 30
	const max_temp = 101
	stack := make([][]int, max_temp-min_temp)

	result := make([]int, len(temperatures))

	for i, temp := range temperatures {
		for j := min_temp; j < temp; j++ {
			for _, idx := range stack[j-min_temp] {
				result[idx] = i - idx
			}
			stack[j-min_temp] = nil
		}
		stack[temp-min_temp] = append(stack[temp-min_temp], i)
	}
	for j := min_temp; j < max_temp; j++ {
		for _, idx := range stack[j-min_temp] {
			result[idx] = 0
		}
	}

	return result
}

// similar to heap, but we don't really need a heap
// stack is sufficient:
// 1. if the next elt is larger - we pop elts, until it's the smallest
// 2. then we push the elt
// => This results in the stack always being sorted in descending order => we don't miss anything in step #1
// NOTE:
// this can be further optimized by storing intervals of elts (instead of all indexes) in the stack
// but the code becomes too complicated tbh
func dailyTemperatures_stack_grow_shrink(temperatures []int) []int {
	stack := make([]int, 0, 5)               // indexes in temperatures
	result := make([]int, len(temperatures)) // initializes with zeroes, important!

	for i, temp := range temperatures {
		for len(stack) > 0 {
			stack_last := stack[len(stack)-1]
			if temperatures[stack_last] >= temp {
				break
			}
			result[stack_last] = i - stack_last
			stack = stack[:len(stack)-1]
		}
		stack = append(stack, i)
	}

	// don't need to pop elts from stack here
	// our array was initialized with 0-s
	// and the task requires us to return 0-s for days for which no warmer temp exists
	// which is exactly the items remaining in the stack

	return result
}

var testData = []tu.TestData[[]int, []int]{
	{Input: []int{41, 40, 37, 35, 31, 31, 31, 32}, Expected: []int{0, 0, 0, 0, 3, 2, 1, 0}},
	{Input: []int{73, 74, 75, 71, 69, 72, 76, 73}, Expected: []int{1, 1, 4, 2, 1, 1, 0, 0}},
	{Input: []int{30, 50, 60, 90}, Expected: []int{1, 1, 1, 0}},
	{Input: []int{30}, Expected: []int{0}},
	{
		Input:    []int{30, 31, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30},
		Expected: []int{1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
	},
}

func TestHeap(t *testing.T) {
	tu.RunTest(t, dailyTemperatures_heap, testData)
}

func TestMultistack(t *testing.T) {
	tu.RunTest(t, dailyTemperatures_multistack, testData)
}

func TestStackValues(t *testing.T) {
	tu.RunTest(t, dailyTemperatures_stack_grow_shrink, testData)
}
