//go:build verbose

package main

import (
	"testing"

	"github.com/k0kubun/pp"
)

func TestTrieVerbose(t *testing.T) {
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
