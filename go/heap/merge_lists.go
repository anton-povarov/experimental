package main

import (
	"unsafe"
)

func MergeSortedArrays[T any, Arr ~[]T, Arrs ~[]Arr, F ~func(T, T) bool](
	inputs Arrs,
	compare F,
) []T {
	return MergeSortedArrays_Baseline(inputs, compare)
}

func MergeSortedArrays_Baseline[T any, Arr ~[]T, Arrs ~[]Arr, F ~func(T, T) bool](
	inputs Arrs,
	compare F,
) []T {
	type head struct {
		input_idx   int
		list_offset int
	}

	// compare by the values in respective lists
	value_compare := func(l, r head) bool {
		return compare(inputs[l.input_idx][l.list_offset], inputs[r.input_idx][r.list_offset])
	}

	total_len := 0
	heads := make([]head, 0, len(inputs))
	for i, input := range inputs {
		total_len += len(input)
		if len(input) > 0 {
			heads = append(heads, head{i, 0})
		}
	}

	result := make([]T, 0, total_len)

	heap := MakeAcquire(heads, value_compare)
	for !heap.Empty() {
		top_head := heap.Top() // copies, maybe not ideal
		top_list := inputs[top_head.input_idx]
		top_value := top_list[top_head.list_offset]
		result = append(result, top_value)

		if len(top_list) > top_head.list_offset+1 {
			// this constructs a new head value, maybe more efficient to change in-place and then fix?
			heap.ReplaceTop(head{top_head.input_idx, top_head.list_offset + 1})
		} else {
			heap.Pop()
		}
	}

	return result
}

func MergeSortedArrays_ValueCopy[T any, Arr ~[]T, Arrs ~[]Arr, F ~func(T, T) bool](
	inputs Arrs,
	compare F,
) []T {
	type head struct {
		cached_value T
		input_idx    int32
		input_pos    int32
	}

	// compare by the values in respective lists
	value_compare := func(l, r head) bool {
		return compare(l.cached_value, r.cached_value)
	}

	total_len := 0
	heads := make([]head, 0, len(inputs))
	for i, input := range inputs {
		input_len := len(input)
		total_len += input_len
		if input_len > 0 {
			heads = append(heads, head{input[0], int32(i), 0})
		}
	}

	result := make([]T, 0, total_len)

	Heapify(heads, value_compare)
	for len(heads) != 0 {
		top_head := &heads[0]
		result = append(result, top_head.cached_value)

		top_head.input_pos++
		if top_head.input_pos == int32(len(inputs[top_head.input_idx])) {
			HeapPop(&heads, value_compare)
		} else {
			top_head.cached_value = inputs[top_head.input_idx][top_head.input_pos]
			HeapFixTop(heads, value_compare)
		}
	}

	return result
}

func MergeSortedArrays_ValueCachedPtr[T any, Arr ~[]T, Arrs ~[]Arr, F ~func(T, T) bool](
	inputs Arrs,
	compare F,
) []T {
	type head struct {
		input_val   *T
		input_idx   int
		list_offset int
	}

	value_compare := func(l, r head) bool {
		return compare(*l.input_val, *r.input_val)
	}

	total_len := 0
	heads := make([]head, 0, len(inputs))
	for i, input := range inputs {
		total_len += len(input)
		if len(input) > 0 {
			heads = append(heads, head{&input[0], i, 0})
		}
	}

	result := make([]T, 0, total_len)

	heap := MakeAcquire(heads, value_compare)
	for !heap.Empty() {
		top_head := heap.Top() // copies, maybe not ideal
		top_list := inputs[top_head.input_idx]
		top_value := top_list[top_head.list_offset]
		result = append(result, top_value)

		if len(top_list) > top_head.list_offset+1 {
			top_head.list_offset++
			// this constructs a new head value, maybe more efficient to change in-place and then fix?
			heap.ReplaceTop(head{
				&top_list[top_head.list_offset],
				top_head.input_idx,
				top_head.list_offset,
			})
		} else {
			heap.Pop()
		}
	}

	return result
}

func MergeSortedArrays_ValuePtr[T any, Arr ~[]T, Arrs ~[]Arr, F ~func(T, T) bool](
	inputs Arrs,
	compare F,
) []T {

	type head struct {
		input_val *T
		input_end *T
	}

	value_compare := func(l, r head) bool {
		return compare(*l.input_val, *r.input_val)
	}

	total_len := 0
	heads := make([]head, 0, len(inputs))
	for _, input := range inputs {
		input_len := len(input)
		total_len += input_len
		if input_len > 0 {
			heads = append(heads, head{&input[0], &input[input_len-1]})
		}
	}

	result := make([]T, 0, total_len)

	Heapify(heads, value_compare)
	for len(heads) != 0 {
		top_head := &heads[0]
		top_value_ptr := top_head.input_val
		result = append(result, *top_value_ptr)

		if top_value_ptr == top_head.input_end {
			HeapPop(&heads, value_compare)
		} else {
			top_head.input_val = (*T)(unsafe.Pointer(uintptr(unsafe.Pointer(top_value_ptr)) + unsafe.Sizeof(*top_value_ptr)))
			HeapFixTop(heads, value_compare)
		}
	}

	return result
}

func MergeSortedArrays_Adaptive[T any, Arr ~[]T, Arrs ~[]Arr, F ~func(T, T) bool](
	inputs Arrs,
	compare F,
) []T {
	var dummy T
	if unsafe.Sizeof(dummy) < 4*unsafe.Sizeof(uint64(0)) {
		return MergeSortedArrays_ValueCopy(inputs, compare)
	} else {
		return MergeSortedArrays_ValuePtr(inputs, compare)
	}
}
