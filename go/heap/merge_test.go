package main

import (
	"cmp"
	"fmt"
	"math/rand"
	"reflect"
	"slices"
	"testing"
)

type TestData struct {
	Name     string
	Input    [][]int
	Compare  HeapCompare[int]
	Expected []int
}

func generateTestDataPredefined() (result []TestData) {
	result = append(result,
		TestData{
			Name: "simple",
			Input: [][]int{
				{1, 2, 3, 4, 5},
				{3, 5, 7, 8, 9},
				{-1},
				{0, 6, 9, 10},
			},
			Compare:  cmp.Less[int],
			Expected: []int{-1, 0, 1, 2, 3, 3, 4, 5, 5, 6, 7, 8, 9, 9, 10},
		},
		TestData{
			Name: "large_to_small",
			Input: [][]int{
				{5, 4, 3, 2, 1},
				{9, 8, 7, 5, 3},
				{-1},
				{10, 9, 6, 0},
			},
			Compare:  func(l, r int) bool { return cmp.Compare(l, r) > 0 },
			Expected: []int{10, 9, 9, 8, 7, 6, 5, 5, 4, 3, 3, 2, 1, 0, -1},
		},
	)
	return
}

func generateTestDataRandom() (result []TestData) {
	type rndSettings struct {
		name    string
		n_lists int // number of lists to generare
		min_len int // min length of each list
		max_len int // max length of each list
	}
	rndData := []rndSettings{
		{"rnd_single", 1, 5, 10},         // single list
		{"rnd_few_short", 10, 10, 20},    // a few short lists
		{"rnd_few_long", 10, 500, 600},   // a few long lists
		{"rnd_many_short", 1000, 1, 10},  // many short lists
		{"rnd_many_vary", 1000, 1, 1000}, // many heavily varying lists
	}

	for _, data := range rndData {
		td := TestData{
			Name: data.name,
		}

		// input lists
		for range data.n_lists {
			list_len := data.min_len + rand.Intn(data.max_len-data.min_len)
			lst := make([]int, list_len)
			for j := range list_len {
				lst[j] = rand.Intn(100000)
			}
			slices.Sort(lst)
			td.Input = append(td.Input, lst)
		}

		// compare is just "less", aligned with slices.Sort
		td.Compare = cmp.Less

		// expected = merged + sorted input lists
		for _, lst := range td.Input {
			td.Expected = append(td.Expected, lst...)
		}
		slices.Sort(td.Expected)

		result = append(result, td)
	}
	return
}

func TestMergeSortedArrays(t *testing.T) {
	testData := []TestData{}
	testData = append(testData, generateTestDataPredefined()...)
	testData = append(testData, generateTestDataRandom()...)

	runTest := func(
		funcName string,
		testFunc func(inputs [][]int, compare HeapCompare[int]) []int,
	) {
		for _, td := range testData {
			t.Run(fmt.Sprintf("%s/%s", funcName, td.Name), func(t *testing.T) {
				res := testFunc(td.Input, td.Compare)
				if !reflect.DeepEqual(res, td.Expected) {
					fmt.Fprintf(t.Output(), "test failed for\n")
					fmt.Fprintf(t.Output(), " Input: %#v\n", td.Input)
					fmt.Fprintf(t.Output(), " Result: %#v\n", res)
					fmt.Fprintf(t.Output(), " Expected: %#v\n", td.Expected)
					t.FailNow()
				}
			})
		}
	}

	runTest("baseline", MergeSortedArrays_Baseline[int])
	runTest("value_copy", MergeSortedArrays_ValueCopy[int])
	runTest("value_ptr", MergeSortedArrays_ValueCachedPtr[int])
	runTest("more_ptrs", MergeSortedArrays_ValuePtr[int])
}

// ------------------------------------------------------------------------------------------------

type BenchData[T any] struct {
	Name    string
	Input   [][]T
	Compare HeapCompare[T]
}

func generateBenchmarkData[T any](genItem func() T, compare func(T, T) int) (result []BenchData[T]) {
	type rndSettings struct {
		name     string
		n_lists  int // number of lists to generare
		list_len int // length of each list, no randomness
	}
	rndData := []rndSettings{
		{"single", 1, 10},         // single list
		{"few_short", 10, 20},     // a few short lists
		{"few_long", 10, 500},     // a few long lists
		{"many_short", 1000, 10},  // many short lists
		{"many_long", 1000, 1000}, // many long lists
	}

	for _, data := range rndData {
		bd := BenchData[T]{Name: data.name}

		// input lists
		for range data.n_lists {
			lst := make([]T, data.list_len)
			for j := range data.list_len {
				lst[j] = genItem()
			}
			slices.SortFunc(lst, compare)
			bd.Input = append(bd.Input, lst)
		}

		// compare is adapted from the generic comparator used for sorting
		bd.Compare = func(l, r T) bool { return compare(l, r) < 0 }

		result = append(result, bd)
	}
	return
}

type blob [8]int64

func generateBenchmarkTestdata_Ints() []BenchData[int] {
	return generateBenchmarkData(
		func() int { return rand.Intn(100000) },
		cmp.Compare[int],
	)
}

func generateBenchmarkTestdata_Blobs() (result []BenchData[blob]) {

	return generateBenchmarkData(
		func() blob {
			b := blob{}
			b[0] = rand.Int63n(100000)
			return b
		},
		func(l, r blob) int {
			return slices.Compare(l[:], r[:])
		},
	)
}

func runWithBenchData[T any](b *testing.B, benchData []BenchData[T]) {
	for _, bd := range benchData {
		b.Run(fmt.Sprintf("%s/base", bd.Name), func(b *testing.B) {
			for b.Loop() {
				MergeSortedArrays_Baseline(bd.Input, bd.Compare)
			}
		})
		b.Run(fmt.Sprintf("%s/value_copy", bd.Name), func(b *testing.B) {
			for b.Loop() {
				MergeSortedArrays_ValueCopy(bd.Input, bd.Compare)
			}
		})
		b.Run(fmt.Sprintf("%s/value_ptr", bd.Name), func(b *testing.B) {
			for b.Loop() {
				MergeSortedArrays_ValueCachedPtr(bd.Input, bd.Compare)
			}
		})
		b.Run(fmt.Sprintf("%s/more_ptrs", bd.Name), func(b *testing.B) {
			for b.Loop() {
				MergeSortedArrays_ValuePtr(bd.Input, bd.Compare)
			}
		})
		b.Run(fmt.Sprintf("%s/adaptive", bd.Name), func(b *testing.B) {
			for b.Loop() {
				MergeSortedArrays_Adaptive(bd.Input, bd.Compare)
			}
		})
	}
}

func BenchmarkMergeInts(b *testing.B) {
	benchData := generateBenchmarkTestdata_Ints()
	runWithBenchData(b, benchData)
}

func BenchmarkMergeBlobs(b *testing.B) {
	benchData := generateBenchmarkTestdata_Blobs()
	runWithBenchData(b, benchData)
}
