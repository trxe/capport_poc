"""
PipelineRegistry will hold a mapping of pipelines to their specs.
The main pipeline produces results to be written into the output dir.

What is a template_task? They are the tasks that will actually ingest the
`args`, `take_from` and `output_as` stuff and process the result.
We will be putting them into ./sources/*, ./sinks/* and ./transforms/*

EVERY TEMPLATE TASK MUST BE ASYNC.
"""

from dataclasses import dataclass

from capport.config.common import ConfigParser
from capport.tools.graph import Edge, Graph, TNode
from capport.tools.logger import Logger


@dataclass
class StageConfig:
    label: str
    use: str | None
    args: dict | None
    take_from: dict | None


@dataclass
class PipelineConfig:
    label: str
    stages: list[StageConfig]


class PipelineParser(ConfigParser):
    pipeline_graph: Graph
    configs: dict[str, PipelineConfig]

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
        cls.unique_stages: dict[str, StageConfig] = {}
        if not cls.pipeline_graph or not cls.configs:
            Logger.warn("Running validate_all first...")
            cls.validate_all(config_pages)
        Logger.log(f"Processing pipelines: {[k.key for k in cls.pipeline_graph.table.values()]}")

        def build_nodes(pipeline: TNode, pipeline_id: str, label_stack: list[str], stage_list: list[str]):
            label_stack.append(pipeline_id)
            for stage in pipeline.value:
                ukey = f"{'.'.join(label_stack)}.{stage.get('label')}"
                if ukey in cls.unique_stages:
                    raise Exception(f"Error: pipeline node key collision: {ukey}")
                is_final = cls.assert_valid_stage_config_return_is_final(stage)
                stage_list.append(ukey)
                if is_final:
                    cls.unique_stages[ukey] = StageConfig(
                        label=ukey,
                        use=stage.get("use"),
                        args=stage.get("args"),
                        take_from=stage.get("take_from"),
                    )
                else:
                    cls.unique_stages[ukey] = StageConfig(
                        label=ukey,
                        use="convert_vars",  # TODO: Replace with standard conversion use node name
                        args=stage.get("args"),
                        take_from=stage.get("take_from"),
                    )
                    build_nodes(
                        cls.pipeline_graph.table[stage.get("pipeline")], stage.get("label"), label_stack, stage_list
                    )
            label_stack.pop()

        cls.configs = {}
        label_stack = []
        for pipeline in cls.pipeline_graph.table.values():
            stage_list = []
            build_nodes(pipeline, pipeline.key, label_stack, stage_list)
            cls.configs[pipeline.key] = PipelineConfig(pipeline.key, [cls.unique_stages[k] for k in stage_list])

    @classmethod
    def get_config(cls, config_key: str) -> PipelineConfig:
        if config_key not in cls.pipeline_graph.table:
            raise Exception(
                f"Pipeline not initialized: {config_key}, not found "
                f"amongst initialized configs: {list(cls.pipeline_graph.table.keys())}"
            )
        return cls.configs[config_key]
