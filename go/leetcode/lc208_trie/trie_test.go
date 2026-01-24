// https://leetcode.com/problems/implement-trie-prefix-tree/

package main

import (
	"fmt"
	"testing"

	"github.com/k0kubun/pp"
)

func TestTrie(t *testing.T) {
	{
		trie := Constructor()
		trie.Insert("hello")
		trie.Insert("world")
		pp.Println(trie)
	}
	{
		trie := Constructor()
		trie.Insert("hello")
		trie.Insert("world")
		trie.Insert("hell")
		pp.Println(trie)
	}
	{
		trie := Constructor()
		trie.Insert("hello")
		trie.Insert("world")
		trie.Insert("hell")
		trie.Insert("hey")
		trie.Insert("hey")
		trie.Insert("hey")
		trie.Insert("imhavingalotoffun")
		trie.Insert("ibrahim")
		pp.Println(trie)
	}
}

func TestSearch(t *testing.T) {
	trie := Constructor()
	trie.Insert("hello")
	trie.Insert("world")
	trie.Insert("hell")
	trie.Insert("hey")
	trie.Insert("hey")
	trie.Insert("hey")
	pp.Println(trie)
	fmt.Printf("%q -> %v, expected: %v\n", "hell", trie.Search("hell"), true)
	fmt.Printf("%q -> %v, expected: %v\n", "hel", trie.Search("hel"), false)
	fmt.Printf("%q -> %v, expected: %v\n", "hellowa", trie.Search("hellowa"), false)
}

func TestStartsWith(t *testing.T) {
	trie := Constructor()
	trie.Insert("hello")
	trie.Insert("world")
	trie.Insert("hell")
	trie.Insert("hey")
	pp.Println(trie)
	fmt.Printf("%q -> %v, expected: %v\n", "hello", trie.StartsWith("hello"), true)
	fmt.Printf("%q -> %v, expected: %v\n", "hell", trie.StartsWith("hell"), true)
	fmt.Printf("%q -> %v, expected: %v\n", "hel", trie.StartsWith("hel"), true)
	fmt.Printf("%q -> %v, expected: %v\n", "hey", trie.StartsWith("hey"), true)
	fmt.Printf("%q -> %v, expected: %v\n", "he", trie.StartsWith("he"), true)
	fmt.Printf("%q -> %v, expected: %v\n", "her", trie.StartsWith("her"), false)
}

func TestRemovePrefix(t *testing.T) {
	{
		trie := Constructor()
		trie.Insert("hello")
		trie.Insert("world")
		trie.Insert("hell")
		trie.Insert("hey")
		trie.Insert("hey")
		trie.Insert("hey")
		trie.Insert("imhavingalotoffun")
		trie.Insert("ibrahim")
		pp.Printf("before\n%v\n", trie)

		trie.RemovePrefix("hel")
		pp.Printf("after\n%v\n", trie)
	}
}

func TestRemovePrefix2(t *testing.T) {
	{
		trie := Constructor()
		trie.Insert("hello")
		trie.Insert("world")
		trie.Insert("hell")
		trie.Insert("hey")
		trie.Insert("imhavingalotoffun")
		trie.Insert("ibrahim")
		pp.Printf("before\n%v\n", trie)

		// path compress from
		// "he" -> ["ll", "y"] -> [["o", ""], []]
		// to
		// "he" -> ["ll", "y"]
		trie.RemovePrefix("hello")
		pp.Printf("after\n%v\n", trie)
	}
}

func TestRemovePrefix3(t *testing.T) {
	trie := Constructor()
	trie.Insert("hello")
	trie.Insert("world")
	trie.Insert("hell")
	trie.Insert("hey")
	trie.Insert("imhavingalotoffun")
	trie.Insert("ibrahim")
	pp.Printf("before\n%v\n", trie)

	// removing hey, should path compress "hello" and "hell" into one node again
	// i.e. from
	// "he" -> ["ll", "y"] -> [["", "o"], [nonexistent, as "y" is a leaf]]
	// to
	// "hell" -> ["", "o"]
	trie.RemovePrefix("hey")
	pp.Printf("after\n%v\n", trie)
}

func TestRemovePrefix4(t *testing.T) {
	trie := Constructor()
	// trie.Insert("hello")
	// trie.Insert("world")
	trie.Insert("hey")
	trie.Insert("heya")
	pp.Printf("before\n%v\n", trie)

	trie.RemovePrefix("hey")
	pp.Printf("after\n%v\n", trie)
}

func TestRemove(t *testing.T) {
	trie := Constructor()
	trie.Insert("hello")
	trie.Insert("world")
	trie.Insert("hell")
	trie.Insert("hey")
	trie.Insert("heya")
	pp.Printf("before\n%v\n", trie)

	trie.Remove("hell")
	trie.Remove("hey")
	pp.Printf("after\n%v\n", trie)
}

func TestLeetcode1(t *testing.T) {
	// ["Trie","insert","search","search","startsWith","startsWith","insert","search","startsWith","insert","search","startsWith"]
	// [[],["ab"],["abc"],["ab"],["abc"],["ab"],["ab"],["abc"],["abc"],["abc"],["abc"],["abc"]]
	trie := Constructor()

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
