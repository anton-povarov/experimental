# https://leetcode.com/problems/minimum-genetic-mutation/

from typing import List


class GraphNode:
    visited: bool
    value: str
    links: list["GraphNode"]

    def __init__(self, v):
        self.visited = False
        self.value = v
        self.links = []


def maybe_print(s: str):
    # print(f"{s}")
    pass


class Solution:
    def minMutation(self, startGene: str, endGene: str, bank: List[str]) -> int:
        return self.minMutation_graph(startGene, endGene, bank)
        return self.minMutation_bruteforce(startGene, endGene, bank)

    def minMutation_graph(self, startGene: str, endGene: str, bank: List[str]) -> int:
        def build_graph_from_bank(bank):
            bank_to_node: dict[str, GraphNode] = {}

            for bv in bank:
                node = GraphNode(bv)
                bank_to_node[bv] = node
                maybe_print(f"creating node {bv}")

            for bv, node in bank_to_node.items():
                for other_bv in bank:
                    if other_bv == bv:
                        continue

                    # do not compare if node is already linked
                    other_node = bank_to_node[other_bv]
                    if other_node in node.links:
                        continue

                    # coult gene mutations required
                    diff_count = 0
                    for i in range(len(bv)):
                        if bv[i] != other_bv[i]:
                            diff_count += 1

                    # only single element mutations
                    if diff_count == 1:
                        maybe_print(f"linking nodes {bv} <--> {other_bv}")
                        other_node = bank_to_node[other_bv]
                        node.links.append(other_node)
                        other_node.links.append(node)
            return bank_to_node

        # find the entrypoint into the graph by mutating startGene
        def get_graph_entrypoints():
            mutated_node = None
            gene = startGene
            for i, g in enumerate(gene):
                for mut in ("A", "C", "T", "G"):
                    if g == mut:
                        continue  # skip non-mutations
                    gene_copy = list(gene)  # copy to be able to change content
                    gene_copy[i] = mut
                    mutated_gene = "".join(gene_copy)

                    mutated_node = bank_to_node.get(mutated_gene)
                    if mutated_node:
                        # mutated_node now contains a valid entrypoint into the graph
                        # but it might not be the only one, so we yield, not return
                        yield mutated_node

        def graph_shortest_path(node: GraphNode, target_gene: str, count=1):
            maybe_print(f" {'>' * count} visiting node {node.value}")

            if node.value == target_gene:
                return count

            node.visited = True

            path_counts = []

            for linked_node in node.links:
                if not linked_node.visited:
                    pc = graph_shortest_path(linked_node, target_gene, count + 1)
                    path_counts.append(pc)

            node.visited = False

            return min([x for x in path_counts if x > 0], default=-1)

        # do the thing

        bank_to_node = build_graph_from_bank(bank)

        min_path_length = -1
        for node in get_graph_entrypoints():
            maybe_print(f"found graph entrypoint {node.value}")
            maybe_print(f"searching for {endGene}")

            path_length = graph_shortest_path(node, endGene, 1)
            maybe_print(f"found path_length: {path_length}")

            if min_path_length < 0 or (path_length > 0 and path_length < min_path_length):
                min_path_length = path_length

        return min_path_length

    # this one only finds the first available path, which might not be the shortest
    def minMutation_bruteforce(self, startGene: str, endGene: str, bank: List[str]) -> int:
        bank_seen: dict[str, bool] = {}

        def find_next_mutation(gene: str) -> str | None:
            nonlocal bank_seen
            for i, g in enumerate(gene):
                for mut in ("A", "C", "T", "G"):
                    geneCopy = list(gene)

                    if g == mut:
                        continue
                    geneCopy[i] = mut

                    geneCopyStr = "".join(geneCopy)

                    print(f"checking mut {geneCopyStr}", end="")

                    if geneCopyStr in bank and geneCopyStr not in bank_seen:
                        print(" -> found")
                        bank_seen[geneCopyStr] = True
                        return geneCopyStr
                    else:
                        pass
                        print(f" -> nope {bank}")
            return None

        count = 0
        gene = startGene
        while gene != endGene:
            print()
            print(f"checking gene {gene}")

            newGene = find_next_mutation(gene)
            if not newGene:
                return -1

            count += 1
            gene = newGene

        return count


def run_test(startGene: str, endGene: str, bank: List[str], expected: int):
    s = Solution()
    res = s.minMutation(startGene, endGene, bank)
    print(f"res = {res}, expected = {expected}")
    print(f"{'OK' if res == expected else 'ERROR'}")


if __name__ == "__main__":
    run_test(startGene="AACCGGTT", endGene="AACCGGTA", bank=["AACCGGTA"], expected=1)

    run_test(
        startGene="AACCGGTT",
        endGene="AAACGGTA",
        bank=["AACCGGTA", "AACCGCTA", "AAACGGTA"],
        expected=2,
    )

    run_test("AAAAAAAA", "ACAAAAAA", ["CAAAAAAA", "CCAAAAAA", "ACAAAAAA"], 1)

    run_test(
        startGene="AAAAACCC",
        endGene="AACCCCCC",
        bank=["AAAACCCC", "AAACCCCC", "AACCCCCC"],
        expected=3,
    )

    run_test(
        startGene="AACCTTGG",
        endGene="AATTCCGG",
        bank=["AATTCCGG", "AACCTGGG", "AACCCCGG", "AACCTACC"],
        expected=-1,
    )

    run_test(
        startGene="AAAAAAAA",
        endGene="CCCCCCCC",
        bank=[
            "AAAAAAAA",
            "AAAAAAAC",
            "AAAAAACC",
            "AAAAACCC",
            "AAAACCCC",
            "AACACCCC",
            "ACCACCCC",
            "ACCCCCCC",
            "CCCCCCCA",
            "CCCCCCCC",
        ],
        expected=8,
    )

    run_test(
        startGene="AAAACCCC",
        endGene="CCCCCCCC",
        bank=[
            "AAAACCCA",
            "AAACCCCA",
            "AACCCCCA",
            "AACCCCCC",
            "ACCCCCCC",
            "CCCCCCCC",
            "AAACCCCC",
            "AACCCCCC",
        ],
        expected=4,
    )
