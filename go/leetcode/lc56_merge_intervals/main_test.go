// https://leetcode.com/problems/merge-intervals/

package main

import (
	tu "antoxa/leetcode/testutil"
	"slices"
	"testing"
)

func intervals_deep_copy(intervals [][]int) [][]int {
	result := slices.Clone(intervals)
	for i := range result {
		result[i] = slices.Clone(result[i])
	}
	return result
}

// this function alters the input array in-place to avoid making deep copies of slices
// deep copy before calling this, if you want to avoid that
func merge_intevals_fold(intervals [][]int) [][]int {
	if len(intervals) <= 1 {
		return intervals
	}

	slices.SortFunc(intervals, func(l, r []int) int { return slices.Compare(l, r) })

	out_i := 0

	for _, iv := range intervals[1:] {
		out_iv := intervals[out_i]
		if out_iv[1] < iv[0] { // disjointed
			out_i++               // keep the current interval intact then
			intervals[out_i] = iv // copy the next interval to output for merging
		} else if out_iv[1] < iv[1] { // half overlap [out_l .. iv_l .. out_r .. iv_r]
			intervals[out_i][1] = iv[1] // extend current interval to the end of iv => [out_l .. iv_r]
		} else { // full overlap [out_l .. iv_l .. iv_r .. our_r]
			// nothing, we've consumed the iv fully, on to the next one
		}
	}
	return intervals[:out_i+1]
}

func merge_wrapper__intevals_fold(intervals [][]int) [][]int {
	return merge_intevals_fold(intervals_deep_copy(intervals))
}

func merge(intervals [][]int) (result [][]int) {
	return merge_intevals_fold(intervals)
}

var testData = []tu.TestData[[][]int, [][]int]{
	{Input: [][]int{}, Expected: [][]int{}},
	{
		Input:    [][]int{{1, 3}, {2, 6}, {8, 10}, {15, 18}},
		Expected: [][]int{{1, 6}, {8, 10}, {15, 18}},
	},
	{
		Input:    [][]int{{1, 4}, {4, 5}},
		Expected: [][]int{{1, 5}},
	},
	{
		Input:    [][]int{{1, 4}, {6, 7}, {-10, 6}},
		Expected: [][]int{{-10, 7}},
	},
	{
		Input:    [][]int{{1, 4}, {6, 8}, {-10, 6}},
		Expected: [][]int{{-10, 8}},
	},
}

func TestFold(t *testing.T) {
	tu.RunTest(t, merge_wrapper__intevals_fold, testData)
}
