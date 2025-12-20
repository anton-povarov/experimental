package main

import (
	"math"
	"math/bits"
	"testing"

	tu "antoxa/leetcode/testutil"
)

func reverse_int32(xi int) (ri int) {
	x := int32(xi)
	r := int32(ri)
	if x == math.MinInt32 {
		return 0
	}

	neg := x < 0
	xx := uint32(x)
	if x < 0 {
		xx = uint32(-x)
	}

	for xx != 0 {
		quo, rem := bits.Div32(0, xx, 10)
		// fmt.Printf("%d -> %d,%d", xx, quo, rem)

		if ((math.MaxInt32 - int32(rem)) / 10) < r { // will overflow
			return 0
		}
		r = int32(r*10 + int32(rem))

		xx = quo
		// fmt.Printf(" -> [max: %d] r: %b, xx: %d\n", math.MaxInt32/10-int32(rem), r, xx)
	}

	if neg {
		r = -r
	}
	return int(r)
}

var testData = []tu.TestData[int, int]{
	{Input: 123, Expected: 321},
	{Input: -123, Expected: -321},
	{Input: 0, Expected: 0},
	{Input: math.MinInt32, Expected: 0},
	{Input: 1534236469, Expected: 0}, // 9646324351, overflows int32
	{Input: 1463847412, Expected: 2147483641},
}

func TestReverse(t *testing.T) {
	tu.RunTest(t, reverse_int32, testData)
}
