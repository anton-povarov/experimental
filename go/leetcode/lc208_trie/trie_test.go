// https://leetcode.com/problems/implement-trie-prefix-tree/

package main

import (
	tu "antoxa/leetcode/testutil"
	"reflect"
	"testing"

	"github.com/k0kubun/pp"
)

func makeTrie(keys []string) *Trie[int] {
	trie := Constructor[int]()
	trie.testutil_Insert(keys)
	return &trie
}

func (trie *Trie[V]) testutil_Insert(keys []string) *Trie[V] {
	for _, k := range keys {
		trie.Insert(k)
	}
	return trie
}

func (trie *Trie[V]) testutil_Remove(keys []string) *Trie[V] {
	for _, k := range keys {
		trie.Remove(k)
	}
	return trie
}

func (trie *Trie[V]) testutil_RemovePrefix(keys []string) *Trie[V] {
	for _, k := range keys {
		trie.RemovePrefix(k)
	}
	return trie
}

func mustDeepEqual[V any](t *testing.T, trie, expected *Trie[V]) {
	if reflect.DeepEqual(expected, trie) == false {
		t.Errorf("trie != expected")
		pp.Printf("trie\n%v\n", trie)
		pp.Printf("expected\n%v\n", expected)
		t.FailNow()
	}
}

func TestSearch(t *testing.T) {
	trie := makeTrie([]string{"hello", "world", "hell", "hey"})
	trie.Insert("hey")
	trie.Insert("hey") // must not fail multiple inserts of the same string

	testData := []tu.TestData[string, bool]{
		{Input: "hell", Expected: true},
		{Input: "hel", Expected: false},
		{Input: "hellowa", Expected: false},
	}
	tu.RunTest(t, func(s string) bool { return trie.Search(s) }, testData)
}

func TestStartsWith(t *testing.T) {
	trie := makeTrie([]string{"hello", "world", "hell", "hey", "imhavinglotsafun", "imhavingloz", "imho"})

	testData := []tu.TestData[string, bool]{
		{Input: "hello", Expected: true},
		{Input: "hell", Expected: true},
		{Input: "hel", Expected: true},
		{Input: "hey", Expected: true},
		{Input: "he", Expected: true},
		{Input: "her", Expected: false},
		{Input: "hellowa", Expected: false},
		{Input: "imhaving", Expected: true},
		{Input: "imhavinglot", Expected: true},
		{Input: "imhavinglog", Expected: false},
		{Input: "imhavinglozz", Expected: false},
		{Input: "imh", Expected: true},
	}
	tu.RunTest(t, func(s string) bool { return trie.StartsWith(s) }, testData)
}

func TestRemovePrefix(t *testing.T) {
	testData := []tu.TestData2[[]string, []string, *Trie[int]]{
		{
			Input1:   []string{"hello", "world", "hell", "hey", "hey", "hey", "imhavingalotoffun", "ibrahim"},
			Input2:   []string{"hel"},
			Expected: makeTrie([]string{"world", "hey", "imhavingalotoffun", "ibrahim"}),
		},
		//
		// path compress from
		// "he" -> ["ll", "y"] -> [["o", ""], []]
		// to
		// "he" -> ["ll", "y"]
		{
			Input1:   []string{"hello", "world", "hell", "hey", "hey", "hey", "imhavingalotoffun", "ibrahim"},
			Input2:   []string{"hello"},
			Expected: makeTrie([]string{"world", "hell", "hey", "imhavingalotoffun", "ibrahim"}),
		},
		//
		// removing "hey", should path compress "hello" and "hell" into one node again
		// i.e. from
		// "he" -> ["ll", "y"] -> [["", "o"], [nonexistent, as "y" is a leaf]]
		// to
		// "hell" -> ["", "o"]
		{
			Input1:   []string{"hello", "world", "hell", "hey", "hey", "hey", "imhavingalotoffun", "ibrahim"},
			Input2:   []string{"hey"},
			Expected: makeTrie([]string{"hello", "world", "hell", "imhavingalotoffun", "ibrahim"}),
		},
		// alternative path compression
		{
			Input1:   []string{"hello", "world", "hey", "heya"},
			Input2:   []string{"hey"},
			Expected: makeTrie([]string{"hello", "world"}),
		},
	}
	testFunc := func(ins, rem []string) *Trie[int] {
		trie := makeTrie(ins)
		trie.testutil_RemovePrefix(rem)
		return trie
	}
	tu.RunTest2(t, testFunc, testData)
}

func TestRemove(t *testing.T) {
	trie := makeTrie([]string{"hello", "world", "hell", "hey", "heya"})
	trie.testutil_Remove([]string{"hell", "hey"})

	expected := makeTrie([]string{"hello", "world", "heya"})
	mustDeepEqual(t, trie, expected)
}

func TestBinaryStrings(t *testing.T) {
	trie := makeTrie([]string{"hello", "world", "hello\x00", "hello\x00wa"})
	trie.Remove("hello\x00wa")
	trie.Remove("hello\x00wa") // remove twice, must not segfault

	expected := makeTrie([]string{"hello", "world", "hello\x00"})
	mustDeepEqual(t, trie, expected)
}

func TestLeetcode1(t *testing.T) {
	// ["Trie","insert","search","search","startsWith","startsWith","insert","search","startsWith","insert","search","startsWith"]
	// [[],["ab"],["abc"],["ab"],["abc"],["ab"],["ab"],["abc"],["abc"],["abc"],["abc"],["abc"]]
	trie := Constructor[int]()

	trie.Insert("ab")
	if trie.Search("abc") != false {
		t.Fatalf("search/abc")
	}
	if trie.Search("ab") != true {
		t.Fatalf("ab")
	}
	if trie.StartsWith("abc") != false {
		t.Fatalf("starts/abc")
	}
	if trie.StartsWith("ab") != true {
		t.Fatalf("starts/ab")
	}

	trie.Insert("ab")
	if trie.Search("abc") != false {
		t.Fatalf("search/abc")
	}
	if trie.StartsWith("abc") != false {
		t.Fatalf("starts/abc")
	}

	trie.Insert("abc")
	if trie.Search("abc") != true {
		t.Fatalf("search/abc")
	}
	if trie.StartsWith("abc") != true {
		t.Fatalf("starts/abc")
	}
}
