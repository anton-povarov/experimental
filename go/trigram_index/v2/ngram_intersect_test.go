package main

import (
	"fmt"
	"math/rand"
	"slices"
	"testing"
)

type NgramMultiset struct {
	total int
	m     map[ngram]int
}

func ngrams_as_multiset_2(ngrams []ngram) NgramMultiset {
	result := NgramMultiset{total: 0, m: make(NgramSet, len(ngrams))}
	for _, ng := range ngrams {
		result.m[ng] = result.m[ng] + 1
		result.total += 1
	}
	return result
}

func ngram_multiset_2_intersect_and_union_size(l, r NgramMultiset) (int, int) {
	intersect_total := 0
	for ngram, cnt := range l.m {
		intersect_total += min(cnt, r.m[ngram])
	}

	return intersect_total, l.total + r.total
}

type NgramIntSet struct {
	total int
	m     map[NgramAsInt]int
}

func ngrams_as_intset(ngrams []ngram) NgramIntSet {
	result := NgramIntSet{total: 0, m: make(map[NgramAsInt]int, len(ngrams))}
	for _, ng := range ngrams {
		g := ngram_to_int(ng)
		result.m[g] = result.m[g] + 1
		result.total += 1
	}
	return result
}

func ngram_intset_intersect_and_union_size(l, r NgramIntSet) (int, int) {
	intersect_total := 0
	for ngram, cnt := range l.m {
		intersect_total += min(cnt, r.m[ngram])
	}

	return intersect_total, l.total + r.total
}

// uint32 slices

type NgramAsInt uint32
type NgramInts []NgramAsInt

func ngram_to_int(ng ngram) NgramAsInt {
	return NgramAsInt((NgramAsInt(ng[0]) << 16) | (NgramAsInt(ng[1]) << 8) | NgramAsInt(ng[2]))
}

func ngrams_as_ints(ngrams []ngram) NgramInts {
	res := make([]NgramAsInt, len(ngrams))
	for i, ngram := range ngrams {
		res[i] = ngram_to_int(ngram)
	}
	return res
}

func ngram_ints_intersect_and_union_size(l, r NgramInts) (int, int) {
	l_len := len(l)
	r_len := len(r)
	i := 0
	j := 0

	n_intersect := 0

	for (i < l_len) && (j < r_len) {
		if l[i] == r[i] {
			val := l[i]

			// count equal elts for l
			end_i := i + 1
			for (end_i < l_len) && (l[end_i] == val) {
				end_i++
			}

			// count equal elts for r
			end_j := j + 1
			for (end_j < r_len) && (val == r[end_j]) {
				end_j++
			}

			n_intersect += min(end_i-i, end_j-j)
			i = end_i
			j = end_j
		} else if l[i] < r[i] {
			i++
		} else {
			j++
		}
	}

	return n_intersect, len(l) + len(r)
}

// slices

func ngram_slice_intersect_and_union_size_less_slice(l, r NgramSlice) (int, int) {
	l_len := len(l)
	r_len := len(r)
	i := 0
	j := 0

	n_intersect := 0

	for (i < l_len) && (j < r_len) {
		cmp := slices.Compare(l[i][:], r[j][:])

		switch {
		case cmp < 0:
			i++
		case cmp > 0:
			j++
		default: // equal
			val := l[i][:]

			// count equal elts for l
			end_i := i + 1
			for (end_i < l_len) && slices.Compare(l[end_i][:], val) == 0 {
				end_i++
			}

			// count equal elts for r
			end_j := j + 1
			for (end_j < r_len) && slices.Compare(val, r[end_j][:]) == 0 {
				end_j++
			}

			n_intersect += min(end_i-i, end_j-j)
			i = end_i
			j = end_j
		}
	}

	return n_intersect, len(l) + len(r)
}

func ngram_slice_intersect_and_union_size_less_bin(l, r NgramSlice) (int, int) {
	l_len := len(l)
	r_len := len(r)
	i := 0
	j := 0

	n_intersect := 0

	for (i < l_len) && (j < r_len) {
		cmp := ngram_less(l[i], r[j])

		switch {
		case cmp < 0:
			i++
		case cmp > 0:
			j++
		default: // equal
			val := l[i]

			// count equal elts for l
			end_i := i + 1
			for (end_i < l_len) && ngram_less(l[end_i], val) == 0 {
				end_i++
			}

			// count equal elts for r
			end_j := j + 1
			for (end_j < r_len) && ngram_less(val, r[end_j]) == 0 {
				end_j++
			}

			n_intersect += min(end_i-i, end_j-j)
			i = end_i
			j = end_j
		}
	}

	return n_intersect, len(l) + len(r)
}

func makeRandomNgramSlice(size int) NgramSlice {
	ngrams := NgramSlice{}
	for range size {
		g := ngram{}
		rnd := rand.Intn(1 << 24)
		g[0] = byte(rnd >> 16)
		g[1] = byte(rnd >> 8)
		g[2] = byte(rnd >> 0)
		ngrams = append(ngrams, g)
	}
	return ngrams_as_slice(ngrams)
}

func makeRandomQueryFromSlice(ngrams NgramSlice, size int) (res NgramSlice) {
	randomNgrams := []ngram{
		ngram_from_str("abc"),
		ngram_from_str("[i]"),
		ngram_from_str("(st"),
		ngram_from_str("fun"),
		ngram_from_str("unc"),
	}

	// make X% of ngrams intersect and other (100-X)% - just random from our set
	const X = float32(0.4)
	n_intersecting_ngrams := min(int(float32(size)*X), 1)

	for range n_intersecting_ngrams {
		res = append(res, ngrams[rand.Intn(len(ngrams))])
	}

	for range size - n_intersecting_ngrams {
		res = append(res, randomNgrams[rand.Intn(len(randomNgrams))])
	}
	return
}

func BenchmarkCompareNgrams(b *testing.B) {
	line_length := []int{20, 40, 80, 100}
	line_ngrams := []NgramSlice{}
	query_ngrams := []NgramSlice{}

	for i, ln := range line_length {
		line_ngrams = append(line_ngrams, makeRandomNgramSlice(ln))
		query_ngrams = append(query_ngrams, makeRandomQueryFromSlice(line_ngrams[i], 5))
	}

	for i, ln := range line_length {
		b.Run(fmt.Sprintf("hash_%d", ln), func(b *testing.B) {
			line_set := ngrams_as_multiset_2(line_ngrams[i])
			query_set := ngrams_as_multiset_2(query_ngrams[i])

			for b.Loop() {
				_, _ = ngram_multiset_2_intersect_and_union_size(query_set, line_set)
			}
		})
	}
	for i, ln := range line_length {
		b.Run(fmt.Sprintf("intset_%d", ln), func(b *testing.B) {
			line_set := ngrams_as_intset(line_ngrams[i])
			query_set := ngrams_as_intset(query_ngrams[i])

			for b.Loop() {
				_, _ = ngram_intset_intersect_and_union_size(query_set, line_set)
			}
		})
	}
	for i, ln := range line_length {
		b.Run(fmt.Sprintf("linear_bin_%d", ln), func(b *testing.B) {
			for b.Loop() {
				_, _ = ngram_slice_intersect_and_union_size_less_bin(query_ngrams[i], line_ngrams[i])
			}
		})
	}
	for i, ln := range line_length {
		b.Run(fmt.Sprintf("linear_slice_%d", ln), func(b *testing.B) {
			for b.Loop() {
				_, _ = ngram_slice_intersect_and_union_size_less_slice(query_ngrams[i], line_ngrams[i])
			}
		})
	}
	for i, ln := range line_length {
		b.Run(fmt.Sprintf("ints_%d", ln), func(b *testing.B) {
			line_ints := ngrams_as_ints(line_ngrams[i])
			query_ints := ngrams_as_ints(query_ngrams[i])
			for b.Loop() {
				_, _ = ngram_ints_intersect_and_union_size(query_ints, line_ints)
			}
		})
	}
}
