package main

import (
	"bufio"
	"os"
	"testing"
)

func readFileLines(filename string) ([]string, error) {
	f, err := os.Open(filename)
	if err != nil {
		return nil, err
	}
	defer f.Close()

	words := make([]string, 0, 1024)

	scan := bufio.NewScanner(f)
	for scan.Scan() {
		words = append(words, scan.Text())
	}

	return words, scan.Err()
}

func benchDatasetInserts(b *testing.B, filename string) {
	lines, err := readFileLines(filename)
	if err != nil {
		b.Fatalf("reading %s error: %v", filename, err)
	}

	// runtime.GC()
	// debug.SetGCPercent(-1)
	// debug.SetMemoryLimit(math.MaxInt64)

	b.Logf("%s contains %d lines", filename, len(lines))

	b.ResetTimer()
	for b.Loop() {
		trie := New[int]()
		for _, line := range lines {
			trie.Insert(line)
		}
	}
}

func BenchmarkDataset_Words(b *testing.B) {
	filename := "testdata/words.txt"
	benchDatasetInserts(b, filename)
}

func BenchmarkDataset_UUID(b *testing.B) {
	filename := "testdata/uuid.txt"
	benchDatasetInserts(b, filename)
}
