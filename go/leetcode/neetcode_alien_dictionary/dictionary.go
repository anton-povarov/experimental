// https://neetcode.io/problems/foreign-dictionary/
// https://leetcode.com/problems/alien-dictionary

// This implementation uses a symbol dependency graph + DFS to reconstruct the alphabet
//
// note that this algorithm is pretty basic and can't deal with dictionary inconsistencies very well
// the graph is also not free from double links or multiple paths to the same node
//  (take a look at the tests for more details)
//
// TODO: i feel this can be made significantly less brittle by
//  1. constructing an MST (Minimal Spanning Tree) before doing any searches
//  2. should explore the potential for other topological sorts in addition to DST

package main

import (
	"fmt"
	"maps"
	"strings"
)

func map_slice[Slice ~[]E, E any, R any](s Slice, apply func(E) R) (result []R) {
	result = make([]R, len(s))
	for i, elt := range s {
		result[i] = apply(elt)
	}
	return
}

type Symbol struct {
	Sym          byte
	predecessors []*Symbol
	successors   []*Symbol
}

func (s Symbol) String() string {
	pred_ids := map_slice(s.predecessors, func(sym *Symbol) string { return string(sym.Sym) })
	succ_ids := map_slice(s.successors, func(sym *Symbol) string { return string(sym.Sym) })
	return fmt.Sprintf("[sym %q, pred: %v, succ: %v ]", s.Sym, pred_ids, succ_ids)
}

type SymGraph struct {
	nodes map[byte]*Symbol
}

func (g *SymGraph) getOrCreateNode(sym byte) *Symbol {
	if n, ok := g.nodes[sym]; ok {
		return n
	}
	node := &Symbol{Sym: sym}
	g.nodes[sym] = node
	return node
}

func (g SymGraph) String() (res string) {
	for k, v := range g.nodes {
		res += fmt.Sprintf(" [%s]: %s\n", string(k), v)
	}
	return
}

func (g *SymGraph) step_reverseDFS(node *Symbol, visited map[*Symbol]struct{}, visitor func(*Symbol)) {
	if _, ok := visited[node]; ok {
		return
	}
	visited[node] = struct{}{}

	for _, pred := range node.predecessors {
		g.step_reverseDFS(pred, visited, visitor)
	}

	visitor(node)
}

func (g *SymGraph) reverseDFS() (res [][]*Symbol) {
	visited := map[*Symbol]struct{}{}

	exit_nodes := []*Symbol{}
	for s := range maps.Values(g.nodes) {
		if len(s.successors) == 0 {
			exit_nodes = append(exit_nodes, s)
		}
	}

	for _, node := range exit_nodes {
		local_res := make([]*Symbol, 0)
		g.step_reverseDFS(node, visited, func(s *Symbol) {
			local_res = append(local_res, s)
		})
		res = append(res, local_res)
	}
	return
}

func figureOutAlienAlphabet(dict []string) []string {
	if len(dict) == 0 {
		return nil
	}

	g := SymGraph{nodes: make(map[byte]*Symbol)}

	// this constructs a symbol precedence graph
	// scan all words in dictionary order and
	// 1. for each prefix of length `prefix_len` - group all the next letters per prefix
	//   i.e. produce a grouped map [prefix_len] -> [nth symbols of strings in dict]
	// 2. symbols in each group are in alphabetical order, add them to the graph
	// 3. make predecessor/successor links between consecutive nodes
	//   importantly - these links will be in dictionary order as well (?)
	for prefix_len := 0; ; /**/ prefix_len++ {
		prefixes := make(map[string][]byte)
		total_letters := 0 // total number of letters at this level
		for _, str := range dict {
			if prefix_len < len(str) {
				prefix := str[:prefix_len]
				symbol := str[prefix_len]
				prefixes[prefix] = append(prefixes[prefix], symbol)
				total_letters++
			}
		}
		// fmt.Printf("prefixes[%d]: %v\n", prefix_len, prefixes)

		for _, prefix_syms := range prefixes {
			for i, sym := range prefix_syms {
				successor_node := g.getOrCreateNode(sym)
				if i > 0 {
					predecessor_node := g.getOrCreateNode(prefix_syms[i-1])
					// create graph links, don't link to self
					// TODO: links are non-unique
					if successor_node != predecessor_node {
						successor_node.predecessors = append(successor_node.predecessors, predecessor_node)
						predecessor_node.successors = append(predecessor_node.successors, successor_node)
					}
				}
			}
		}

		if total_letters == 0 {
			break
		}
	}

	// fmt.Printf("graph:\n%s\n", g)
	dfs_nodes := g.reverseDFS()
	dfs_syms := map_slice(dfs_nodes, func(syms []*Symbol) string {
		inner_syms := map_slice(syms, func(s *Symbol) string { return string(s.Sym) })
		return strings.Join(inner_syms, "")
	})
	// fmt.Printf("dfs_nodes: %v\n", dfs_nodes_ids)

	return dfs_syms
}
