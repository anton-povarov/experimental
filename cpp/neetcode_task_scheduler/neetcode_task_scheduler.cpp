// https://neetcode.io/problems/task-scheduling

// note that tasks ar single uppercase char, so there's 26 possible tasks only
// two solution ideas
// 1. actual simulation
//    simulate time as a counter incremented in a loop, and for each iteration:
//    execute the first *available* task - selected as "the highest frequency"
//    executed tasks go into the queue of [executions_remaining, next_time_it_can_execute]
//      it's critical to use 'absolute' next_time_it_can_execute, not "time to wait" -> no need to touch elements not on head
//      the queue would be _naturally_ sorted by next_time_it_can_execute (since the cooldown is the same for all tasks)
//      the queue would also be naturally sorted by executions_remaining (since we insert the highest frequency ones first)
//    if a task from the queue can now be executed (next_time_it_can_execute == curr_time) -> move it to the heap
//
// 2. count the number of idle slots
//   sort the tasks by number_of_executions required
//   now imagine splitting the timeline into chunks of length N (parameter)
//    we need max_number_of_executions * block_length blocks, but the last one is special, since it need not have idle slots
//    i.e. for the max_number_of_executions we'll have
//    i.e. [A...] [A...] [A...] [A] <- no need for idle at the last slot
//    so the number of possible idle slots is (max_number_of_executions-1) * block_length
//   then we could go through the other tasks and just count the number of those idle slots they would take
//   so our answer is (number of idle slots) + number_of_tasks
//   it's key to note is that there might not be enough idle slots (!)
//   in that case we just accept it, say "we have zero idle slots" and the answer still works

#include <deque>
#include <print>
#include <queue>
#include <vector>

using std::vector;

class Solution
{
public:
	int leastInterval(vector<char> &tasks, int n) { return idea1_implementation(tasks, n); }

private:
	// this one has extra tracking for task_chr to print the execution flow,
	//  but still an assumption that they're single capital letter
	//  can alleviate it with unordered_map if we actually want any kind of task
	int idea1_implementation(vector<char> &tasks, int n)
	{
		// max heap [number_of_executions remaining]
		using heap_t = std::priority_queue<std::tuple<uint32_t, char>>;
		// [number_of_executions remaining, next_time_to_execute]
		using queue_t = std::deque<std::tuple<uint32_t, char, int>>;

		// count n occurrences of all tasks
		vector<uint32_t> counts(size_t{26}, 0);
		for (auto const t : tasks)
			counts[t - 'A']++;

		heap_t heap;
		for (int i = 0; i < counts.size(); ++i)
			if (counts[i] > 0)
				heap.push({counts[i], 'A' + i});

		queue_t queue;

		int time = 0;

		while (!heap.empty() || !queue.empty()) {
			if (!heap.empty()) { // execute one task if available
				auto [exec_count, task_chr] = heap.top();
				heap.pop();

				time++;
				std::print("[t: {}] executing {}\n", time, task_chr);

				exec_count -= 1; // -1 since we've just executed it
				if (exec_count > 0)
					queue.push_back({exec_count, task_chr, time + n});
			}
			else {
				// nothing to execute right now, jump forward in time to the next task waiting
				// queue is not empty due to the outer while loop condition
				auto const &[_, _, next_exec_time] = queue.front();

				for (int i = 0; i < (next_exec_time - time); i++)
					std::print("[t: {}] idle\n", time + i + 1);
				time = next_exec_time;
			}

			// try pop from the queue, if there are any tasks now executable
			while (!queue.empty()) {
				auto const &[execs_remaining, task_chr, next_exec_time] = queue.front();
				if (next_exec_time <= time) { // can execute
					heap.push({execs_remaining, task_chr});
					queue.pop_front();
				}
				else
					break;
			}
		}

		return time;
	}
};

#include <string>

void run_test(std::string tasks_str, int n)
{
	std::vector<char> tasks{tasks_str.begin(), tasks_str.end()};

	Solution s;
	int      res = s.leastInterval(tasks, n);
	std::print("tasks: {}, n = {} -> {}\n", tasks, n, res);
}

int main()
{
	run_test("AABB", 2);
	run_test("AAABBB", 2);
	return 0;
}