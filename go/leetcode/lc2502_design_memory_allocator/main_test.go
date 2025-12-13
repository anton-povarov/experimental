// https://leetcode.com/problems/design-memory-allocator/

package main

import (
	tu "antoxa/leetcode/testutil"
	"fmt"
	"slices"
	"testing"
)

/**
 * Your Allocator object will be instantiated and called as such:
 * obj := Constructor(n);
 * param_1 := obj.Allocate(size,mID);
 * param_2 := obj.FreeMemory(mID);
 */

type allocRegion struct {
	offset int
	len    int
}

type Allocator struct {
	freelist  []allocRegion
	allocated map[int][]allocRegion
}

func Constructor(n int) Allocator {
	alloc := Allocator{
		freelist:  make([]allocRegion, 0, 1),
		allocated: make(map[int][]allocRegion),
	}
	alloc.freelist = append(alloc.freelist, allocRegion{offset: 0, len: n})
	return alloc
}

func (this *Allocator) Allocate(size int, mID int) int {
	// find the leftmost free region of sufficient size
	region_i := -1
	for i, reg := range this.freelist {
		if reg.len >= size {
			region_i = i
			break
		}
	}

	if region_i == -1 {
		return -1
	}

	if size == 0 {
		// not sure what to return here, but might need special handling
		// make it an error for now
		return -1
	}

	region := &this.freelist[region_i]

	newRegion := allocRegion{region.offset, size}
	this.allocated[mID] = append(this.allocated[mID], newRegion)

	region.offset += size
	region.len -= size // this can become 0, be careful storing empty regions

	return newRegion.offset
}

func (this *Allocator) FreeMemory(mID int) int {
	regionList, ok := this.allocated[mID]
	if !ok {
		return 0 // "return number of memory units freed"
	}

	delete(this.allocated, mID)

	slotsFreed := 0
	for _, reg := range regionList {
		slotsFreed += reg.len
		this.freelist = append(this.freelist, reg)
	}

	slices.SortFunc(this.freelist, func(l, r allocRegion) int {
		return l.offset - r.offset
	})

	// coalesce freelist regions and remove zero length ones
	out_i := 0
	for _, reg := range this.freelist[1:] {
		out := &this.freelist[out_i]
		if (out.offset + out.len) == reg.offset {
			out.len += reg.len
		} else {
			out_i++
			this.freelist[out_i] = reg
		}
	}
	this.freelist = this.freelist[:out_i+1]

	return slotsFreed
}

type testCall struct {
	allocID    int // if >= 0 - it's an alloc/free, if < 0, it's an init
	allocSlots int // if <= 0 then it's a free, if > 0 - it's an allocate
}

func testCall_init(slots int) testCall {
	return testCall{-10000, slots}
}

func testCall_alloc(slots, id int) testCall {
	return testCall{id, slots}
}
func testCall_free(id int) testCall {
	return testCall{id, -1}
}

func testAllocatorWithDebug(calls []testCall, expected []int) (result []int) {
	var alloc Allocator

	do_call := func(call testCall) (string, int) {
		if call.allocID < 0 {
			alloc = Constructor(calls[0].allocSlots)
			return fmt.Sprintf("alloc %d", calls[0].allocSlots), call.allocID
		} else {
			if call.allocSlots < 0 {
				return fmt.Sprintf("free %d", call.allocID), alloc.FreeMemory(call.allocID)
			} else {
				return fmt.Sprintf("alloc id: %d sz: %d", call.allocID, call.allocSlots), alloc.Allocate(call.allocSlots, call.allocID)
			}
		}
	}

	isOK := func(b bool) string {
		if b {
			return "OK"
		}
		return "ERROR"
	}

	for i, call := range calls {
		name, res := do_call(call)
		fmt.Printf("  [%s] %s -> %d, expected %d\n", isOK(res == expected[i]), name, res, expected[i])

		result = append(result, res)
	}
	return
}

func testAllocator(calls []testCall) (result []int) {
	var alloc Allocator

	do_call := func(call testCall) (string, int) {
		if call.allocID < 0 {
			alloc = Constructor(calls[0].allocSlots)
			return fmt.Sprintf("alloc %d", calls[0].allocSlots), call.allocID
		} else {
			if call.allocSlots < 0 {
				return fmt.Sprintf("free %d", call.allocID), alloc.FreeMemory(call.allocID)
			} else {
				return fmt.Sprintf("alloc id: %d sz: %d", call.allocID, call.allocSlots), alloc.Allocate(call.allocSlots, call.allocID)
			}
		}
	}

	for _, call := range calls {
		_, res := do_call(call)
		result = append(result, res)
	}
	return
}

var testData = []tu.TestData[[]testCall, []int]{
	{
		Input: []testCall{
			testCall_init(10),
			testCall_alloc(1, 1),
			testCall_alloc(1, 2),
			testCall_alloc(1, 3),
			testCall_free(2),
			testCall_alloc(3, 4),
			testCall_alloc(1, 1),
			testCall_alloc(1, 1),
			testCall_free(1),
			testCall_alloc(10, 2),
			testCall_free(7),
		},
		Expected: []int{-10000, 0, 1, 2, 1, 3, 1, 6, 3, -1, 0},
	},
	{
		Input: []testCall{
			testCall_init(50),
			testCall_alloc(12, 6),
			testCall_alloc(28, 16),
			testCall_alloc(17, 23),
			testCall_alloc(50, 23),
			testCall_free(6),
			testCall_free(10),
			testCall_free(10),
			testCall_alloc(16, 8),
			testCall_alloc(17, 41),
			testCall_alloc(44, 27),
			testCall_alloc(12, 45),
			testCall_free(33),
			testCall_free(8),
			testCall_free(16),
			testCall_free(23),
			testCall_free(23),
			testCall_free(23),
			testCall_free(29),
			testCall_alloc(38, 32),
			testCall_free(29),
			testCall_free(6),
			testCall_alloc(40, 11),
			testCall_free(16),
			testCall_alloc(22, 33),
			testCall_alloc(27, 5),
			testCall_free(3),
			testCall_free(10),
			testCall_free(29),
			testCall_alloc(16, 14),
			testCall_alloc(46, 47),
			testCall_alloc(48, 9),
			testCall_alloc(36, 17),
			testCall_free(33),
			testCall_alloc(14, 24),
			testCall_free(16),
			testCall_free(8),
			testCall_alloc(2, 50),
			testCall_alloc(31, 36),
			testCall_alloc(17, 45),
			testCall_alloc(46, 31),
			testCall_alloc(2, 6),
			testCall_alloc(16, 2),
			testCall_alloc(39, 30),
			testCall_free(33),
			testCall_free(45),
			testCall_free(30),
			testCall_free(27),
		},
		Expected: []int{-10000, 0, 12, -1, -1, 12, 0, 0, -1, -1, -1, 0, 0, 0, 28, 0, 0, 0, 0, 12, 0, 0, -1, 0, -1, -1, 0, 0, 0, -1, -1, -1, -1, 0, -1, 0, 0, -1, -1, -1, -1, -1, -1, -1, 0, 12, 0, 0},
	},
}

func map_slice[Slice ~[]E, E any, R any](s Slice, apply func(E) R) (result []R) {
	result = make([]R, len(s))
	for i, elt := range s {
		result[i] = apply(elt)
	}
	return
}

func TestAllocator(t *testing.T) {
	tu.RunTest(t, testAllocator, testData)
}

func TestAllocatorSpecial(t *testing.T) {
	tu.RunTest(t, func(calls []testCall) []int {
		expected := map_slice(testData, func(td tu.TestData[[]testCall, []int]) []int { return td.Expected })
		return testAllocatorWithDebug(calls, expected[1])
	}, testData[1:2])
}
