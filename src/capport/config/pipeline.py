"""
PipelineRegistry:

PipelineRegistry will hold a mapping of pipelines to their specs.
The main pipeline produces results to be written into the output dir.

The pipeline only consists of Nodes. Each node's configuration is parsed
by capport/core/node.py currently, so it doesn't have to happen here.

Nodes are of 3 types: source, sink and transform. All nodes are executed as
async tasks (currently signle threaded bc I haven't setup MT).
Each node is of the either form:

---
- label: <unique_node_label>
  use: <template_task>
  args:
    <user_arg_label>: <user_arg_value>
  take_from: # <-- this is mandatory for non-sources, ignored by sources
    <user_arg_label>: <user_arg_value>
- label: <unique_nested_pipeline_label>
  pipeline: <original_pipeline_name>
  take_from: 
    <user_arg_label>: <user_arg_value>
---

What is a template_task? They are the tasks that will actually ingest the
`args`, `take_from` and `output_as` stuff and process the result.
We will be putting them into ./sources/*, ./sinks/* and ./transforms/*

EVERY TEMPLATE TASK MUST BE ASYNC.
"""

from copy import copy
from dataclasses import dataclass

from capport.config.common import ConfigParser
from capport.tools.graph import Edge, Graph, TNode
from capport.tools.logger import Logger


@dataclass
class NodeConfig:
    label: str
    use: str | None
    args: dict | None
    take_from: dict | None


class PipelineParser(ConfigParser):
    pipeline_graph: Graph
    configs: dict[str, list]

    @classmethod
    def assert_valid_stage_config_return_is_final(cls, stage_config: dict) -> bool:
        # shared behaviour
        assert "label" in stage_config
        if "use" in stage_config:
            return True  # final i.e. no more unpacking.
        if "pipeline" in stage_config:
            return False  # non-final i.e. pipeline node.
        raise Exception("Unknown stage type (neither task/pipeline)")

    @classmethod
    def validate_all(cls, config_pages: list[dict[str, dict]]):
        """
        config_pages: page(dict) -> pipeline(str) -> stage(dict)
        Checks no dupes, builds pipeline dependency graph
        """

        all_pipelines = [pipeline for page in config_pages for pipeline in page.items()]
        for _, pipeline in all_pipelines:
            for stage in pipeline:
                if "label" not in stage:
                    raise Exception(f"label not found in stage: {stage}")
                if not isinstance(stage.get("label"), str):
                    raise Exception(f"label not cstr in stage: {stage}")
        all_pipeline_names = [name for name, _ in all_pipelines]
        cls.pipeline_names = all_pipeline_names

        cls.assert_no_duplicates(all_pipeline_names)
        tnodes = dict(all_pipelines)
        edges = []
        for name, pipeline in tnodes.items():
            for stage in pipeline:
                if "pipeline" in stage:
                    pfrom = name
                    pto = stage.get("pipeline")
                    assert isinstance(pto, str)
                    edges.append(Edge(pfrom, pto))
        cls.pipeline_graph = Graph(tnodes, edges)
        cls.configs = tnodes
        assert not cls.pipeline_graph.is_cyclic()

    @classmethod
    def parse_all(cls, config_pages: list[dict[str, dict]]):
        """
        Builds all unique stages that pipelines later utilize to build.
        At this point the correctness/availability of each stage's requested take_from variables isn't handled yet.
        """
        cls.unique_stages: dict[str, NodeConfig] = {}
        if not cls.pipeline_graph or not cls.configs:
            Logger.warn("Running validate_all first...")
            cls.validate_all(config_pages)
        Logger.log(f"Processing pipelines: {[k.key for k in cls.pipeline_graph.table.values()]}")

        def build_nodes(pipeline: TNode, pipeline_id: str, label_stack: list[str]):
            label_stack.append(pipeline_id)
            stages = [(stage, cls.assert_valid_stage_config_return_is_final(stage)) for stage in pipeline.value]
            final_stages = [stage for stage, is_final in stages if is_final]
            nested_pipeline_stages = [stage for stage, is_final in stages if not is_final]
            for stage in final_stages:
                ukey = f"{'.'.join(label_stack)}.{stage.get('label')}"
                cls.unique_stages[ukey] = NodeConfig(
                    label=ukey,
                    use=stage.get("use"),
                    args=stage.get("args"),
                    take_from=stage.get("take_from"),
                )
            for stage in nested_pipeline_stages:
                ukey = f"{'.'.join(label_stack)}.{stage.get('label')}"
                cls.unique_stages[ukey] = NodeConfig(
                    label=ukey,
                    use="convert_vars",  # TODO: Replace with standard conversion use node name
                    args=stage.get("args"),
                    take_from=stage.get("take_from"),
                )
                # breakpoint()
                build_nodes(cls.pipeline_graph.table[stage.get("pipeline")], stage.get("label"), label_stack)
            label_stack.pop()

        label_stack = []
        for pipeline in cls.pipeline_graph.table.values():
            build_nodes(pipeline, pipeline.key, label_stack)

    @classmethod
    def validate(cls, config_id: str):
        # first validate no duplicate unique_stages at all
        ukeys = [u.key for u in cls.unique_stages]
        cls.assert_no_duplicates(ukeys)

        if config_id not in cls.pipeline_graph.table:
            raise Exception(f"{config_id} not found amongst pipelines: [{cls.pipeline_names}]")

        cls.unique_stage_table = {u.key: u for u in cls.unique_stages}
        pipeline = cls.pipeline_graph.table.get(config_id).value
