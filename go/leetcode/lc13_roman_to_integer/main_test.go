package main

import (
	"testing"

	tu "antoxa/leetcode/testutil"
)

func TestRomanToInt(t *testing.T) {
	data := []tu.TestData[string, int]{
		{Input: "IX", Expected: 9},
		{Input: "X", Expected: 10},
		{Input: "MCMXC", Expected: 1990},
		{Input: "LVII", Expected: 57},
		{Input: "MCMXCIV", Expected: 1994},
	}

	t.Run("forward", func(t *testing.T) { tu.RunTest(t, romanToInt_forward, data) })
	t.Run("backward", func(t *testing.T) { tu.RunTest(t, romanToInt_backward, data) })
}
