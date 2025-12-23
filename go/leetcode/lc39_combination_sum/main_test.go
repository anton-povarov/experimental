// https://leetcode.com/problems/combination-sum/
// https://neetcode.io/problems/combination-target-sum/

package main

import (
	tu "antoxa/leetcode/testutil"
	"cmp"
	"slices"
	"testing"
)

func combinationSum_recursive(n int, prefix []int, nums []int, target int) (result [][]int) {
	// fmt.Printf("%s p %v, n %v, t %v\n", strings.Repeat(">", n), prefix, nums, target)

	for i, num := range nums {
		if num > target {
			break
		}

		if num == target {
			result = append(result, slices.Concat(prefix, []int{num}))
			break
		}

		prefix = append(prefix, num)
		result = append(result, combinationSum_recursive(n+1, prefix, nums[i:], target-num)...)
		prefix = prefix[:len(prefix)-1]
	}

	// fmt.Printf("%s %v\n", strings.Repeat("<", n), result)
	return
}

// combinationSum finds all combinations of unique numbers from `nums` that sum up to `target`
// each number can be used multiple times
// the idea is similar to the "coin change" algorithm, but
// instead of counting the min number of coins needed - it counts all possible variants without duplicates
// the key to avoid duplicates is to
// exhaust all options for a number (in combination with all others) first and
// then exclude it completely when other numbers are tried
// this function sorts incoming numbers to be more efficient at skipping impossible compbinations
func combinationSum(nums []int, target int) (result [][]int) {
	if len(nums) == 0 {
		return nil
	}
	slices.Sort(nums)
	result = combinationSum_recursive(1, []int{}, nums, target)
	return sortSliceToTestEqual(result)
}

// combinationSum2 is similar to combinationSum, but
//  1. does not sort `nums`
//     means we must not to skip everything after we've found nums[i] == target
//     which might be less efficient than sorting, due to a bit more branching
//  2. uses an inline recursive function (go is a bit weird syntax-wise here)
//  3. appends to result inside recurive calls, instead of returning an array of them
//     this should be more efficient on the GC/memcpy side)
func combinationSum2(nums []int, target int) (result [][]int) {
	if len(nums) == 0 {
		return nil
	}

	var recursive func(prefix []int, start_i int, target int)
	recursive = func(prefix []int, start_i int, target int) {
		for i, num := range nums[start_i:] {
			if num > target {
				continue
			}

			prefix = append(prefix, num)

			if num == target {
				result = append(result, slices.Clone(prefix))
			} else {
				recursive(prefix, start_i+i, target-num)
			}
			prefix = prefix[:len(prefix)-1]
		}
	}

	recursive(make([]int, 0, len(nums)), 0, target)
	return sortSliceToTestEqual(result)
}

func sortSliceToTestEqual(xs [][]int) [][]int {
	for i := range xs {
		slices.SortFunc(xs[i], func(l, r int) int { return cmp.Compare(l, r) })
	}
	slices.SortFunc(xs, func(l, r []int) int { return slices.Compare(l, r) })
	return xs
}

var testData = []tu.TestData2[[]int, int, [][]int]{
	{
		Input1:   []int{2, 5, 6, 9},
		Input2:   9,
		Expected: sortSliceToTestEqual([][]int{{2, 2, 5}, {9}}),
	},
	{
		Input1:   []int{2, 3, 5},
		Input2:   8,
		Expected: sortSliceToTestEqual([][]int{{2, 2, 2, 2}, {2, 3, 3}, {3, 5}}),
	},
	{
		Input1:   []int{4, 2, 8},
		Input2:   8,
		Expected: sortSliceToTestEqual([][]int{{2, 2, 2, 2}, {2, 2, 4}, {4, 4}, {8}}),
	},
	{
		Input1:   []int{3, 4, 5},
		Input2:   16,
		Expected: sortSliceToTestEqual([][]int{{3, 3, 3, 3, 4}, {3, 3, 5, 5}, {4, 4, 4, 4}, {3, 4, 4, 5}}),
	},
}

func TestCombination(t *testing.T) {
	tu.RunTest2(t, combinationSum, testData)
}

func TestCombination2(t *testing.T) {
	tu.RunTest2(t, combinationSum2, testData)
}
