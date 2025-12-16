package main

import (
	"cmp"
	"fmt"
	"slices"
)

type HeapCompare[T any] func(T, T) bool

type Heap[T any] struct {
	items   []T
	compare HeapCompare[T]
}

func Heapify[T any, S ~[]T](heap S, compare func(T, T) bool) {
	n := len(heap)
	for i := n/2 - 1; i >= 0; i-- {
		down(heap, compare, i, n)
	}
}

func HeapPush[T any, S ~[]T](heap *S, compare func(T, T) bool, vals ...T) {
	n := len(*heap)
	(*heap) = append(*heap, vals...)

	if n == 0 {
		Heapify(*heap, compare)
	} else {
		for i := range len(vals) {
			up(*heap, compare, n+i-1)
		}
	}
}

func HeapPushV[T any, S ~[]T](heap *S, compare func(T, T) bool, val T) T {
	HeapPush(heap, compare, val)
	return val
}

func HeapPop[T any, S ~[]T](heap *S, compare func(T, T) bool) (ret T) {
	// 	n := h.Len() - 1
	n := len(*heap) - 1

	// 	h.Swap(0, n)
	(*heap)[0], (*heap)[n] = (*heap)[n], (*heap)[0]

	// 	down(h, 0, n)
	down(*heap, compare, 0, n)

	// 	return h.Pop()
	ret = (*heap)[n]
	(*heap) = (*heap)[:n]
	return
}

// HeapReplace pops the current top value and pushes a new value
// this is cheaper than HeapPop() + HeapPush()
// modeled after python's heapq.heapreplace()
func HeapReplaceTop[T any, S ~[]T](heap S, compare HeapCompare[T], val T) (ret T) {
	ret = heap[0]
	heap[0] = val

	down(heap, compare, 0, len(heap))
	return
}

func HeapFixTop[T any, S ~[]T](heap S, compare HeapCompare[T]) {
	down(heap, compare, 0, len(heap))
}

func up[T any, S ~[]T](heap S, compare HeapCompare[T], j int) {
	for {
		i := (j - 1) / 2 // parent
		if i == j || !compare(heap[j], heap[i]) {
			break
		}
		heap[i], heap[j] = heap[j], heap[i]
		j = i
	}
}

func down[T any, S ~[]T](heap S, compare HeapCompare[T], i0, n int) bool {
	i := i0
	for {
		j1 := 2*i + 1
		if j1 >= n || j1 < 0 { // j1 < 0 after int overflow
			break
		}
		j := j1 // left child
		if j2 := j1 + 1; j2 < n && compare(heap[j2], heap[j1]) {
			j = j2 // = 2*i + 2  // right child
		}
		if !compare(heap[j], heap[i]) {
			break
		}
		heap[i], heap[j] = heap[j], heap[i]
		i = j
	}
	return i > i0
}

// Heap[T]

// New creates new heap with a specificed comparator
func New[T any](compare func(T, T) bool) *Heap[T] {
	return &Heap[T]{items: nil, compare: compare}
}

// NewAcquire constructs a heap by "acquiring" provided `vals` slice and modiying it in place
func NewAcquire[T any, S ~[]T](vals S, compare func(T, T) bool) *Heap[T] {
	heap := &Heap[T]{items: vals, compare: compare}
	Heapify(heap.items, compare)
	return heap
}

// Make is a return-by-value version of New
func Make[T any](compare func(T, T) bool) Heap[T] {
	return Heap[T]{items: nil, compare: compare}
}

// MakeAcquire is a return-by-value version of NewAcquire
func MakeAcquire[T any, S ~[]T](vals S, compare func(T, T) bool) Heap[T] {
	heap := Heap[T]{items: vals, compare: compare}
	Heapify(heap.items, compare)
	return heap
}

// Push pushes (potentially multiple) values into the heap
// this is more efficient than calling Push() multiple times
func (h *Heap[T]) Push(vals ...T) {
	HeapPush(&h.items, h.compare, vals...)
}

func (h *Heap[T]) Pop() T {
	return HeapPop(&h.items, h.compare)
}

func (h *Heap[T]) ReplaceTop(val T) T {
	return HeapReplaceTop(h.items, h.compare, val)
}

func (h *Heap[T]) Empty() bool {
	return len(h.items) == 0
}

func (h *Heap[T]) Top() T {
	return h.items[0]
}

func (h *Heap[T]) Size() int {
	return len(h.items)
}

func verboseHeapify[T any, S ~[]T](heap S, compare func(T, T) bool) {
	fmt.Printf("verboseHeapify: %v", heap)
	Heapify(heap, compare)
	fmt.Printf(" -> %v\n", heap)
}

func heapPrintSorted[T any, S ~[]T](heap S, compare func(T, T) bool) {
	hcopy := make([]T, 0, len(heap))
	hcopy = append(hcopy, heap...)

	vals := make([]T, 0, len(hcopy))
	for len(hcopy) > 0 {
		vals = append(vals, HeapPop(&hcopy, compare))
	}
	fmt.Printf("sorted: %v\n", vals)
}

func main() {
	verboseHeapify([]int{1, 2, 3}, cmp.Less)

	{
		heap := New(cmp.Less[int])
		heap.Push(1, 2, 3, -1, 34, 12)

		fmt.Printf("int_v1\n")
		fmt.Printf("heap: %v\n", heap.items)
		heapPrintSorted(heap.items, heap.compare)
	}

	{
		heap := New(func(l, r [2]int) bool { return slices.Compare(l[:], r[:]) < 0 })
		heap.Push([][2]int{{1, 0}, {2, 0}, {3, 0}, {-1, 0}, {34, 0}, {12, 0}}...)

		fmt.Printf("[2]int\n")
		fmt.Printf("heap: %v\n", heap.items)
		heapPrintSorted(heap.items, heap.compare)
	}

	{
		type V struct {
			a int
			b int
		}

		compare := func(l, r V) bool { return cmp.Compare(l.a, r.a) > 0 }

		fmt.Printf("v1 (max_heap)\n")
		heap := []V{{1, 2}, {-1, 2}, {8, 8}, {3, 2}}
		verboseHeapify(heap, compare)

		HeapPush(&heap, compare, V{10, 3})
		fmt.Printf("pushed: %v\n", heap)

		heapPrintSorted(heap, compare)
	}

	{
		type V struct {
			a int
			b int
		}
		compare := func(l, r V) bool { return cmp.Compare(l.a, r.a) < 0 }

		fmt.Printf("v2 (min_heap)\n")

		heap := New(compare)
		fmt.Printf("heap: %v\n", heap.items)
		heap.Push([]V{{1, 2}, {-1, 3}, {15, 8}, {3, 3}}...)
		fmt.Printf("heap: %v\n", heap.items)
		fmt.Printf("pop: %v <- %v\n", heap.Pop(), heap.items)
		fmt.Printf("push: %v -> %v\n", HeapPushV(&heap.items, heap.compare, V{3, 4}), heap.items)

		v := V{5, 4}
		fmt.Printf("replace: %v -> %v -> %v\n", v, heap.items, heap.ReplaceTop(v))
		heapPrintSorted(heap.items, heap.compare)
	}

	{
		fmt.Printf("merge sorted arrays\n")
		inputs := [][]int{
			{1, 2, 3, 4, 5},
			{3, 5, 7, 8, 9},
			{-1},
			{0, 6, 9, 10},
		}
		result := MergeSortedArrays_Baseline(inputs, cmp.Less)
		fmt.Printf("merged: %v\n", result)
	}
}
