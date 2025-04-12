from copy import copy
from dataclasses import dataclass, field
from typing import Self

from tools.logger import Logger


@dataclass
class TNode:
    key: str | int
    value: any
    out_: list[str | int] = field(default_factory=list)  # list of tnode_ids, filled by Tree
    in_: list[str | int] = field(default_factory=list)  # list of tnode_ids, filled by Tree

    def __hash__(self):
        return self.key

    def __repr__(self):
        return f"{self.in_}->({self.key}:{self.value})->{self.out_}"

    def __str__(self):
        return f"{self.key} - {self.value}" f" - from:{[k.key for k in self.in_]}" f" - to:{[k.key for k in self.out_]}"


@dataclass
class Edge:
    _from: str | int
    _to: str | int


class Graph:
    def __init__(self, tnodes: dict[str | int, any], edges: list[Edge]):
        self.table: dict[str, TNode] = {key: TNode(key, val) for key, val in tnodes.items()}
        for edge in edges:
            self.table[edge._from].out_.append(edge._to)
            self.table[edge._to].in_.append(edge._from)
        tnodelist = list(self.table.values())
        self.roots: list[TNode] = [tnode for tnode in tnodelist if not tnode.in_]
        self.leafs: list[TNode] = [tnode for tnode in tnodelist if not tnode.out_]

    def is_cyclic(self) -> bool:
        """
        Determine there are 0 SCCs.
        """
        is_sub_dag = set()
        nodes_to_check: list[TNode] = list(self.table.values())

        def dfs_has_cycle(node: TNode, visited: set[str | int]):
            if not node.out_:
                is_sub_dag.add(node.key)
                return False
            if node.key in visited:
                return True
            visited.add(node.key)
            for out in node.out_:
                if out in is_sub_dag:
                    continue
                if dfs_has_cycle(self.table[out], visited):
                    return True
            return False

        while nodes_to_check:
            curr = nodes_to_check.pop()
            if curr.key in is_sub_dag:
                continue
            # ensure that each reachable graph is it's own SCC
            # otherwise immediately return false
            visited_sub_dag_nodes = set()
            if dfs_has_cycle(curr, visited_sub_dag_nodes):
                return True
            for nodekey in visited_sub_dag_nodes:
                is_sub_dag.add(nodekey)
        return False

    def subgraph_from(self, node_key: str | int) -> Self:
        # gets the subgraph reachable from
        reached: dict[str | int, any] = {}
        edges: list[Edge] = []
        node = self.table[node_key]
        stack = [node]
        while stack:
            curr = stack.pop()
            if curr in reached:
                continue
            reached[curr.key] = curr.value
            edges.extend([Edge(curr.key, outkey) for outkey in curr.out_])
            stack.extend([self.table[outkey] for outkey in curr.out_])
        return self.__init__(reached, edges)
