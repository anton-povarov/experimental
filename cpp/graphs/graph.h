#include <vector>
#include <unordered_map>

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

inline Graph construct_graph(std::vector<std::pair<int, int>> const &nodes)
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
