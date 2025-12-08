from collections import deque
from dataclasses import dataclass
from typing import Any, List, Tuple, Callable, Awaitable, cast
import pprint
import asyncio
import random
import multiprocessing as mp


@dataclass
class GraphNode:
    id: int
    outputs: list[int]
    inputs: list[int]


type Graph = dict[int, GraphNode]


def create_graph(nodes):
    gn: Graph = {}
    for n in nodes:
        if n[0] not in gn:
            gn[n[0]] = GraphNode(n[0], [], [])
        if n[1] not in gn:
            gn[n[1]] = GraphNode(n[1], [], [])
        gn[n[0]].outputs.append(n[1])
        gn[n[1]].inputs.append(n[0])

    return gn


def find_entry_nodes(g: Graph) -> list[GraphNode]:
    return [n for n in g.values() if not n.inputs]


def find_sync_nodes(g: Graph) -> list[GraphNode]:
    return [n for n in g.values() if len(n.inputs) > 1]


@dataclass
class WorkItem:
    node: GraphNode
    response_q: asyncio.Queue
    task: Callable[["WorkItem"], Awaitable[None]]


async def graph_node_worker(q: asyncio.Queue[WorkItem]):
    while q:
        wi = await q.get()
        await wi.task(wi)
        await wi.response_q.put(wi)


def graph_walk(
    g: Graph,
    start_node: GraphNode,
    sync_nodes: list[GraphNode],
):
    node: GraphNode | None = start_node
    while node:
        if node in sync_nodes:
            print(f"encountered blocking node {node.id}")
        yield node
        node = g[node.outputs[0]] if node.outputs else None


async def traverse_graph(
    nodes: list[tuple[int, int]], visitor: Callable[[GraphNode], Awaitable[None]]
):
    g = create_graph(nodes)
    print(f"graph:\n{pprint.pformat(g)}")
    entry_nodes = find_entry_nodes(g)
    print(f"entry nodes: {[n.id for n in entry_nodes]}")
    sync_nodes = find_sync_nodes(g)
    print(f"sync  nodes: {[n.id for n in sync_nodes]}")

    # workq = asyncio.Queue[WorkItem]()
    # resultq = asyncio.Queue[WorkItem]()
    # workers = [asyncio.create_task(graph_node_worker(workq)) for _ in range(3)]

    available_work = deque(entry_nodes)
    sync_counters: dict[int, int] = {n.id: len(n.inputs) for n in sync_nodes}
    in_flight_tasks = 0
    running_tasks = set()

    async def visitor_call_thunk(wi: WorkItem):
        await visitor(wi.node)

    async def visitor_wrapper(node: GraphNode):
        await visitor(node)
        return node

    print()

    while True:
        if in_flight_tasks == 0 and not available_work:
            break

        while available_work:
            node = available_work.popleft()
            if node.id in sync_counters:  # this is a sync node
                # print(f"encountered a sync node {node}")

                sync_cnt = sync_counters[node.id]
                sync_counters[node.id] -= 1
                sync_cnt -= 1
                if sync_cnt != 0:  # all synced
                    print(f"waiting for sync on node {node}, remaining = {sync_cnt}")
                    continue
                else:
                    print(f"unblocking sync node {node}")

            # print(f"pushing work item: {node}")
            # wi = WorkItem(node, resultq, visitor_call_thunk)
            # in_flight_tasks += 1
            # await workq.put(wi)

            future = asyncio.create_task(asyncio.to_thread(visitor_wrapper, node))
            running_tasks.add(future)

        while True:
            if not running_tasks:
                break

            done, pending = await asyncio.wait(
                running_tasks, timeout=None, return_when="FIRST_COMPLETED"
            )
            running_tasks = pending

            for task in done:
                # res = await task.result()
                # node = res.node
                node = await task.result()
                for n in node.outputs:
                    # print(f"got response for node {node} -> adding work: {n}")
                    available_work.append(g[n])

            # # print("waiting for data")
            # res = await resultq.get()
            # in_flight_tasks -= 1
            # node = res.node
            # for n in node.outputs:
            #     # print(f"got response for node {node} -> adding work: {n}")
            #     available_work.append(g[n])

            # if resultq.empty():
            #     break

    # for w in workers:
    #     w.cancel()

    # print("all work done")

    return 0


def node_append_to_list(append_id_to: list[int]):
    async def visit(node: GraphNode):
        print(f"visiting node: {node}")
        append_id_to.append(node.id)
        await asyncio.sleep(0.1 + random.random() * 0.3)

    return visit


async def main():
    # expected to run 1,2,3 and 5,6 in parallel, sync up on 7 and then branch again from 8
    # 300 \
    #      1 -> 2 -> 3 \        / -> 10
    # 200 /             \      /
    # 25 ------------>   7 -> 8
    # 5 -> 6 -----------/      \ -> 9 -> 100
    #  [300]  | [1, 2, 3] |        | [ 10 ]
    #  [200]  |           | [7, 8] |
    #  [25]   |           |        | [9, 100]
    #  [5, 6] |           |        |
    graph = [
        (300, 1),
        (200, 1),
        (1, 2),
        (2, 3),
        (3, 7),
        (5, 6),
        (6, 7),
        (7, 8),
        (8, 10),
        (8, 9),
        (9, 100),
        (25, 7),
    ]
    nodes_visited = []
    await traverse_graph(graph, node_append_to_list(nodes_visited))

    print(f"visited: {nodes_visited}")

    # run_test_1([(1, 2), (2, 3), (3, 7), (5, 6), (6, 7), (7, 8), (8, 10), (8, 9), (9, 100), (25, 7)])


if __name__ == "__main__":
    asyncio.run(main())
