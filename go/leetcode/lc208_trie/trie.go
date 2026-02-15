// https://leetcode.com/problems/implement-trie-prefix-tree/

package main

import (
	"fmt"
	"math/bits"
	"slices"
	"strings"
)

const bitmask_size = 256
const bitmask_block_size = 64
const bitmask_blocks_count = bitmask_size / bitmask_block_size

type bitmask struct {
	b [bitmask_blocks_count]uint64
}

func (b bitmask) String() string {
	sb := strings.Builder{}
	for i := range bitmask_blocks_count {
		if i != 0 {
			sb.WriteByte(' ')
		}
		fmt.Fprintf(&sb, "%#x", b.b[i])
	}
	return sb.String()
}

func (b *bitmask) check_bit_is_in_range(bit int, name string) {
	if 0 > bit || bit >= bitmask_size {
		panic(fmt.Sprintf("bitmask::%s bit (=%d) must be in [0, %d)", name, bit, bitmask_size))
	}
}

func (b *bitmask) Set(bit int) *bitmask {
	b.check_bit_is_in_range(bit, "Set")
	b.b[bit/bitmask_block_size] |= uint64(1 << (bit % bitmask_block_size))
	return b
}

func (b *bitmask) Reset(bit int) *bitmask {
	b.check_bit_is_in_range(bit, "Reset")
	b.b[bit/bitmask_block_size] &= ^uint64(1 << (bit % bitmask_block_size))
	return b
}

func (b *bitmask) IsSet(bit int) bool {
	b.check_bit_is_in_range(bit, "IsSet")
	return (b.b[bit/bitmask_block_size] & uint64(1<<(bit%bitmask_block_size))) != 0
}

func (b *bitmask) CountOnesBelowBit(bit int) (n_bits_set int, this_bit_set bool) {
	b.check_bit_is_in_range(bit, "CountOnesBelowBit")

	bit_chunk := bit / bitmask_block_size
	bit_offset := bit % bitmask_block_size

	for i := range bit_chunk {
		n_bits_set += bits.OnesCount64(b.b[i])
	}

	mask := uint64((1 << bit_offset) - 1)
	n_bits_set += bits.OnesCount64(b.b[bit_chunk] & mask)
	this_bit_set = (b.b[bit_chunk] & (1 << bit_offset)) != 0
	return
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

func trieKeysConcat(l, r string) string {
	return l + r
}

type trieNode[V any] struct {
	prefix string
	child  *Trie[V]
}

// Trie is a radix trie with path compression
type Trie[V any] struct {
	// nodeMask - a bitmask of nodes present in the [nodes] array
	// this allows to avoid storing child nodes (or pointers to them) unless they're actually used
	// the tradeoff is that when nodes are inserted/removed - all nodes must be shifted in the [nodes] array
	// at high node density, this would probably perform worse than just storing all nodes directly
	// Trie stores empty prefixes as nodes, so:
	//  if [node.prefix] == "" -> no bits are set, node will always be at the end of [nodes]
	nodeMask bitmask

	// child nodes of this trie, we do NOT allocate array of size for all possible prefixes
	// instead we allocate only the nodes that are present and address them via the nodeMask
	// see the [getInsertBitAndOffset] method
	nodes []trieNode[V]
}

func New[V any]() *Trie[V] {
	return &Trie[V]{}
}

func Constructor[V any]() Trie[V] {
	return Trie[V]{}
}

// getInsertBitAndOffset returns (based on prefix)
// 1. position of the bit in this.nodeMask
// 2. offset in the nodes array to insert into
// 3. is the bit in this.nodeMask already set
func (this *Trie[V]) getInsertBitAndOffset(prefix string) (bit int, offset int, is_set bool) {
	if len(prefix) == 0 {
		panic("getInsertBitAndOffset called for empty prefix")
	} else {
		bit = int(prefix[0])
		// c := prefix[0]
		// if '0' <= c && c <= '9' {
		// 	bit = int(c - '0')
		// } else if 'A' <= c && c <= 'Z' {
		// 	bit = int(10 + c - 'A')
		// } else if 'a' <= c && c <= 'z' {
		// 	bit = int(10 + 26 + c - 'a')
		// } else {
		// 	panic("trie: unexpected character in key")
		// }
	}

	offset, is_set = this.nodeMask.CountOnesBelowBit(bit)
	return bit, offset, is_set
}

func (this *Trie[V]) getNodeForPrefix(prefix string) *trieNode[V] {
	if len(prefix) == 0 {
		if len(this.nodes) > 0 {
			node := &this.nodes[len(this.nodes)-1]
			if len(node.prefix) == 0 {
				return node
			}
		}
		return nil
	}

	_, offset, is_set := this.getInsertBitAndOffset(prefix)
	if is_set {
		return &this.nodes[offset]
	}
	return nil
}

func (this *Trie[V]) insertNode(node trieNode[V]) {
	if len(node.prefix) == 0 {
		if len(this.nodes) > 0 {
			if len(this.nodes[len(this.nodes)-1].prefix) == 0 {
				panic("insertNode: empty-string slot must not be present before insertion")
			}
		}
		this.nodes = append(this.nodes, node)
		return
	}

	if len(this.nodes) == 0 {
		bit := int(node.prefix[0])
		this.nodeMask.Set(bit)
		this.nodes = append(this.nodes, node)
		return
	}

	bit, offset, is_set := this.getInsertBitAndOffset(node.prefix)
	if is_set {
		panic("insertNode: slot must be empty before insertion")
	}
	this.nodeMask.Set(bit)
	this.nodes = slices.Insert(this.nodes, offset, node)
}

func (this *Trie[V]) removeNode(node *trieNode[V]) {
	if len(node.prefix) == 0 {
		if len(this.nodes) > 0 {
			if len(this.nodes[len(this.nodes)-1].prefix) != 0 {
				panic("removeNode: removing empty-string node, but last node is not empty-string")
			}
		}
		this.nodes = this.nodes[:len(this.nodes)-1]
		return
	}

	bit, offset, is_set := this.getInsertBitAndOffset(node.prefix)
	if !is_set {
		panic("removeNode: slot must be filled before removal")
	}
	this.nodeMask.Reset(bit)
	this.nodes = slices.Delete(this.nodes, offset, offset+1)
}

func (this *Trie[V]) Insert(word string) {

	for {
		node := this.getNodeForPrefix(word)
		if node == nil {
			this.insertNode(trieNode[V]{prefix: word, child: nil})
			return
		}

		prefix := commonPrefix(word, node.prefix)
		word_suffix := word[len(prefix):]
		node_suffix := node.prefix[len(prefix):]

		// this [node.prefix] is a full prefix of [word]
		// so it's likely we'd need to recurse into the child node to continue the search
		if len(node_suffix) == 0 {
			if len(word_suffix) == 0 { // [node.prefix] == [word]
				if node.child == nil { // leaf node, full match, already exists
					return
				}

				// non-leaf node, continue inserting, even though empty
				// node.child.Insert(word_suffix)
			} else {
				// [word......................)
				//                [word_suffix)
				// [node.prefix...)

				// convert the node from leaf to branch, inserting empty string terminator
				if node.child == nil {
					node.child = &Trie[V]{}
					node.child.insertNode(trieNode[V]{prefix: "", child: nil})
				}

				// node.child.Insert(word_suffix)
			}

			// ITERATIVE part
			word = word_suffix
			this = node.child
			continue

			// return
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
		node.child = func() *Trie[V] { // wrapped to preserve the current node.child
			new_child := &Trie[V]{}
			new_child.insertNode(trieNode[V]{prefix: node_suffix, child: node.child})
			new_child.insertNode(trieNode[V]{prefix: word_suffix, child: nil})
			return new_child
		}()
		return
	}
}

func (this *Trie[V]) RemovePrefix(word string) bool {
	node := this.getNodeForPrefix(word)
	if node == nil {
		return false
	}

	prefix := commonPrefix(word, node.prefix)
	word_suffix := word[len(prefix):]
	node_suffix := node.prefix[len(prefix):]

	if len(word_suffix) == 0 { // [word] is a prefix of [node.prefix]
		this.removeNode(node)
		return true
	}

	if len(node_suffix) != 0 { // suffixes have diverged
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
			node.prefix = trieKeysConcat(node.prefix, child_node.prefix)
			node.child = child_node.child
		}
	}
	return removed_in_child
}

func (this *Trie[V]) Remove(word string) bool {
	node := this.getNodeForPrefix(word)
	if node == nil {
		return false
	}

	prefix := commonPrefix(word, node.prefix)
	word_suffix := word[len(prefix):]
	node_suffix := node.prefix[len(prefix):]

	if len(node_suffix) != 0 { // node is there, but it contains something else
		return false
	}

	if node.child == nil { // we're at leaf, can't recurse -> check for full match
		if len(word_suffix) == 0 {
			this.removeNode(node)
			return true
		}
		return false
	}

	removed_in_child := node.child.Remove(word_suffix)
	if removed_in_child == true {
		// compress the path back if possible
		if len(node.child.nodes) == 0 {
			panic("Remove: child trie can't become empty after node removal")
		}
		if len(node.child.nodes) == 1 {
			child_node := node.child.nodes[0]
			node.prefix = trieKeysConcat(node.prefix, child_node.prefix)
			node.child = child_node.child
		}
	}
	return removed_in_child
}

func (this *Trie[V]) Search(word string) bool {
	node := this.getNodeForPrefix(word)
	if node == nil {
		return false
	}

	prefix := commonPrefix(word, node.prefix)
	word_suffix := word[len(prefix):]
	node_suffix := node.prefix[len(prefix):]

	if len(node_suffix) != 0 { // node is there, but it contains something else
		return false
	}

	if node.child == nil { // we're at leaf, can't recurse -> check for full match
		return len(word_suffix) == 0 // true if [word] == [node.prefix]
	}

	return node.child.Search(word_suffix)
}

func (this *Trie[V]) StartsWith(word string) bool {
	node := this.getNodeForPrefix(word)
	if node == nil {
		return false
	}

	prefix := commonPrefix(word, node.prefix)
	word_suffix := word[len(prefix):]
	node_suffix := node.prefix[len(prefix):]

	if len(word_suffix) == 0 { // [word] is a prefix of [node.prefix]
		return true
	}

	if len(node_suffix) != 0 { // suffixes have diverged
		return false
	}

	if node.child == nil { // we're at leaf, can't recurse, bail
		return false
	}

	return node.child.StartsWith(word_suffix)
}
