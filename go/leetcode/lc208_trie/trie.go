// https://leetcode.com/problems/implement-trie-prefix-tree/

package main

import (
	"fmt"
	"math/bits"
	"slices"
)

type bitmask uint64

func (b bitmask) String() string {
	return fmt.Sprintf("%064b", uint64(b))
}

type Node struct {
	prefix string
	child  *Trie
}

// Trie is a radix trie with path compression
// Trie only supports alphanumeric keys (i.e. [a-zA-Z0-9]+)
type Trie struct {
	// nodeMask contains a bit per any possible starting char of the prefix
	// we expect only alphanumeric characters (there's 26 + 26 + 10 = 62 of them)
	// we have 64 bits total in [nodeMask]
	// (bit 63) is used for empty string
	// (bit 62) is reserved for now
	// (bits 0-61) are used for alphanumeric character prefixes
	nodeMask bitmask

	// child nodes of this trie, we do NOT allocate array of size for all possible prefixes
	// instead we allocate only the nodes that are present and address them via the nodeMask
	// see the [getInsertBitAndOffset] method
	nodes []Node
}

func commonPrefix(s1, s2 string) string {
	i := 0
	for ; i < len(s1); i++ {
		if i >= len(s2) {
			return s2
		}
		if s1[i] != s2[i] {
			return s1[:i]
		}
	}
	return s1[:i]
}

func Constructor() Trie {
	return Trie{}
}

// getInsertBitAndOffset returns (based on prefix)
// 1. position of the bit in this.nodeMask
// 2. offset in the nodes array to insert into
// 3. is the bit in this.nodeMask already set
func (this *Trie) getInsertBitAndOffset(prefix string) (bit int, offset int, is_set bool) {
	if prefix == "" {
		bit = 63
	} else {
		c := prefix[0]
		if '0' <= c && c <= '9' {
			bit = int(c - '0')
		} else if 'A' <= c && c <= 'Z' {
			bit = int(10 + c - 'A')
		} else if 'a' <= c && c <= 'z' {
			bit = int(10 + 26 + c - 'a')
		} else {
			panic("trie: unexpected character in key")
		}
	}

	// [bit] number of 1-s, i.e. for bit == 5 => 0000...00011111
	// the idea is to remove all bits higher than [bit],
	//  to count how many elements should be in front of this one
	mask := uint64((1 << bit) - 1)
	offset = bits.OnesCount64(uint64(this.nodeMask) & mask)
	return bit, offset, (this.nodeMask & (1 << bit)) != 0
}

func (this *Trie) getNodeForPrefix(prefix string) (node *Node) {
	_, offset, is_set := this.getInsertBitAndOffset(prefix)
	if is_set {
		return &this.nodes[offset]
	}
	return nil
}

func (this *Trie) insertNode(node Node) {
	bit, offset, is_set := this.getInsertBitAndOffset(node.prefix)
	if is_set {
		panic("insertNode: slot must be empty before insertion")
	}
	this.nodeMask |= (1 << bit)
	this.nodes = slices.Insert(this.nodes, offset, node)
}

func (this *Trie) removeNode(node *Node) {
	bit, offset, is_set := this.getInsertBitAndOffset(node.prefix)
	if !is_set {
		panic("insertNode: slot must be filled before removal")
	}
	this.nodeMask &= ^(1 << bit)
	this.nodes = slices.Delete(this.nodes, offset, offset+1)
}

func (this *Trie) Insert(word string) {
	// fmt.Printf("inserting %q", word)

	node := this.getNodeForPrefix(word)
	// if node != nil {
	// 	fmt.Printf(" -> node: { %q, %p }\n", node.prefix, node.child)
	// } else {
	// 	fmt.Printf(" -> [not set]\n")
	// }

	if node == nil {
		this.insertNode(Node{prefix: word, child: nil})
		return
	}

	prefix := commonPrefix(word, node.prefix)
	word_suffix := word[len(prefix):]
	node_suffix := node.prefix[len(prefix):]

	// this [node.prefix] is a full prefix of [word]
	// so it's likely we'd need to recurse into the child node to continue the search
	if node_suffix == "" {
		if word_suffix == "" { // [node.prefix] == [word]
			if node.child == nil { // leaf node, full match, already exists
				return
			}

			// non-leaf node, continue inserting, even though empty
			node.child.Insert(word_suffix)
		} else {
			// [word......................)
			//                [word_suffix)
			// [node.prefix...)

			// convert the node from leaf to branch, inserting empty string terminator
			if node.child == nil {
				node.child = &Trie{}
				node.child.insertNode(Node{prefix: "", child: nil})
			}

			node.child.Insert(word_suffix)
		}

		return
	}

	// now we can be in a combination of these orthogonal cases
	// 1. word_suffix is empty or not
	// 2. node is leaf or branch
	//
	//   [word....)
	//            [????)     <-- word_suffix is empty OR not empty
	//   [prefix..)
	//            [.......)  <-- node_suffix is NOT empty
	//   [node.prefix.....)
	//
	// Turns out we don't care about any of those, we can deal with them generically.

	// split the node into [prefix] -> [node_suffix] -> [preserve whatever child was there]
	// insert the remaining current [word_suffix] under the new [prefix] node as well
	node.prefix = prefix
	node.child = func() *Trie { // wrapped to preserve the current node.child
		new_child := &Trie{}
		new_child.insertNode(Node{prefix: node_suffix, child: node.child})
		new_child.insertNode(Node{prefix: word_suffix, child: nil})
		return new_child
	}()

}

func (this *Trie) RemovePrefix(word string) bool {
	node := this.getNodeForPrefix(word)
	if node == nil {
		return false
	}

	prefix := commonPrefix(word, node.prefix)
	word_suffix := word[len(prefix):]
	node_suffix := node.prefix[len(prefix):]

	if word_suffix == "" { // [word] is a prefix of [node.prefix]
		this.removeNode(node)
		return true
	}

	if node_suffix != "" { // suffixes have diverged
		return false
	}

	if node.child == nil { // we're at leaf, can't recurse, bail
		return false
	}

	removed_in_child := node.child.RemovePrefix(word_suffix)
	if removed_in_child == true {
		// compress the path back if possible
		if len(node.child.nodes) == 0 {
			panic("RemovePrefix: child trie can't become empty after prefix node removal")
		}
		if len(node.child.nodes) == 1 {
			child_node := node.child.nodes[0]
			node.prefix += child_node.prefix
			node.child = child_node.child
		}
	}
	return removed_in_child
}

func (this *Trie) Remove(word string) bool {
	node := this.getNodeForPrefix(word)
	if node == nil {
		return false
	}

	prefix := commonPrefix(word, node.prefix)
	word_suffix := word[len(prefix):]
	node_suffix := node.prefix[len(prefix):]

	if node_suffix != "" { // node is there, but it contains something else
		return false
	}

	if node.child == nil { // we're at leaf, can't recurse -> check for full match
		if word_suffix == "" {
			this.removeNode(node)
			return true
		}
	}

	removed_in_child := node.child.Remove(word_suffix)
	if removed_in_child == true {
		// compress the path back if possible
		if len(node.child.nodes) == 0 {
			panic("Remove: child trie can't become empty after node removal")
		}
		if len(node.child.nodes) == 1 {
			child_node := node.child.nodes[0]
			node.prefix += child_node.prefix
			node.child = child_node.child
		}
	}
	return removed_in_child
}

func (this *Trie) Search(word string) bool {
	node := this.getNodeForPrefix(word)
	if node == nil {
		return false
	}

	prefix := commonPrefix(word, node.prefix)
	word_suffix := word[len(prefix):]
	node_suffix := node.prefix[len(prefix):]

	if node_suffix != "" { // node is there, but it contains something else
		return false
	}

	if node.child == nil { // we're at leaf, can't recurse -> check for full match
		return word_suffix == "" // true if [word] == [node.prefix]
	}

	return node.child.Search(word_suffix)
}

func (this *Trie) StartsWith(word string) bool {
	node := this.getNodeForPrefix(word)
	if node == nil {
		return false
	}

	prefix := commonPrefix(word, node.prefix)
	word_suffix := word[len(prefix):]
	node_suffix := node.prefix[len(prefix):]

	if word_suffix == "" { // [word] is a prefix of [node.prefix]
		return true
	}

	if node_suffix != "" { // suffixes have diverged
		return false
	}

	if node.child == nil { // we're at leaf, can't recurse, bail
		return false
	}

	return node.child.StartsWith(word_suffix)
}
