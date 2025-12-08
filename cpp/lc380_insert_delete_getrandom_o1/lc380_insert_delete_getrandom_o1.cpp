// https://leetcode.com/problems/insert-delete-getrandom-o1/

#include <unordered_map>
#include <vector>
#include <print>
#include <algorithm>

//
// Your RandomizedSet object will be instantiated and called as such:
// RandomizedSet* obj = new RandomizedSet();
// bool param_1 = obj->insert(val);
// bool param_2 = obj->remove(val);
// int param_3 = obj->getRandom();
//

// the idea is to have a hash table with offsets into an array
// getRandom: get random element from the array
// insert: insert into the hash, append to array
// remove: find item in hash, swap with last item, update hash for last item
class RandomizedSet
{
public:
	std::unordered_map<int, uint32_t> map_;
	std::vector<int> data_;

public:
	RandomizedSet()
	{
		srandom(time(NULL));
	}

	bool insert(int val)
	{
		auto const it = map_.find(val);
		if (it != map_.end())
			return false;

		data_.push_back(val);
		auto const ipair = map_.emplace_hint(it, val, data_.size() - 1);
		return true;
	}

	bool remove(int val)
	{
		auto it = map_.find(val);
		if (it == map_.end())
			return false;

		uint32_t const offset = it->second;
		if (offset != data_.size() - 1) // not last item, slowpath
		{
			int last = data_.back();
			map_[last] = offset;
			std::swap(data_[data_.size() - 1], data_[offset]);
		}

		map_.erase(val);
		data_.pop_back();

		return true;
	}

	int getRandom()
	{
		return data_[random() % data_.size()];
	}
};

void run_test_1()
{
	RandomizedSet s;

	bool v;

	std::print("insert(1); ");
	v = s.insert(1);
	std::print("h: {}, d: {} -> {}\n", s.map_, s.data_, v);

	std::print("remove(2); ");
	v = s.remove(2);
	std::print("h: {}, d: {} -> {}\n", s.map_, s.data_, v);

	std::print("insert(2); ");
	v = s.insert(2);
	std::print("h: {}, d: {} -> {}\n", s.map_, s.data_, v);

	{
		std::print("get_random(); ");
		std::unordered_map<int, uint32_t> counters;
		for (int i = 0; i < 1000; i++)
		{
			int const offset = s.getRandom();
			counters[offset]++;
		}
		std::print("{}\n", counters);
	}

	std::print("remove(1); ");
	v = s.remove(1);
	std::print("h: {}, d: {} -> {}\n", s.map_, s.data_, v);

	{
		std::print("get_random(); ");
		std::unordered_map<int, uint32_t> counters;
		for (int i = 0; i < 1000; i++)
		{
			int const offset = s.getRandom();
			counters[offset]++;
		}
		std::print("{}\n", counters);
	}
}

void run_test_2()
{
	RandomizedSet s;

	bool v;

	std::print("\n");

	std::print("insert(0); ");
	v = s.insert(0);
	std::print("h: {}, d: {} -> {}\n", s.map_, s.data_, v);

	std::print("insert(1); ");
	v = s.insert(1);
	std::print("h: {}, d: {} -> {}\n", s.map_, s.data_, v);

	std::print("remove(0); ");
	v = s.remove(0);
	std::print("h: {}, d: {} -> {}\n", s.map_, s.data_, v);

	std::print("insert(2); ");
	v = s.insert(2);
	std::print("h: {}, d: {} -> {}\n", s.map_, s.data_, v);

	std::print("remove(1); ");
	v = s.remove(1);
	std::print("h: {}, d: {} -> {}\n", s.map_, s.data_, v);

	{
		std::print("get_random(); ");
		std::unordered_map<int, uint32_t> counters;
		for (int i = 0; i < 1000; i++)
		{
			int const offset = s.getRandom();
			counters[offset]++;
		}
		std::print("{}\n", counters);
	}
}

int main()
{
	run_test_1();
	run_test_2();
}