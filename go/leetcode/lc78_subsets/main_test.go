package main

import (
	tu "antoxa/leetcode/testutil"
	"cmp"
	"math/bits"
	"slices"
	"testing"
)

func subsets_recursive_path(nums []int) (result [][]int) {
	result = slices.Grow(result, (1 << len(nums)))

	var recursive func(prefix []int, start_i int)
	recursive = func(prefix []int, start_i int) {
		result = append(result, prefix)
		// loop acts as the "don't include me" branch
		for i, num := range nums[start_i:] {
			recursive(slices.Concat(prefix, []int{num}), start_i+i+1)
		}
	}

	recursive([]int{}, 0)
	return sortSliceToTestEqual(result)
}

func subsets_recursive_return(nums []int) [][]int {

	var recursive func(start_i int) [][]int
	recursive = func(start_i int) (result [][]int) {
		if start_i >= len(nums) {
			return [][]int{{}}
		}
		for _, tail := range recursive(start_i + 1) {
			result = append(result, slices.Clone(tail))          // do not include me
			result = append(result, append(tail, nums[start_i])) // include me
		}
		return
	}

	return sortSliceToTestEqual(recursive(0))
}

func subsets_recursive_append(nums []int) (result [][]int) {
	result = slices.Grow(result, (1 << len(nums)))

	var recursive func(prefix []int, start_i int)
	recursive = func(prefix []int, start_i int) {
		if start_i >= len(nums) {
			return
		}

		// do not include me
		// result = append(result, slices.Clone(prefix))
		recursive(prefix, start_i+1)

		// include me
		prefix = append(prefix, nums[start_i])
		result = append(result, slices.Clone(prefix))
		recursive(prefix, start_i+1)
	}

	result = append(result, []int{}) // empty set
	recursive([]int{}, 0)
	return sortSliceToTestEqual(result)
}

func subsets_recursive_inplace(nums []int) (result [][]int) {
	result = slices.Grow(result, (1 << len(nums)))

	var recursive func(prefix []int, start_i int)
	recursive = func(prefix []int, start_i int) {
		for i, num := range nums[start_i:] {
			prefix = append(prefix, num)
			result = append(result, slices.Clone(prefix))
			recursive(prefix, start_i+i+1)
			prefix = prefix[:len(prefix)-1]
		}
	}

	result = append(result, []int{}) // empty set
	recursive([]int{}, 0)
	return sortSliceToTestEqual(result)
}

func subsets_iterative(nums []int) (result [][]int) {
	result = slices.Grow(result, (1 << len(nums)))
	result = append(result, []int{})

	for _, num := range nums {
		rlen := len(result)
		for ri := range rlen {
			result = append(result, slices.Concat(result[ri], []int{num}))
		}
	}
	return sortSliceToTestEqual(result)
}

func subsets_iterative_bits(nums []int) (result [][]int) {
	result = slices.Grow(result, (1 << len(nums)))

	for i := range uint(1 << len(nums)) {
		subset := make([]int, 0, bits.OnesCount(i))
		for j := range len(nums) {
			if (i & (1 << j)) != 0 {
				subset = append(subset, nums[j])
			}
		}
		result = append(result, subset)
	}
	return sortSliceToTestEqual(result)
}

func sortSliceToTestEqual(xs [][]int) [][]int {
	for i := range xs {
		slices.SortFunc(xs[i], func(l, r int) int { return cmp.Compare(l, r) })
	}
	slices.SortFunc(xs, func(l, r []int) int { return slices.Compare(l, r) })
	return xs
}

var testData = []tu.TestData[[]int, [][]int]{
	{
		Input:    []int{1, 2, 3},
		Expected: sortSliceToTestEqual([][]int{{}, {1}, {2}, {1, 2}, {3}, {1, 3}, {2, 3}, {1, 2, 3}}),
	},
	{
		Input:    []int{3, 2, 1},
		Expected: sortSliceToTestEqual([][]int{{}, {1}, {2}, {1, 2}, {3}, {1, 3}, {2, 3}, {1, 2, 3}}),
	},
	{
		Input:    []int{9, 0, 3, 5, 7},
		Expected: sortSliceToTestEqual([][]int{{}, {9}, {0}, {0, 9}, {3}, {3, 9}, {0, 3}, {0, 3, 9}, {5}, {5, 9}, {0, 5}, {0, 5, 9}, {3, 5}, {3, 5, 9}, {0, 3, 5}, {0, 3, 5, 9}, {7}, {7, 9}, {0, 7}, {0, 7, 9}, {3, 7}, {3, 7, 9}, {0, 3, 7}, {0, 3, 7, 9}, {5, 7}, {5, 7, 9}, {0, 5, 7}, {0, 5, 7, 9}, {3, 5, 7}, {3, 5, 7, 9}, {0, 3, 5, 7}, {0, 3, 5, 7, 9}}),
	},
}

func TestRecursivePath(t *testing.T) {
	tu.RunTest(t, subsets_recursive_path, testData)
}

func TestRecursiveReturn(t *testing.T) {
	tu.RunTest(t, subsets_recursive_return, testData)
}

func TestRecursiveAppend(t *testing.T) {
	tu.RunTest(t, subsets_recursive_append, testData)
}

func TestRecursiveInplace(t *testing.T) {
	tu.RunTest(t, subsets_recursive_inplace, testData)
}

func TestIterative(t *testing.T) {
	tu.RunTest(t, subsets_iterative, testData)
}

func TestIterativeBits(t *testing.T) {
	tu.RunTest(t, subsets_iterative_bits, testData)
}

var benchmarkData = testData[2].Input

func BenchmarkRecursivePath(b *testing.B) {
	for b.Loop() {
		subsets_recursive_path(benchmarkData)
	}
}

func BenchmarkRecursiveReturn(b *testing.B) {
	for b.Loop() {
		subsets_recursive_return(benchmarkData)
	}
}

func BenchmarkRecursiveAppend(b *testing.B) {
	for b.Loop() {
		subsets_recursive_append(benchmarkData)
	}
}

func BenchmarkRecursiveInplace(b *testing.B) {
	for b.Loop() {
		subsets_recursive_inplace(benchmarkData)
	}
}

func BenchmarkIterative(b *testing.B) {
	for b.Loop() {
		subsets_iterative(benchmarkData)
	}
}

func BenchmarkIterativeBits(b *testing.B) {
	for b.Loop() {
		subsets_iterative_bits(benchmarkData)
	}
}
