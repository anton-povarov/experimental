package main

import (
	"fmt"
	"math"
	"os"
	"runtime/debug"
	"strings"
	"testing"
)

func readFileWithCode(filename string) (string, error) {
	bytes, err := os.ReadFile(filename)
	return string(bytes), err
}

func BenchmarkTextSearch(b *testing.B) {
	filename := "test_file.txt"
	content, err := readFileWithCode(filename)
	if err != nil {
		b.Fatalf("could not read the input file %s", filename)
	}

	index := NewIndex()
	index.setFromLines(strings.Split(content, "\n"))

	queries := []string{
		"resul",  // many results
		"} else", // probably no results
		"error",  // not results (! weird)
		"err",    // a bit more results than "error"
		"index",
		"add result string to index and then do something with it", // long string, but no results
	}

	// Temporarily disable GC for the benchmark
	debug.SetGCPercent(-1)
	debug.SetMemoryLimit(math.MaxInt64)

	for _, q := range queries {
		b.Run(fmt.Sprintf("query %q", q), func(b *testing.B) {
			for b.Loop() {
				index.findSubstring(q)
			}
		})
	}
}
