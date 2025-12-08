package main

import (
	"fmt"
	"iter"
	"slices"
	"strings"
)

// the idea is to search for substring in text, finding all occurrences
// interesting questions to the interviewer
//  1. should we expect strings shorter than 3 chars?
//  2. if the string is shorter - do we assume it's at the start or still want to find in the middle?
//     if any psition - then we'd need to generate all possible trigrams on the sides
//     if start only - we can prefix the string with some number of underscores
//  3. do we search for whitespace? if it's code - then probably yes
//  4. do we search for strings containing newlines? let's say - no

// v1 implementation does not store trigram offsets into the string
// therefore has to use quadratic sub-string (sub-trigram array really) search

const ngram_length = 3

// todo: maybe define trigram as [3]byte, instead of string

func make_trigrams(str string) (res []string) {
	// todo: maybe preprocess the string to remove punctuation between words
	//
	// str = fmt.Sprintf("__%s ", res)
	for i := 0; i < len(str)-ngram_length+1; i++ {
		res = append(res, str[i:i+ngram_length])
	}
	return res
}

// type NGram struct {
// 	ngram      string
// 	lineOffset uint
// }

type NGramIndexLine struct {
	lineNumber uint
	rawString  string
	trigrams   []string // order is important here, or we'd need to store offsets inside
}

type NGramIndex struct {
	lines []*NGramIndexLine            // lineNumber -> line
	tri   map[string][]*NGramIndexLine // inverted trigram -> []line
}

func NGramIndexNew() *NGramIndex {
	return &NGramIndex{tri: make(map[string][]*NGramIndexLine)}
}

func (index *NGramIndex) appendLine(line string) {
	// fmt.Printf("addLine[%d] -> %#v\n", lineNumber, ngrams)
	trigrams := make_trigrams(line)

	lineNumber := uint(len(index.lines))
	indexLine := &NGramIndexLine{lineNumber: lineNumber, rawString: line, trigrams: trigrams}
	index.lines = append(index.lines, indexLine)

	for _, tri := range trigrams {
		entry, ok := index.tri[tri]
		if !ok {
			entry = make([]*NGramIndexLine, 0, 1)
			entry = append(entry, indexLine)
		} else {
			// avoid adding the same line twice in case of repeated trigrams
			if entry[len(entry)-1] != indexLine {
				entry = append(entry, indexLine)
			}
		}
		index.tri[tri] = entry
	}
}

func (index *NGramIndex) injectLineBefore(beforeIndex int, line string) {
	if 0 > beforeIndex || beforeIndex > len(index.lines) {
		return
	}

	trigrams := make_trigrams(line)

	lineNumber := uint(beforeIndex)
	indexLine := &NGramIndexLine{lineNumber: lineNumber, rawString: line, trigrams: trigrams}
	index.lines = append(index.lines, nil) // note, this increments len(index.lines)

	// move elts forward and update line numbers
	for i := len(index.lines) - 1; i > beforeIndex; i-- {
		index.lines[i] = index.lines[i-1]
		index.lines[i].lineNumber = uint(i)
	}
	// insert the line where it's supposed to be
	index.lines[beforeIndex] = indexLine

	// trigrams, same as in appendLine()
	for _, tri := range trigrams {
		entry, ok := index.tri[tri]
		if !ok {
			entry = make([]*NGramIndexLine, 0, 1)
			entry = append(entry, indexLine)
		} else {
			// avoid adding the same line twice in case of repeated trigrams
			if entry[len(entry)-1] != indexLine {
				entry = append(entry, indexLine)
			}
		}
		index.tri[tri] = entry
	}
}

type NGramSearchResultLine struct {
	line    *NGramIndexLine
	offsets []uint
}

type NGramSearchResult struct {
	query string
	lines []NGramSearchResultLine
}

func (index *NGramIndex) findSubstring(substr string) NGramSearchResult {
	query_tri := make_trigrams(substr)

	// for _, indexLine := range index.lines {
	// 	fmt.Printf("indexLine = %#v\n", indexLine)
	// }

	result := NGramSearchResult{query: substr}
	if len(query_tri) == 0 {
		return result
	}

	index_entry := index.tri[query_tri[0]]
	// fmt.Printf("index_entry = %#v\n", index_entry)
	if index_entry == nil {
		return result
	}

	res_map := make(map[uint]*NGramSearchResultLine) // lineNumber -> line info

	// now in this entry we need to select only the lines that contain all trigrams sequentially
	// index_entry is an array of index lines
	for _, indexLine := range index_entry {
		// fmt.Printf("indexLine = %#v\n", indexLine)

		for i := 0; i < len(indexLine.trigrams)-len(query_tri)+1; i++ {
			// fmt.Printf("comparing: %#v %#v ", query_tri, line.trigrams[i:i+len(query_tri)])
			eq := slices.Equal(query_tri, indexLine.trigrams[i:i+len(query_tri)])
			// fmt.Printf(" -> %v\n", eq)
			if eq {
				// add line to result, merging offsets
				res_line, ok := res_map[indexLine.lineNumber]
				if !ok {
					res_line = &NGramSearchResultLine{line: indexLine, offsets: nil}
					res_map[indexLine.lineNumber] = res_line
				}
				res_line.offsets = append(res_line.offsets, uint(i))
			}
		}
	}
	// }

	for _, res_elt := range res_map {
		result.lines = append(result.lines, *res_elt)
	}
	return result
}

func (match *NGramSearchResultLine) partsIterator(query_str string) iter.Seq[string] {
	return func(yield func(string) bool) {
		start := uint(0)
		for _, offset := range match.offsets {
			if !yield(match.line.rawString[start:offset]) {
				return
			}

			start = offset
			offset += uint(len(query_str))
			if !yield(match.line.rawString[start:offset]) {
				return
			}

			start = offset
		}

		if !yield(match.line.rawString[start:]) {
			return
		}
	}
}

func map_slice[Slice ~[]E, E any, R any](s Slice, apply func(E) R) iter.Seq[R] {
	return func(yield func(R) bool) {
		for _, elt := range s {
			if !yield(apply(elt)) {
				return
			}
		}
	}
}

func map_iter[Seq iter.Seq[E], E any, R any](s Seq, apply func(E) R) iter.Seq[R] {
	return func(yield func(R) bool) {
		for elt := range s {
			if !yield(apply(elt)) {
				return
			}
		}
	}
}

// inefficient implementation with an itermediate slice
func strings_join_seq(s iter.Seq[string], sep string) string {
	return strings.Join(slices.Collect(s), sep)
}

func iter_enumerate[Seq iter.Seq[E], E any](s Seq) iter.Seq2[int, E] {
	return func(yield func(int, E) bool) {
		i := 0
		for elt := range s {
			if !yield(i, elt) {
				return
			}
			i++
		}
	}
}

func searchAndDisplayResults(index *NGramIndex, query_str string) {
	query_result := index.findSubstring(query_str)

	fmt.Printf("query: %s\n", query_str)
	for _, matchedLine := range slices.SortedFunc(
		slices.Values(query_result.lines), func(l, r NGramSearchResultLine) int {
			return int(l.line.lineNumber - r.line.lineNumber)
		}) {
		fmt.Printf(" line %d: %v\n", matchedLine.line.lineNumber, matchedLine.offsets)
		fmt.Printf("   %q\n", matchedLine.line.rawString)

		parts_it := matchedLine.partsIterator(query_str)
		fmt.Printf("   %v\n", strings_join_seq(map_iter(parts_it, func(s string) string {
			return fmt.Sprintf("[%q]", s)
		}), " -> "))
	}
	fmt.Printf("\n")
}

func main() {
	// fmt.Printf("trigrams = %#v\n", make_trigrams("hey, i'm a string"))

	// take some text, split it by newlines (we don't expect to have search queries with newlines in them)
	text := `
func make_trigrams(str string) (result []string) {
	// todo: maybe preprocess the string to remove punctuation between words
	//
	// str = fmt.Sprintf("__%s ", result)
	for i := 0; i < len(str)-ngram_length+1; i++ {
		result = append(result, str[i:i+ngram_length])
	}
	return result
}
`
	index := NGramIndexNew()
	for line := range strings.SplitSeq(text, "\n") {
		if len(line) > 0 {
			index.appendLine(line)
		}
	}
	searchAndDisplayResults(index, "result")
	searchAndDisplayResults(index, "{") // no results

	index.injectLineBefore(0, "// this comment should be in the final result")
	searchAndDisplayResults(index, "result")

	index.injectLineBefore(10, "// also in the final result")
	searchAndDisplayResults(index, "result")
}
