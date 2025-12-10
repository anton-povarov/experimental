package main

import (
	tu "antoxa/leetcode/testutil"
	"testing"
)

var testData = []tu.TestData[[]string, []string]{
	{Input: []string{"z", "o"}, Expected: []string{"zo"}},
	{Input: []string{"hrn", "hrf", "er", "enn", "rfnn"}, Expected: []string{"hernf"}},
	{Input: []string{"wrt", "wrf", "er", "ett", "rftt"}, Expected: []string{"wertf"}},

	//
	// inconsistencies
	//

	// this one has multiple no-predecessor nodes ('w' and 'i' in this case)
	// so the function returns a separate head 'i' (it has no predecessors or successors)
	// w -> e -> r -> t -> f
	//      (no links)     i
	{Input: []string{"wrt", "wrf", "eri", "ett", "rftt"}, Expected: []string{"wertf", "i"}},

	// add a predecessor for 'i', but still no successors (so it's considered an "entry node")
	// this one is still an inconsistency, as there is no way to order 'f' and 'i' (common predecessor 't')
	// w -> e -> r -> t -> f
	//                 \-> i
	{Input: []string{"wrt", "wrf", "ert", "eri", "ett", "rftt"}, Expected: []string{"wertf", "i"}},

	// resolve the inconsistency, by providing an example where 'f' > 'i'
	// w -> e -> r -> t -> f ----> i
	//                 \--------/
	{Input: []string{"wrt", "wrf", "wri", "ert", "eri", "ett", "rftt"}, Expected: []string{"wertfi"}},
}

func TestConstructAlphabet(t *testing.T) {
	tu.RunTest(t, figureOutAlienAlphabet, testData)
}

func TestCheckDictionaryIsConsistent(t *testing.T) {
	// TODO: detect inconsistencies in the provided dictionary
	// example: loops in the graph
	// example: multiple entry (aka no-predecessor) nodes

	// tu.RunTest(t, figureOutAlienAlphabet, testData)
}
