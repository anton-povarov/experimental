package main

import (
	"os"
	"reflect"
	"strings"
	"testing"
)

func TestSplitIntoNgrams(t *testing.T) {
	got := split_into_ngrams("hello")
	want := []ngram{ngram_from_str("hel"), ngram_from_str("ell"), ngram_from_str("llo")}

	if len(got) != len(want) {
		t.Fatalf("unexpected length: got %d want %d", len(got), len(want))
	}

	for i := range want {
		if got[i] != want[i] {
			t.Fatalf("mismatch at %d: got %q want %q", i, got[i].String(), want[i].String())
		}
	}
}

func findAllOffsets(s, sub string) []int {
	var offs []int
	start := 0
	for {
		idx := strings.Index(s[start:], sub)
		if idx < 0 {
			break
		}
		offs = append(offs, start+idx)
		start = start + idx + 1
		if start >= len(s) {
			break
		}
	}
	return offs
}

func TestSearchResultGroupByLines(t *testing.T) {
	sr := SearchResult{
		query: "unused",
		items: []SearchResultItem{
			{line: &IndexLine{lineNumber: 1}, offset: 10},
			{line: &IndexLine{lineNumber: 1}, offset: 20},
			{line: &IndexLine{lineNumber: 1}, offset: 193},
			{line: &IndexLine{lineNumber: 2}, offset: 555},
		},
	}

	expected := map[int][]int{
		1: {10, 20, 193},
		2: {555},
	}

	grouped := sr.GroupByLine()
	gotMap := make(map[int][]int)
	for _, lm := range grouped {
		gotMap[lm.line.lineNumber] = append(gotMap[lm.line.lineNumber], lm.offsets...)
	}

	if !reflect.DeepEqual(gotMap, expected) {
		t.Fatalf("grouping is incorrect\nexpected: %v\n     got: %v", expected, gotMap)
	}
}

func TestIndexFindSubstring_GroupByLine_PartsIterator(t *testing.T) {
	type InputsT struct {
		lines   []string
		queries []string
	}

	inputs := []InputsT{
		{
			lines: []string{
				"first entry here",
				"no match here",
				"another entry here",
				"entry at start, entry again",
			},
			queries: []string{"ent", "here"},
		},
		{
			lines: strings.Split(`
			type inputs struct {
				lines   []string
				queries []string
			}

			inp := []inputs{
				{
					lines: []string{
						"first entry here",
						"no match here",
		`, "\n"),
			queries: []string{
				"inp", "input", "strin", "huzzah", // these are ok
				// "in", // this will fail, as we don't support queries < 3 chars
			},
		},
		{
			lines: func() []string {
				c, _ := os.ReadFile("test_file.txt")
				return strings.Split(string(c), "\n")
			}(),
			queries: []string{"index", "resul", "error", "err", "unc", "a very long string that we can never find in the file"},
		},
	}

	for _, input := range inputs {
		idx := NewIndex()
		idx.setFromLines(input.lines)

		for _, query := range input.queries {
			groups := idx.findSubstring(query).GroupByLine()

			// transform from search into [line_no] -> []offsets
			gotMap := make(map[int][]int)
			for _, lm := range groups {
				gotMap[lm.line.lineNumber] = append(gotMap[lm.line.lineNumber], lm.offsets...)
			}

			// compute expected offsets using a plain search for each line
			wantMap := make(map[int][]int)
			for i, l := range input.lines {
				offs := findAllOffsets(l, query)
				if len(offs) > 0 {
					wantMap[i] = offs
				}
			}

			if !reflect.DeepEqual(gotMap, wantMap) {
				t.Fatalf("unexpected results: got %+v want %+v", gotMap, wantMap)
			}
		}
	}
}
