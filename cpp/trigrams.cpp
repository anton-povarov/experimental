#include <algorithm>
#include <format>
#include <memory>
#include <print>
#include <ranges>
#include <string>
#include <string_view>
#include <unordered_map>
#include <unordered_set>
#include <vector>

auto generate_trigrams(std::string_view str)
{
	// std::print("str = '{}'\n", str);

	auto words =
	        str
	        // chunk by words and other stuff
	        | std::views::chunk_by([](char l, char r) { return not(!isalnum(l) or !isalnum(r)); })
	        // remove chunks that do not start with a word-like char
	        | std::views::filter([](auto range) { return !range.empty() && isalnum(range[0]); })
	        // transform ranges into words with prefix and suffix (NOTE: small allocations here)
	        | std::views::transform([](auto range) { return std::format("__{} ", std::string_view{range}); });

	std::vector<std::string> trigrams;

	for (auto const &word : words) {
		for (size_t i = 0; i < word.size() - 2; i++)
			trigrams.push_back(std::string{&word[i], 3});
	}

	return trigrams;
};

struct document_content_t
{
	uint64_t    id;
	std::string content;

	std::unordered_set<std::string> trigrams;
};

// trigram -> documents
using document_content_ptr = std::shared_ptr<document_content_t>;
using document_index_t = std::unordered_map<std::string, std::vector<document_content_ptr>>;

void index_insert(document_index_t &index, uint64_t doc_id, std::string const &document)
{
	auto const trigrams = generate_trigrams(document);

	// precompute trigram hash for the document
	std::unordered_set<std::string> tri_hash;
	for (auto const &tri : trigrams) {
		tri_hash.insert_range(trigrams);
	}

	auto doc_content = std::make_shared<document_content_t>(doc_id, document, std::move(tri_hash));

	// insert the doc into all trigrams it contains
	for (auto const &tri : trigrams) {
		index[tri].push_back(doc_content);
	}
}

auto index_search(document_index_t const &index, std::string const &query, double min_similarity = 0.15)
{
	std::unordered_map<uint64_t, std::tuple<document_content_ptr, double>> result;
	std::unordered_set<uint64_t>                                           docs_checked;

	auto const trigrams = generate_trigrams(query);
	std::print("[min_sim: {}] query: '{}'\n", min_similarity, query);
	std::print("q_trigrams: {}\n", trigrams);

	for (auto const &tri : trigrams) {
		auto const it = index.find(tri);
		if (it == index.end())
			continue;

		auto const &documents = it->second;
		for (document_content_ptr doc : documents) {

			auto const [_, inserted] = docs_checked.insert(doc->id);
			if (!inserted) // i.e. key already existed = we've seen this doc before
				continue;

			// std::print("doc[{}] trigrams: {}\n", doc->id, doc->trigrams);

			// Similarity
			//  A = query
			//  B = document
			// Jaccard: https://en.wikipedia.org/wiki/Jaccard_index
			//  (|A intersect B|) / (|A| + |B| - |A intersect B|)
			// D-guy-forgot-his-name
			//  (2 * |A intersect B|) / (|A| + |B|)
			//
			// (chargpt told me postgres uses D-guy, but google does not confirm)
			// looking at cockroachdb docs - they use Jaccard

			size_t const intersection_sz = std::ranges::count_if(
			        trigrams, [&doc](auto const &v) { return doc->trigrams.contains(v); });

			size_t const union_sz = trigrams.size() + doc->trigrams.size() - intersection_sz;

			double const similarity = double(intersection_sz) / double(union_sz);

			std::print("similarity for doc {}: {}/{} = {}\n", doc->id, intersection_sz, union_sz, similarity);

			if (similarity > min_similarity)
				result.emplace(doc->id, std::make_tuple(doc, similarity));
		}
	}

	return result;
}

int main()
{
	// { // generate trigrams
	// 	auto const str = std::string_view{"like you !a"};
	// 	auto const trigrams = generate_trigrams(str);
	// 	std::print("trigrams = {}\n", trigrams);
	// }

	document_index_t doc_index;
	index_insert(doc_index, 1, "hey, do you like wine?");
	index_insert(doc_index, 2, "I've been seeing ghosts recently");
	index_insert(doc_index, 3, "noone is like me in the whole world");
	index_insert(doc_index, 4, "we're going to rock the world");
	index_insert(doc_index, 5, "ghostbusters!");
	index_insert(doc_index, 6, "steven!");
	index_insert(doc_index, 7, "wordy");
	index_insert(doc_index, 8, "wofoord");

	auto run_query = [&doc_index](auto &&query, double min_sim = 0.15) {
		auto const docs = index_search(doc_index, query, min_sim);
		for (auto const &[doc_id, doc_data] : docs) {
			auto const &[doc_ptr, similarity] = doc_data;
			std::print("[sim: {:.4f}] doc[{}] '{}'\n", similarity, doc_id, doc_ptr->content);
		}
	};

	run_query("stephen", 0.15);
	run_query("steevy", 0.15);
	run_query("word", 0.15);

	return 0;
}