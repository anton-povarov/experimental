// https://leetcode.com/problems/coin-change/

package main

import (
	tu "antoxa/leetcode/testutil"
	"slices"
	"testing"
)

func coinChange_recursive_memoize_step(cache map[int]int, coins []int, amount int) int {
	// fmt.Printf("coins: %v ~ amount: %d\n", coins, amount)

	if v, ok := cache[amount]; ok {
		return v
	}

	min_coins := -1

	for i := len(coins) - 1; i >= 0; i-- {
		coin := coins[i]

		if coin > amount {
			continue
		}

		n_coins := 0
		if amount%coin == 0 {
			n_coins = amount / coin
		} else {
			n_coins = coinChange_recursive_memoize_step(cache, coins, amount-coin)
			if n_coins == -1 {
				continue
			}
			n_coins += 1
		}

		if min_coins == -1 {
			min_coins = n_coins
		} else {
			min_coins = min(min_coins, n_coins)
		}
	}

	cache[amount] = min_coins
	return min_coins
}

func coinChange_recursive_memoize(coins []int, amount int) int {
	if amount == 0 {
		return 0
	}
	if len(coins) == 0 {
		return -1
	}

	slices.Sort(coins)
	cache := make(map[int]int) // amount -> result
	return coinChange_recursive_memoize_step(cache, coins, amount)
}

// DP implementation
// iteratively calculates the answer from 0 up to amount
// re-using already completed computations for [current_amount - current_coin]
// faster than memoizing for these reasons
//  1. fewer computations, this is liner, memo is exponential with branch cutting (not sure about the exact Big-O)
//  2. no recursion (no memory/cpu overhead to call extra functions)
//  3. flat array instead of a has table as "cache" of already computed values
func coinChange_dp_array(coins []int, amount int) int {
	if amount == 0 {
		return 0
	}

	dp := make([]int, amount+1)
	dp[0] = 0
	// no need to iniialize dp[1:], the loop below only looks backwards and will init everything

	for dp_amount := 1; dp_amount <= amount; dp_amount++ {
		dp_count := amount + 1
		for _, coin := range coins {
			if coin <= dp_amount {
				// don't even try to optimize with division, it's expensive
				// the iterative nature of the computation accounts for it much better
				//  as it's only a single step backwards + 1
				dp_count = min(dp_count, dp[dp_amount-coin]+1)
			}
		}
		dp[dp_amount] = dp_count
	}

	if dp[amount] <= amount {
		return dp[amount]
	}
	return -1
}

func coinChange(coins []int, amount int) int {
	// return coinChange_recursive_memoize(coins, amount)
	return coinChange_dp_array(coins, amount)
}

type InputData struct {
	coins  []int
	amount int
}

func testWrapper(test_func func([]int, int) int) func(d InputData) int {
	return func(d InputData) int {
		return test_func(d.coins, d.amount)
	}
}

var testData = []tu.TestData[InputData, int]{
	{Input: InputData{[]int{1, 2, 5}, 11}, Expected: 3},
	{Input: InputData{[]int{2}, 3}, Expected: -1},
	{Input: InputData{[]int{1}, 0}, Expected: 0},
	{Input: InputData{[]int{1}, 1}, Expected: 1},
	{Input: InputData{[]int{186, 419, 83, 408}, 6249}, Expected: 20},
}

func TestRecursive(t *testing.T) {
	tu.RunTest(t, testWrapper(coinChange_recursive_memoize), testData)
}

func TestDP(t *testing.T) {
	tu.RunTest(t, testWrapper(coinChange_dp_array), testData)
}
