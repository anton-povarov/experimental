#include <cstring>
#include <print>
#include <ranges>
#include <string>
#include <string_view>
#include <vector>

struct MyStruct
{
	int id;
	std::string name;
	double value;
};

int main()
{
	{
		// Create a vector of MyStruct objects
		std::vector<MyStruct> data = {{1, "Alpha", 10.0},
		                              {2, "Beta", 15.0},
		                              {3, "Gamma", 20.0},
		                              {4, "Delta", 25.0},
		                              {5, "Epsilon", 30.0}};

		// Extract the 'id' field and filter for even numbers
		auto even_ids = data                                                                   //
		              | std::views::transform([](MyStruct const &s) { return s.id; })          // Extract 'id'
		              | std::views::filter([](int id) { return id % 2 == 0; })                 //
		              | std::views::transform([](auto id) { return std::format("[{}]", id); }) //
		        // | std::views::enumerate
		        ;

		std::print("{}\n", even_ids);
	}

	// {
	// 	std::vector<int> data = {10, 20, 30, 40, 50};

	// 	// Iterate with index using std::views::enumerate
	// 	for (auto const &[index, value] : std::views::enumerate(data)) {
	// 		std::cout << "Index: " << index << ", Value: " << value << std::endl;
	// 	}
	// }

	auto const string_split = [](auto const &str, std::string_view const &delim) {
		auto seq = std::views::split(str, delim) |
		           std::views::transform([](auto &&t) { return std::string_view{t}; });
		return seq;
	};

	{
		using namespace std::literals;
		// std::string_view const str = "apple:dumple:heyo";
		auto const str = "apple:dumple:heyo"sv;
		auto enumerated_seq = string_split(str, ":"sv) | std::views::enumerate;

		for (auto const &[idx, name] : enumerated_seq) {
			std::print("elt[{}]: {}\n", idx, name);
		}
		std::print("split = {}\n", enumerated_seq);
	}

	{
		std::string_view v3 = "__cpp_lib_ranges_chunk_by";
		auto fn3 = [](auto x, auto y) { return not(x == '_' or y == '_'); };
		auto view3 = v3 | std::views::chunk_by(fn3) |
		             std::views::transform([](auto r) { return std::string_view(r); }) |
		             std::ranges::to<std::vector>();
		std::print("v3 = {}\n", view3);
	}

	{
		std::string_view v3 = "like you";
		auto view3 = v3 | std::views::chunk_by([](auto x, auto y) { return !(x == ' ' or y == ' '); }) |
		             std::views::transform([](auto r) { return std::string_view(r); }) |
		             std::ranges::to<std::vector>();
		std::print("v3 = {}\n", view3);
	}

	{ // generate trigrams
		auto const generate_trigrams = [](std::string_view str) {
			std::print("str = '{}'\n", str);

			auto words = str
			           // chunk by words and other stuff
			           | std::views::chunk_by([](char l, char r) { return not(!isalnum(l) or !isalnum(r)); })
			           // remove chunks that do not start with a word-like char
			           | std::views::filter([](auto range) { return !range.empty() && isalnum(range[0]); })
			           // transform ranges into words with prefix and suffix (NOTE: small allocations here)
			           | std::views::transform(
			                     [](auto range) { return std::format("__{} ", std::string_view{range}); });

			std::vector<std::string> trigrams;

			for (auto const &word : words) {
				for (size_t i = 0; i < word.size() - 2; i++)
					trigrams.push_back(std::string{&word[i], 3});
			}

			return trigrams;
		};

		auto const str = std::string_view{"like you !a"};
		auto const trigrams = generate_trigrams(str);
		std::print("trigrams = {}\n", trigrams);
	}

	return 0;
}