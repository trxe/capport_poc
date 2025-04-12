import pytest

from capport.tools.graph import Edge, Graph, TNode


class GraphBuilder:
    @classmethod
    def combine(cls, adj_prefix: str | int, idx: int):
        if isinstance(adj_prefix, str):
            return f"{adj_prefix}{idx}"
        elif isinstance(adj_prefix, int):
            return adj_prefix + idx

    @classmethod
    def cycle(cls, prefix: str | int, size: int) -> Graph:
        if isinstance(prefix, int):
            prefix = prefix << 16
        tnodes = {cls.combine(prefix, i): i for i in range(size)}
        edges = [Edge(cls.combine(prefix, i - 1), cls.combine(prefix, i)) for i in range(size)]
        edges[0]._from = cls.combine(prefix, (size - 1))
        edges[-1]._to = cls.combine(prefix, 0)

        return Graph(tnodes, edges)

    @classmethod
    def pascal(cls, prefix: str | int, levels: int) -> Graph:
        if isinstance(prefix, int):
            prefix = prefix << 16
        tnodes = {cls.combine(prefix, i): i for i in range(1, (levels + 1) * levels // 2 + 1)}
        prev = [1]
        edges = []
        for level in range(1, levels):
            edges.extend([Edge(cls.combine(prefix, pc), cls.combine(prefix, (pc + level))) for pc in prev])
            edges.extend([Edge(cls.combine(prefix, pc), cls.combine(prefix, (pc + level + 1))) for pc in prev])
            curr = [pc + level for pc in prev]
            curr.append(prev[-1] + level + 1)
            prev = curr
        return Graph(tnodes, edges)

    @classmethod
    def split(cls, tnodes: dict[str | int, any], root: str | int, prefix: str | int, num_children: int) -> Graph:
        if isinstance(prefix, int):
            prefix = prefix << 16
        num_tnodes = len(tnodes)
        new_tnodes = {cls.combine(prefix, i): i for i in range(num_tnodes + 1, num_tnodes + num_children + 1)}
        new_edges = [Edge(root, new_tnode) for new_tnode in new_tnodes]
        return new_tnodes, new_edges

    @classmethod
    def join(cls, tnodes: dict[str | int, any], parent_tnodes: list[str | int], child_key: str | int) -> Graph:
        num_tnodes = len(tnodes)
        new_tnodes = {child_key: num_tnodes + 1}
        new_edges = [Edge(parent_tnode, child_key) for parent_tnode in parent_tnodes]
        return new_tnodes, new_edges


class TestTree:
    def test_simple_cycle(self):
        cycle_graph = GraphBuilder.cycle(12, 12)
        assert cycle_graph.is_cyclic()
        cycle_graph = GraphBuilder.cycle("t_", 12)
        assert cycle_graph.is_cyclic()

    def test_simple_branching_dag(self):
        pascal_graph = GraphBuilder.pascal(5, 8)
        assert not pascal_graph.is_cyclic()
        pascal_graph = GraphBuilder.pascal("p_", 8)
        assert not pascal_graph.is_cyclic()

    def test_split_and_merge_dag_and_non_dag(self):
        tnodes = {"base": 0}
        layer_1_nodes, layer_1_edges = GraphBuilder.split(tnodes, "base", "l1_", 7)
        layer_1_node_keys = list(layer_1_nodes.keys())
        layer_2a, layer_2b, layer_2c = layer_1_node_keys[:3], layer_1_node_keys[3:4], layer_1_node_keys[4:7]
        layer_2a_nodes, layer_2a_edges = GraphBuilder.join(layer_1_nodes, layer_2a, "l2a")
        layer_2b_nodes, layer_2b_edges = GraphBuilder.split(layer_1_nodes, layer_2b[0], "l2b_", 2)
        layer_2c_nodes, layer_2c_edges = GraphBuilder.join(layer_1_nodes, layer_2c, "l2c")
        layer_2_nodes = {**layer_2a_nodes, **layer_2b_nodes, **layer_2c_nodes}
        sink_node, sink_edges = GraphBuilder.join(layer_2_nodes, list(layer_2_nodes.keys()), "sink")
        all_edges = [*layer_1_edges, *layer_2a_edges, *layer_2b_edges, *layer_2c_edges, *sink_edges]
        all_tnodes = {**tnodes, **layer_1_nodes, **layer_2_nodes, **sink_node}
        dag_graph = Graph(all_tnodes, all_edges)
        non_dag_graph_no_roots_no_leaves = Graph(all_tnodes, [*all_edges, Edge("sink", "base")])
        non_dag_graph_no_roots = Graph(all_tnodes, [*all_edges, Edge("l1_3", "base")])
        non_dag_graph_no_leaves = Graph(all_tnodes, [*all_edges, Edge("sink", "l1_3")])
        dag_graph_l1_3 = Graph(all_tnodes, [*all_edges, Edge("l2c", "l1_3")])
        non_dag_graph_l1_8 = Graph(all_tnodes, [*all_edges, Edge("l2c", "l1_8")])

        assert non_dag_graph_no_roots_no_leaves.is_cyclic()
        assert non_dag_graph_no_roots.is_cyclic()
        assert non_dag_graph_no_leaves.is_cyclic()
        assert non_dag_graph_l1_8.is_cyclic()
        assert not dag_graph_l1_3.is_cyclic()
        assert not dag_graph.is_cyclic()
