# https://leetcode.com/problems/substring-with-concatenation-of-all-words/

from collections import defaultdict
import sys
from typing import List


sys.path.insert(0, "..")  # a hacky way, but whatever
from verbose_call import verbose_group


class Solution:
    def findSubstring(self, s: str, words: List[str]) -> List[int]:
        return self._find_substring_char_window(s, words)
        # return self._find_substring_block_approach(s, words)

    def _find_substring_char_window(self, s: str, words: List[str]) -> List[int]:
        if not words or not str:
            return []

        str_len = len(s)
        word_len = len(words[0])
        substring_len = word_len * len(words)

        word_counts = defaultdict[str, int](int)
        for word in words:
            word_counts[word] += 1

        result = []

        def sequence_is_acceptable(substring: str):
            seen_words = dict[str, int]()

            for i in range(0, substring_len, word_len):
                word = substring[i : i + word_len]
                if word not in word_counts:
                    return False

                seen_words[word] = seen_words.get(word, 0) + 1
                if seen_words[word] > word_counts[word]:
                    return False

            for word, count in word_counts.items():
                if count != seen_words.get(word, 0):
                    return False
            return True

        # print()

        i = 0
        max_i = str_len - substring_len
        while i <= max_i:
            end_i = i + substring_len
            # print(f"[{i}:{end_i}] -> {s[i:end_i]}", end="")
            acceptable = sequence_is_acceptable(s[i:end_i])
            # print(f" -> {acceptable}")

            if acceptable:
                result.append(i)

            # todo: maybe we could move further after a successful match
            #       but i'm not sure at this point, strings might overlap wildly

            # ideally we'd move by the length of the common prefix of all strings
            # this would reduce the 'constant' of the algorithm, but not its quadratic-ish nature
            i += 1

        return result

    # this function works under assumption that the whole of `s` is comprised of words
    # might not be the same words as in `words`, but still
    #  the string can be split into chunks of length `len(words[])` considered words
    # this transforms the function into a subsequence search
    def _find_substring_block_window(self, s: str, words: List[str]) -> List[int]:
        if not words or not str:
            return []

        word_len = len(words[0])

        str_words = [s[i : i + word_len] for i in range(0, len(s) - word_len + 1, word_len)]
        word_to_id = {word: i for i, word in enumerate(words)}
        str_words_ids = [word_to_id.get(word) for word in str_words]
        word_id_counts = defaultdict[int, int](int)
        for word_id in words:
            word_id_counts[word_to_id[word_id]] += 1

        # print()
        # print(str_words)
        # print(word_to_id)
        # print(str_words_ids)
        # print(word_id_counts)

        def sequence_is_acceptable(str_words_ids: list[int | None]):
            # do we have a full range?
            # if yes - check if we have all permutations via counters
            if len(str_words_ids) != len(words):
                return False

            w_counts_local = word_id_counts.copy()
            for word_id in str_words_ids:
                assert word_id is not None
                word_count = w_counts_local.get(word_id)
                assert word_count is not None

                if word_count == 0:
                    return False  # this word is used too many times

                w_counts_local[word_id] -= 1
            return True

        result = []

        begin_i = 0
        while begin_i < len(str_words_ids):
            if str_words_ids[begin_i] is None:
                begin_i += 1
                continue

            # begin_i is now on the first word

            end_i = begin_i + 1
            while end_i < min(begin_i + len(words), len(str_words_ids)):
                if str_words_ids[end_i] is None:
                    break
                end_i += 1

            # end_is is now past-the-end of the possible words sequence

            # print(f"[{begin_i}:{end_i}] -> {str_words_ids[begin_i:end_i]}", end="")
            acceptable = sequence_is_acceptable(str_words_ids[begin_i:end_i])
            # print(f" -> {acceptable}")
            if acceptable:
                result.append(begin_i)

            # begin_i = end_i
            begin_i += 1

        # result contains word offsets, we need symbol offsets
        return [res * word_len for res in result]


if __name__ == "__main__":
    with verbose_group("_find_substring_char_window") as g:
        g.verbose_call(
            Solution()._find_substring_char_window,
            "aababaabd",
            ["aba", "abd"],
            expected=[3],
        )
        g.verbose_call(
            Solution()._find_substring_char_window,
            "lingmindraboofooowingdingbarrwingmonkeypoundcake",
            ["fooo", "barr", "wing", "ding", "wing"],
            expected=[13],
        )
        g.verbose_call(
            Solution()._find_substring_char_window,
            "lingmindraboofooowingdingbarrwing",
            ["fooo", "barr", "wing", "ding", "wing"],
            expected=[13],
        )
        g.verbose_call(
            Solution()._find_substring_char_window,
            "barfoothefoobarman",
            ["foo", "bar"],
            expected=[0, 9],
        )
        g.verbose_call(
            Solution()._find_substring_char_window,
            "wordgoodgoodgoodbestword",
            ["word", "good", "best", "word"],
            expected=[],
        )
        g.verbose_call(
            Solution()._find_substring_char_window,
            "barfoofoobarthefoobarman",
            ["bar", "foo", "the"],
            expected=[6, 9, 12],
        )
        g.verbose_call(
            Solution()._find_substring_char_window,
            "wordgoodgoodgoodbestword",
            ["word", "good", "best", "good"],
            expected=[8],
        )

    with verbose_group("_find_substring_block_window") as g:
        g.verbose_call(
            Solution()._find_substring_block_window,
            "barfoothefoobarman",
            ["foo", "bar"],
            expected=[0, 9],
        )
        g.verbose_call(
            Solution()._find_substring_block_window,
            "wordgoodgoodgoodbestword",
            ["word", "good", "best", "word"],
            expected=[],
        )
        g.verbose_call(
            Solution()._find_substring_block_window,
            "barfoofoobarthefoobarman",
            ["bar", "foo", "the"],
            expected=[6, 9, 12],
        )
        g.verbose_call(
            Solution()._find_substring_block_window,
            "wordgoodgoodgoodbestword",
            ["word", "good", "best", "good"],
            expected=[8],
        )
