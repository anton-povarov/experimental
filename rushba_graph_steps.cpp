#include <vector>
#include <deque>
#include <unordered_map>
#include <unordered_set>
#include <memory>
#include <print>
#include <thread>
#include <functional>
#include <cassert>
#include <span>
#include <ranges>

struct GraphNode
{
	int id;
	std::vector<int> inputs;
	std::vector<int> outputs;
};

struct Graph
{
	std::vector<std::unique_ptr<GraphNode>> nodes_;
	std::unordered_map<int, GraphNode *> g_;

	GraphNode *get_node(int id) const
	{
		auto const it = g_.find(id);
		return (it == g_.end()) ? nullptr : it->second;
	}

	GraphNode *get_or_create_node(int id)
	{
		if (auto *existing_node = this->get_node(id); existing_node)
		{
			return existing_node;
		}

		auto node = std::make_unique<GraphNode>();
		node->id = id;
		g_[id] = node.get();
		nodes_.push_back(std::move(node));
		return nodes_.back().get();
	}

	auto get_entry_nodes() const
	{
		std::vector<GraphNode const *> result;

		for (auto const &n : nodes_)
		{
			if (n->inputs.empty())
				result.push_back(n.get());
		}

		return result;
	}

	auto get_exit_nodes() const
	{
		std::vector<GraphNode const *> result;

		for (auto const &n : nodes_)
		{
			if (n->outputs.empty())
				result.push_back(n.get());
		}

		return result;
	}

	auto get_sync_nodes() const
	{
		std::vector<GraphNode const *> result;

		for (auto const &n : nodes_)
			if (n->inputs.size() > 1)
				result.push_back(n.get());

		return result;
	}
};

Graph construct_graph(std::vector<std::pair<int, int>> const &nodes)
{
	Graph g;

	for (auto const &p : nodes)
	{
		auto *first = g.get_or_create_node(p.first);
		auto *second = g.get_or_create_node(p.second);

		first->outputs.push_back(second->id);
		second->inputs.push_back(first->id);
	}

	return g;
}

void print_graph(Graph const &g)
{
	for (auto const &n : g.g_)
	{
		auto const *node = n.second;
		std::print("{}: {} {}\n", node->id, node->inputs, node->outputs);
	}
}

template <class T>
struct Queue
{
	std::deque<T> queue;
	std::mutex mtx;
	std::condition_variable cv;
};

struct QueueItem
{
	int node_id;
	std::function<void()> task;
	Queue<QueueItem> *response_q = nullptr;
};

struct worker_thread_t
{
	std::string name;
	std::thread t;
};
using worker_thread_ptr = std::unique_ptr<worker_thread_t>;

struct worker_pool_t
{
	Queue<QueueItem> input_queue;
	std::vector<worker_thread_ptr> pool;

	void shutdown()
	{
		for (auto &w : pool)
		{
			std::unique_lock lk(input_queue.mtx);
			input_queue.queue.push_back({-1});
			input_queue.cv.notify_all();
		}

		for (auto &w : pool)
			w->t.join();
	}

	void send_work(QueueItem qi)
	{
		std::unique_lock lk(input_queue.mtx);
		input_queue.queue.push_back(std::move(qi));
		input_queue.cv.notify_one();
	}
};

std::unique_ptr<worker_pool_t> make_worker_pool(int pool_size)
{
	auto pool = std::make_unique<worker_pool_t>();

	for (int i = 0; i < pool_size; i++)
	{
		auto wt = std::make_unique<worker_thread_t>();

		auto const worker = [](worker_thread_t *wt, Queue<QueueItem> &input_queue)
		{
			while (true)
			{
				QueueItem item;

				{
					std::unique_lock lk(input_queue.mtx);
					while (input_queue.queue.empty())
						input_queue.cv.wait(lk);

					item = std::move(input_queue.queue.front());
					input_queue.queue.pop_front();
				}

				if (item.node_id == -1)
				{
					std::print("{}: got exit signal, bye\n", wt->name);
					return;
				}

				std::print("got work item: {}\n", item.node_id);
				if (item.task)
					item.task();

				assert(item.response_q != nullptr && "empty response queue in work item, nowhere to reply");

				{
					std::unique_lock lk(item.response_q->mtx);

					auto *response_q = item.response_q; // take the pointer before we move the item
					response_q->queue.push_back(std::move(item));
					response_q->cv.notify_one();
				}
			}
		};

		wt->name = std::format("worker-{}", i);
		wt->t = std::thread(worker, wt.get(), std::ref(pool->input_queue));
		pool->pool.push_back(std::move(wt));
	}

	return std::move(pool);
}

void traverse_graph(Graph const &g, std::function<void(GraphNode const &)> const &visitor)
{
	auto pool = make_worker_pool(3);

	struct guard
	{
		worker_pool_t *pool;
		guard(worker_pool_t *p) : pool(p) {}
		~guard() { pool->shutdown(); }
	} g_ = {pool.get()};

	Queue<QueueItem> response_q;

	std::unordered_map<int, uint32_t> sync_node_counts;
	for (auto const &node : g.get_sync_nodes())
		sync_node_counts[node->id] = node->inputs.size();

	std::vector<int>
		available_work = {};
	int work_inflight = 0;

	for (auto const &node : g.get_entry_nodes())
		available_work.push_back(node->id);

	while (!available_work.empty() || work_inflight > 0)
	{
		std::print("available work: {}\n", available_work);

		for (auto &w_nid : available_work)
		{
			if (auto sync_it = sync_node_counts.find(w_nid); sync_it != sync_node_counts.end())
			{
				// this is a sync node, we need wait for all paths to reach here
				if (--sync_it->second > 0)
				{
					std::print("waiting on sync node {}, count = {}\n", w_nid, sync_it->second);
					continue;
				}
			}

			pool->send_work({
				w_nid,
				[&g, &visitor, w_nid]()
				{
					auto const *node = g.get_node(w_nid);
					visitor(*node);
				},
				&response_q,
			});

			++work_inflight;
		}
		available_work.clear();

		// grab all responses we can grab, wait for at least one
		std::vector<QueueItem> responses;
		{
			std::unique_lock lk(response_q.mtx);
			response_q.cv.wait(lk, [&]()
							   { return !response_q.queue.empty(); });

			responses.push_back(std::move(response_q.queue.front()));
			response_q.queue.pop_front();
		}

		// process responses, generate new work
		for (auto const &r : responses)
		{
			--work_inflight;

			std::print("got response for node: {}\n", r.node_id);
			auto const *node = g.get_node(r.node_id);
			if (!node)
			{
				std::print("NODE {} does not exist, THIS IS A BUG", r.node_id);
				continue; // THIS IS WEIRD
			}

			for (auto const nid : node->outputs)
				available_work.push_back(nid);
		}
	}
}

using visitor_arg_t = std::vector<std::vector<GraphNode const *>>;
using visitor_func_t = std::function<void(visitor_arg_t &&)>;

struct traverse_ctx_t
{
	Graph const &g;
	visitor_func_t visitor;
	std::unordered_set<GraphNode const *> visited;
};

std::vector<GraphNode const *> traverse_graph_dfs_inner(traverse_ctx_t &ctx, GraphNode const *node)
{
	// walk back over nodes with single input links and coalesce them eagerly
	std::vector<GraphNode const *> nodes = {};
	while (node->inputs.size() == 1)
	{
		ctx.visited.insert(node);
		nodes.push_back(node);

		std::print("coalesce, added node {}\n", node->id);

		auto const *prev_node = ctx.g.get_node(node->inputs[0]);
		if (!prev_node || ctx.visited.contains(prev_node))
			break;

		node = prev_node;
	}

	std::print("curr_node: {}\n", node->id);
	std::print("coalesced_nodes: {}\n", nodes | std::views::transform([](GraphNode const *n)
																	  { return n->id; }) |
											std::ranges::to<std::vector>());

	// mark self before going deeper, in case there is a loop
	ctx.visited.insert(node);

	// now the general case, multiple inputs (including none)
	std::vector<std::vector<GraphNode const *>> sched_children = {};

	for (int input_id : node->inputs)
	{
		auto const *input_node = ctx.g.get_node(input_id);
		if (!input_node || ctx.visited.contains(input_node))
			continue;

		auto to_schedule = traverse_graph_dfs_inner(ctx, input_node);
		if (!to_schedule.empty())
			sched_children.push_back(std::move(to_schedule));
	}

	// sched children if any
	if (!sched_children.empty())
	{
		ctx.visitor(std::move(sched_children));
	}

	// if this is the sync node -> schedule self
	switch (node->inputs.size())
	{
	case 0:					   // entry node
		nodes.push_back(node); // coalesce it with the rest
		break;
	case 1: // exited, because there was a loop in the graph, already have the node in list
		break;
	default: // sync node
		// ctx.visitor({{node}}); // schedule it now, without coalescing
		nodes.push_back(node);
		break;
	}

	auto ids = nodes | std::views::reverse | std::views::transform([](auto n)
																   { return n->id; }) |
			   std::ranges::to<std::vector>();
	std::print("ids: {}\n", ids);

	// let our parent schedule any of our coalesced stuff
	std::vector<GraphNode const *> reversed = nodes | std::views::reverse | std::ranges::to<std::vector>();
	return reversed;
}

void traverse_graph_dfs(traverse_ctx_t &ctx, GraphNode const *node)
{
	auto to_schedule = traverse_graph_dfs_inner(ctx, node);
	ctx.visitor({to_schedule}); // to_schedule will be empty at end of iteration
}

void traverse_graph_recursive(Graph const &g, visitor_func_t const &visitor)
{
	traverse_ctx_t ctx = {
		g,
		visitor,
		{},
	};

	auto const exit_nodes = g.get_exit_nodes();

	for (auto const *node : exit_nodes)
		traverse_graph_dfs(ctx, node);
}

// , std::function<void(std::vector<GraphNode const *> &&)> visitor
enum class direction
{
	forward,
	backward,
};
auto traverse_graph_bfs(Graph const &g, direction d)
{
	auto const *node = (d == direction::forward)
						   ? g.get_entry_nodes()[0]
						   : g.get_exit_nodes()[0];

	std::unordered_set<GraphNode const *> visited;
	std::deque<std::pair<GraphNode const *, int>> queue = {{node, 0}}; // [node, depth]

	std::vector<std::vector<int>> result = {};

	while (!queue.empty())
	{
		auto const pair = queue.front();
		queue.pop_front();

		auto const [node, depth] = pair;

		if (visited.contains(node))
			continue;

		visited.insert(node);

		if (result.size() <= depth)
			result.resize(depth + 1, {});

		result[depth].push_back(node->id);

		auto const &linked_nodes = (d == direction::backward) ? node->inputs : node->outputs;
		for (int input_id : linked_nodes)
		{
			auto const *input_node = g.get_node(input_id);
			if (!input_node || visited.contains(input_node))
				continue;

			queue.push_back({input_node, depth + 1});
		}
	}

	return result;
}

int main()
{
	// this is a parallel scan from entry to exits, with counters to handle sync nodes
	{
		Graph const g = construct_graph({{1, 2}, {2, 3}, {3, 7}, {5, 6}, {6, 7}, {7, 8}, {8, 10}, {8, 9}, {9, 100}, {25, 7}, {10, 101}, {100, 101}});
		print_graph(g);

		std::mutex mtx;
		std::vector<int> nodes_visited;
		traverse_graph(g,
					   [&](GraphNode const &node)
					   {
						   {
							   std::unique_lock lk(mtx);
							   nodes_visited.push_back(node.id);
						   }
						   std::print("visiting node: {}\n", node.id);
					   });
		std::print("visited: {}\n", nodes_visited);
	}

	// this is a reverse-DFS variant, where you get "execute this in parallel" callbacks
	// can't fully extract parallelism from graphs that are much longer "on one side"
	// (will not start executing other sides with it, even if dependencies allow)
	// i.e. below
	//  - it will not recognize that 5 and 25 can be executed concurrently with 200 and 300
	//  - will execute [1,2,3] concurrently with [5,6] though
	{
		/*
			300 \
				1 -> 2 -> 3 \        / -> 10 -----\
			200 /             \      /              \
							7 -> 8                101
			5 -> 6 -----------/      \ -> 9 -> 100 -/
			25 -> 29 --------------------------/
		*/
		// reverse dfs with chain coalescing and concurrency grouping
		// [
		//   [ [300], [200]       ],
		//   [ [1, 2, 3], [5, 6]  ],
		//   [ [25, 29], [7]      ],
		//   [ [8, 10], [9, 100]  ],
		//   [ [101 ]             ],
		// ]
		Graph const g = construct_graph({
			{300, 1},
			{200, 1},
			{1, 2},
			{2, 3},
			{3, 7},
			{5, 6},
			{6, 7},
			{25, 29},
			{29, 8},
			{7, 8},
			{8, 10},
			{8, 9},
			{9, 100},
			{10, 101},
			{100, 101},
		});
		// Graph const g = construct_graph({{300, 1}, {200, 1}, {1, 2}, {2, 3}, {3, 7}, {5, 6}, {6, 7}, {25, 7}, {7, 8}, {8, 10}, {8, 9}, {9, 100}});
		// Graph const g = construct_graph({{300, 1}, {200, 1}, {1, 2}, {2, 3}, {3, 7}, {5, 6}, {6, 7}, {25, 7}, {7, 8}});
		print_graph(g);

		std::vector<std::vector<std::vector<int>>> nodes_visited;
		traverse_graph_recursive(g,
								 [&](visitor_arg_t &&node_ll)
								 {
									 std::vector<std::vector<int>> parallel_ids = {};
									 for (auto &&node_l : node_ll)
									 {
										 parallel_ids.push_back(node_l | std::views::transform([](GraphNode const *n)
																							   { return n->id; }) |
																std::ranges::to<std::vector>());
									 }
									 nodes_visited.push_back(parallel_ids);
								 });
		std::print("visited: {}\n", nodes_visited);
	}

	{
		/*
		 300 \
			  1 -> 2 -> 3 \        / -> 10 -----\
		 200 /             \      /              \
							7 -> 8                101
		 5 -> 6 -----------/      \ -> 9 -> 100 -/
		 25 -> 29 --------------------------/
		*/
		// reverse bfs order
		// [[300, 200], [1], [2, 5], [25, 3, 6], [29, 7], [8, 9], [10, 100], [101]]
		// reverse depth order
		// [
		//   (300,0), (200,0), (5,0), (25,0),
		//   (1,0), (6,0), (29,0)
		//   (2,1), (7,1), (100,1)
		// ]
		Graph const g = construct_graph({
			{300, 1},
			{200, 1},
			{1, 2},
			{2, 3},
			{3, 7},
			{5, 6},
			{6, 7},
			{25, 29},
			{29, 8},
			{7, 8},
			{8, 10},
			{8, 9},
			{9, 100},
			{10, 101},
			{100, 101},
		});

		{
			auto const bfs_list = traverse_graph_bfs(g, direction::forward);
			std::print("bfs entry: {}\n", bfs_list);
		}

		{
			auto const bfs_list = traverse_graph_bfs(g, direction::backward) | std::views::reverse | std::ranges::to<std::vector>();
			std::print("bfs exit: {}\n", bfs_list);
		}
	}

	return 0;
}