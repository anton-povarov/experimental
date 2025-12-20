// https://leetcode.com/problems/find-first-and-last-position-of-element-in-sorted-array/

package main

import (
	tu "antoxa/leetcode/testutil"
	"cmp"
	"slices"
	"testing"
)

// ! use standard library provided binsearch
// this is a bit of cheating, since LC (and an interviewer probably), would like you to write binsearch yourself
func searchRange_library(nums []int, target int) []int {
	idx, found := slices.BinarySearch(nums, target)
	if !found {
		return []int{-1, -1}
	}

	i := idx + 1
	for ; i < len(nums) && nums[i] == target; i++ {
	}
	return []int{idx, i - 1}
}

// LowerBound is the same as slices.BinarySearch
// finds the _first_ position where an element would be inserted provided the array is sorted
// according to the comparison function `compare`.
// First result is the index to insert, second result - if the element was already found at that position
func LowerBound[T any](input []T, target T, compare func(T, T) int) (int, bool) {
	if len(input) == 0 {
		return 0, false
	}

	begin := 0
	end := len(input)

	// binsearch while the array is large
	// do NOT end if we get lucky with pivot, array might contain duplicates and
	//  pivot elt is necessarily be the first one of them
	for (end - begin) > 4 {
		// fmt.Printf("[%d, %d] -> %v\n", begin, end, nums[begin:end])
		pivot := begin + (end-begin)/2
		// fmt.Printf("pivot: %d(%d) -> %d\n", pivot-begin, pivot, nums[pivot])
		switch compare(input[pivot], target) {
		case -1: // [... pivot ... maybe target ...]
			begin = pivot
		case 1: // [ ... maybe target ... pivot ... ]
			end = pivot + 1
		case 0: // [ ... maybe target . pivot . maybe target still ...]
			end = pivot + 1
		}
	}

	// linear search when the array is small enough
	// fmt.Printf("[%d, %d] -> %v\n", begin, end, nums[begin:end])

	i := begin
linearSearch:
	for ; i < end; i++ {
		// fmt.Printf("[%d] -> %v\n", i, nums[i])
		switch compare(input[i], target) {
		case 0: // input[i] == target
			return i, true
		case 1: // input[i] > target
			break linearSearch
		}
	}
	return i, false
}

// UpperBound is complementary to LowerBound
// finds the _last_ position where an element would be inserted provided the array is sorted
// according to the comparison function `compare`.
// This function is similar to C++ std::upper_bound and Python's bisect.bisect_right
// First result is the element index, second result - if the element was already found at that position
func UpperBound[T any](input []T, target T, compare func(T, T) int) (int, bool) {
	if len(input) == 0 {
		return 0, false
	}

	begin := 0
	end := len(input)

	// binsearch while the array is large
	// do NOT end if we get lucky with pivot, array might contain duplicates and
	//  pivot elt is necessarily be the first one of them
	for (end - begin) > 4 {
		// fmt.Printf("[%d, %d] -> %v\n", begin, end, nums[begin:end])
		pivot := begin + (end-begin)/2
		// fmt.Printf("pivot: %d(%d) -> %d\n", pivot-begin, pivot, nums[pivot])
		switch compare(input[pivot], target) {
		case -1: // [... pivot ... maybe target ...]
			begin = pivot
		case 1: // [ ... maybe target ... pivot ... ]
			end = pivot + 1
		case 0: // [ ... maybe target . pivot . maybe target still ...]
			begin = pivot
		}
	}

	// linear search when the array is small enough
	// fmt.Printf("[%d, %d] -> %v\n", begin, end, nums[begin:end])

	i := end - 1
linearSearchBackwards:
	for ; i >= begin; i-- {
		// fmt.Printf("[%d] -> %v\n", i, nums[i])
		switch compare(input[i], target) {
		case 0: // input[i] == target
			return i + 1, true
		case -1: // input[i] > target
			break linearSearchBackwards
		}
	}
	return i + 1, false
}

func searchRange_manual_lower_and_loop(nums []int, target int) []int {

	idx, found := LowerBound(nums, target, cmp.Compare)
	if !found {
		return []int{-1, -1}
	}

	i := idx + 1
	for ; i < len(nums) && nums[i] == target; i++ {
	}
	return []int{idx, i - 1}
}

func searchRange_manual_lower_upper(nums []int, target int) []int {

	lower_idx, lower_found := LowerBound(nums, target, cmp.Compare)
	upper_idx, upper_found := UpperBound(nums, target, cmp.Compare)

	if !lower_found || !upper_found {
		return []int{-1, -1}
	}
	return []int{lower_idx, upper_idx - 1}
}

// ------------------------------------------------------------------------------------------------

type InputData struct {
	Arr    []int
	Target int
}

var testData = []tu.TestData[InputData, []int]{
	{
		Input:    InputData{Arr: []int{5, 7, 7, 8, 8, 10}, Target: 8},
		Expected: []int{3, 4},
	},
	{
		Input:    InputData{Arr: []int{1, 2, 4, 5, 7}, Target: 8},
		Expected: []int{-1, -1},
	},
	{
		Input:    InputData{Arr: []int{9, 9, 9, 9, 9, 9}, Target: 8},
		Expected: []int{-1, -1},
	},
	{
		Input:    InputData{Arr: []int{1, 1, 1, 1, 1, 1, 1, 1, 1, 7, 8, 8, 8, 10}, Target: 8},
		Expected: []int{10, 12},
	},
	{
		Input:    InputData{Arr: []int{1, 1, 1, 1, 1, 1, 1, 1, 1, 7, 8, 8, 8, 8, 8, 8, 8, 8, 10}, Target: 8},
		Expected: []int{10, 17},
	},
	{
		Input:    InputData{Arr: []int{}, Target: 8},
		Expected: []int{-1, -1},
	},
}

func testWrapper(test_func func([]int, int) []int) func(d InputData) []int {
	return func(d InputData) []int {
		return test_func(d.Arr, d.Target)
	}
}

func TestSearchWithLibrary(t *testing.T) {
	tu.RunTest(t, testWrapper(searchRange_library), testData)
}

func TestSearchManual_LowerAndLoop(t *testing.T) {
	tu.RunTest(t, testWrapper(searchRange_manual_lower_and_loop), testData)
}

func TestSearchManual_LowerUpper(t *testing.T) {
	tu.RunTest(t, testWrapper(searchRange_manual_lower_upper), testData)
}
