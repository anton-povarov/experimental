#include <vector>
#include <deque>
#include <unordered_set>
#include <unordered_map>
#include <algorithm>
#include <print>
#include <format>
#include <type_traits>
#include <span>
#include <functional>
#include <stack>
#include <cstdint>
#include <cassert>

using std::pair;
using std::unordered_set;
using std::vector;

template <class IDType>
struct csr_t
{
	vector<IDType> edges;
	vector<uint32_t> offsets;

	std::span<IDType const> edges_by_id(uint32_t node_id) const
	{
		return {
			&edges[offsets[node_id]],
			offsets[node_id + 1] - offsets[node_id]};
	}
};

template <class T>
	requires std::formattable<T, char>
struct std::formatter<csr_t<T>> : std::formatter<std::string>
{
	template <class FmtContext>
	auto format(csr_t<T> const &csr, FmtContext &ctx) const
	{
		std::format_to(ctx.out(), "{{ E: {}, O: {} }}", csr.edges, csr.offsets);
		return ctx.out();
	}
};

csr_t<int> csr_construct_from_link_pairs(vector<pair<int, int>> const &pairs)
{
	if (pairs.empty())
		return {};

	csr_t<int> csr;

	return csr;
}

// ------------------------------------------------------------------------------------------------------------

struct graph_default_node_base_t
{
};

template <class NodeT>
struct graph_impl_node_t : public NodeT
{
	uint32_t internal_id; // offset in the nodes array, set at creation time
	uint32_t virtual_id;  // given at creation time by the caller
};

template <class T>
	requires std::formattable<T, char>
struct std::formatter<graph_impl_node_t<T>> : std::formatter<std::string>
{
	template <class FmtContext>
	auto format(graph_impl_node_t<T> const &node, FmtContext &ctx) const
	{
		std::format_to(ctx.out(), "{{ {}: {} }}", node.internal_id, *static_cast<T const *>(&node));
		return ctx.out();
	}
};

template <class NodeT = graph_default_node_base_t>
struct GraphImpl
{
	using node_t = graph_impl_node_t<NodeT>;

	std::deque<node_t> nodes; // deque to make sure nodes do not move in memory as we add/remove some
	csr_t<uint32_t> csr_inputs;
	csr_t<uint32_t> csr_outputs;

	uint32_t node_count() const
	{
		return nodes.size();
	}

	node_t *get_node_by_id(uint32_t id)
	{
		if (id >= nodes.size())
			return nullptr;

		return &nodes[id];
	}

	node_t const *get_node_by_id(uint32_t id) const
	{
		if (id >= nodes.size())
			return nullptr;

		return &nodes[id];
	}

	template <class... Args>
	node_t *create_node(Args &&...args)
	{
		node_t &inserted_node = nodes.emplace_back(std::forward<Args...>(args)...);
		inserted_node.internal_id = nodes.size() - 1;
		return &inserted_node;
	}

	std::span<uint32_t const> node_inputs(uint32_t node_id) const
	{
		return csr_inputs.edges_by_id(node_id);
	}

	std::span<uint32_t const> node_outputs(uint32_t node_id) const
	{
		return csr_outputs.edges_by_id(node_id);
	}

	static GraphImpl construct_from_virtual_edges(vector<pair<int, int>> const &node_pairs)
	{
		GraphImpl g;
		std::unordered_set<uint32_t> created;

		for (auto const &p : node_pairs)
		{
			if (!created.contains(p.first))
			{
				auto *node = g.create_node();
				node->created.insert(p.first);
			}
		}

		return std::move(g);
	}

	static GraphImpl construct_from_edges(vector<pair<int, int>> const &node_pairs)
	{
		GraphImpl g;

		// nodes = [0, max_node_id], count = max_node_id+1
		int node_count = 0;
		for (auto const &[first, second] : node_pairs)
			node_count = std::max({node_count, first + 1, second + 1});

		for (int i = 0; i < node_count; i++)
			g.create_node();

		// count in and out edges from each vertex
		// note the shift by 1, this will matter at the next step
		g.csr_outputs.offsets.resize(node_count + 1);
		g.csr_inputs.offsets.resize(node_count + 1);
		for (auto const &[first, second] : node_pairs)
		{
			g.csr_outputs.offsets[first + 1]++;
			g.csr_inputs.offsets[second + 1]++;
		}

		// compute the running prefix sum, this will be the offset for edges data starts
		for (int i = 0; i < node_count; i++)
		{
			g.csr_outputs.offsets[i + 1] += g.csr_outputs.offsets[i];
			g.csr_inputs.offsets[i + 1] += g.csr_inputs.offsets[i];
		}

		// fill in the edge data
		// we copy the offsets array (we're going to be modifying it)
		// we then use the abs offsets to insert the edge ids, incrementing for the next one
		{
			g.csr_outputs.edges.resize(node_pairs.size());
			std::vector<uint32_t> insert_offsets = g.csr_outputs.offsets;
			for (auto const &[first, second] : node_pairs)
				g.csr_outputs.edges[insert_offsets[first]++] = second;
		}
		{
			g.csr_inputs.edges.resize(node_pairs.size());
			std::vector<uint32_t> insert_offsets = g.csr_inputs.offsets;
			for (auto const &[first, second] : node_pairs)
				g.csr_inputs.edges[insert_offsets[second]++] = first;
		}

		return std::move(g);
	}
}; // GraphImpl<>

// ------------------------------------------------------------------------------------------------------------

template <class NodeT>
auto graph_get_entry_node_ids(GraphImpl<NodeT> const &g)
{
	std::vector<uint32_t> result;
	for (uint32_t i = 0; i < g.node_count(); i++)
		if (g.node_inputs(i).size() == 0)
			result.push_back(i);
	return result;
}

template <class NodeT>
auto graph_get_exit_node_ids(GraphImpl<NodeT> const &g)
{
	std::vector<uint32_t> result;
	for (uint32_t i = 0; i < g.node_count(); i++)
		if (g.node_outputs(i).size() == 0)
			result.push_back(i);
	return result;
}

template <class T>
using graph_dfs_node_visitor_t = std::function<void(typename GraphImpl<T>::node_t const &)>;

template <class NodeT>
struct graph_dfs_iterative_ctx_t
{
	GraphImpl<NodeT> const &g;
	std::unordered_set<uint32_t> visited;
	graph_dfs_node_visitor_t<NodeT> const &visitor_fn;
};

template <class NodeT>
void graph_dfs_iterative_inner(graph_dfs_iterative_ctx_t<NodeT> &ctx, uint32_t node_id)
{
	std::stack<pair<uint32_t, uint32_t>> st; // [node_id, child_index]
	st.push({node_id, 0});

	while (!st.empty())
	{
		auto &[node_id, child_index] = st.top();

		ctx.visited.insert(node_id);

		auto const child_node_ids = ctx.g.node_inputs(node_id);

		// processed all children, can exit recursion
		if (child_index >= child_node_ids.size())
		{
			auto const *node_ptr = ctx.g.get_node_by_id(node_id);
			assert(node_ptr && "node_id is out of bounds, graph is broken");

			ctx.visitor_fn(*node_ptr);

			st.pop();
			continue;
		}

		// need to process next child, unless it's been visited
		// in case we're at end now -> just loop around and we'll process the node
		// note the reference increment here, will update item at the top of the stack
		for (; child_index < child_node_ids.size(); ++child_index)
		{
			uint32_t child_id = child_node_ids[child_index];
			if (ctx.visited.contains(child_id))
				continue;

			st.push({child_id, 0}); // FIXME: this can invalidate node_id and child_index
			break;
		}
	}
}

template <class NodeT>
void graph_dfs_iterative(GraphImpl<NodeT> const &g, graph_dfs_node_visitor_t<NodeT> const &visitor)
{
	graph_dfs_iterative_ctx_t ctx = {
		.g = g,
		.visited = {},
		.visitor_fn = visitor,
	};

	for (auto const &node_id : graph_get_exit_node_ids(g))
		if (!g.node_inputs(node_id).empty() || !g.node_outputs(node_id).empty())
			graph_dfs_iterative_inner(ctx, node_id);
}

// ------------------------------------------------------------------------------------------------------------

struct node_base_t
{
	std::string value;
};
using graph_t = GraphImpl<node_base_t>;
using graph_node_t = typename graph_t::node_t;

template <>
struct std::formatter<node_base_t> : std::formatter<std::string>
{
	template <class FmtContext>
	auto format(node_base_t const &node, FmtContext &ctx) const
	{
		std::format_to(ctx.out(), "{}", node.value);
		return ctx.out();
	}
};

void run_dfs_visit_test(std::string name, vector<pair<int, int>> const &graph_edges)
{
	auto g = graph_t::construct_from_edges(graph_edges);
	// for (uint32_t i = 0; i < g.node_count(); i++)
	// 	g.get_node_by_id(i)->value = std::format("node-{}", i);

	// std::print("nodes: {}\n", g.nodes);
	// std::print("csr_inputs: {}\n", g.csr_inputs);
	// std::print("csr_outputs: {}\n", g.csr_outputs);

	// for (uint32_t i = 0; i < g.node_count(); i++)
	// 	std::print("node {}, inputs: {}, outputs: {}\n",
	// 			   g.get_node_by_id(i)->internal_id,
	// 			   g.node_inputs(i),
	// 			   g.node_outputs(i));

	std::print("running dfs_iterative on {}\n", name);

	std::vector<uint32_t> visited_nodes;
	graph_dfs_iterative(g, [&](graph_node_t const &node)
						{ visited_nodes.push_back(node.internal_id); });
	std::print("visited: {}\n", visited_nodes);
	std::print("\n");
}

int main()
{
	run_dfs_visit_test(
		"small_graph",
		{
			{0, 2},
			{1, 2},
			{2, 3},
			{2, 4},
			{4, 5},
			{3, 5},
		});

	run_dfs_visit_test(
		"standard_graph",
		{
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

	return 0;
}