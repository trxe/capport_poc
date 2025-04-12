from typing import Optional

import pytest
import pytest_asyncio

from capport.config.pipeline import PipelineParser
from capport.pipeline.node import PipelineNode
from capport.pipeline.pipeline import Pipeline
from capport.tools.constants import NOOP_KEYWORD


async def select_value_label_type(_node: PipelineNode, **kwargs) -> any:
    response = kwargs
    if "value" in kwargs:
        value = kwargs.get("value")
        response = value
        if value and "select" in kwargs:
            res = value.get(kwargs.get("select", "?"))
            if res:
                response = res
    if isinstance(response, dict):
        response["node_name"] = _node.label
    return response


@pytest.fixture(scope="class")
def setup_select_value_label_type():
    PipelineNode.default_callable = select_value_label_type


class PipelineBuilder:

    default_use = NOOP_KEYWORD

    @classmethod
    def create_node_config(
        cls,
        label: str,
        args: Optional[dict] = None,
        take_from: Optional[dict] = None,
        use: str = default_use,
    ):
        return {
            "label": label,
            "use": use,
            "args": args or {},
            "take_from": take_from,
        }

    @classmethod
    def create_pipeline_node_config(
        cls,
        label: str,
        pipeline: str,
        args: Optional[dict] = None,
        take_from: Optional[dict] = None,
    ):
        return {
            "label": label,
            "pipeline": pipeline,
            "args": args or {},
            "take_from": take_from,
        }

    @classmethod
    def branch_to_children(
        cls, label_prefix: str, select_key: str, count: int, parent_conf: dict
    ) -> list[dict]:
        return [
            cls.create_node_config(
                label=f"{label_prefix}_{idx}",
                args={"select": select_key},  # this becomes kwargs in the node.
                # i.e. parent must produce a dict with the select_key
                take_from={"value": parent_conf.get("label")},  # this becomes args in the node.
            )
            for idx in range(1, count + 1)
        ]

    @classmethod
    def merge_to_child(cls, label: str, parent_confs: list[dict]) -> dict:
        chosen_idx = len(parent_confs) // 2
        take_from = {("value" if i == chosen_idx else f"{i}"): node.get("label") for i, node in enumerate(parent_confs)}
        return cls.create_node_config(
            label=label,
            args={"select": "return_whole_value"},  # this becomes kwargs in the node.
            take_from=take_from,
        )

    @classmethod
    def create_single_path(cls, label: str, levels: int, input_value: any) -> list[dict]:
        nodelist = [cls.create_node_config(label, args={"value": input_value})]
        for i in range(1, levels):
            nodelist.append(
                cls.create_node_config(
                    f"{label}_{i}",
                    args={"select": "?"},
                    take_from={"value": nodelist[-1].get("label")},
                )
            )
        nodelist.append(
            cls.create_node_config(
                f"{label}_{levels}",
                args={"select": "?"},
                take_from={"value": nodelist[-1].get("label")},
            )
        )
        return nodelist

    @classmethod
    def create_branching_layer_with_root_and_sink(cls, label: str, count: int, input_value: any) -> list[dict]:
        nodelist = [cls.create_node_config(label, args={"value": input_value})]
        children = cls.branch_to_children(
            label,
            count=count,
            select_key="?",
            parent_conf=nodelist[0],
        )
        nodelist.extend(children)
        nodelist.append(cls.merge_to_child(label=f"{label}_sink", parent_confs=children))
        return nodelist


class TestPipelineConfig:
    def test_config_single_path_valid(self):
        config = [
            PipelineBuilder.create_node_config("A", args={"value": 12}),
            PipelineBuilder.create_node_config("B", args={"select": "?"}, take_from={"value": "A"}),
            PipelineBuilder.create_node_config("C", args={"select": "?"}, take_from={"value": "B"}),
            PipelineBuilder.create_node_config("D", args={"select": "?"}, take_from={"value": "C"}),
        ]

        def assert_pipeline_config(config_pages):
            PipelineParser.validate_all(config_pages)
            PipelineParser.parse_all(config_pages)
            assert set(PipelineParser.unique_stages.keys()) == set(
                [
                    f"{plname}.{stage.get('label')}"
                    for page in config_pages
                    for plname, stages in page.items()
                    for stage in stages
                ]
            )

        assert_pipeline_config([{"main": config, "alt": config}])
        assert_pipeline_config([{"alt": config}, {"main": config}])

    def test_config_nested_pipelines_valid(self):
        config_main = [
            PipelineBuilder.create_node_config("A", use="a"),
            # nested pipeline with label identical to label.
            # take_from keys must be unique from the stages in the sub pipeline
            PipelineBuilder.create_pipeline_node_config("alt", "alt", take_from={"main": "A"}),
            PipelineBuilder.create_node_config("C", use="c", take_from={"value": "B"}),
            PipelineBuilder.create_node_config("D", use="d", take_from={"value": "C"}),
        ]
        config_alt = [
            PipelineBuilder.create_node_config("A", use="a"),
            PipelineBuilder.create_node_config("B", use="b", take_from={"value": "main"}),
            # nested pipeline with label identical to current pipeline label, but pipeline name is different
            PipelineBuilder.create_pipeline_node_config(
                "alt", "alt2", take_from={"alt": "A", "main": "B", "orig": "main"}
            ),
        ]
        config_alt2 = [
            PipelineBuilder.create_node_config(
                "alt2", use="e", take_from={"secondary": "alt", "primary": "main", "orig": "orig"}
            ),
        ]

        def assert_pipeline_config(config_pages):
            PipelineParser.validate_all(config_pages)
            PipelineParser.parse_all(config_pages)
            assert set(PipelineParser.unique_stages.keys()) == set(
                [
                    "main.A",
                    "main.alt",
                    "main.alt.A",
                    "main.alt.B",
                    "main.alt.alt",
                    "main.alt.alt.alt2",
                    "main.C",
                    "main.D",
                    "alt.A",
                    "alt.B",
                    "alt.alt",
                    "alt.alt.alt2",
                    "alt2.alt2",
                ]
            )

        assert_pipeline_config([{"main": config_main, "alt": config_alt, "alt2": config_alt2}])
        assert_pipeline_config([{"alt": config_alt}, {"main": config_main, "alt2": config_alt2}])


class TestPipeline:
    @pytest.mark.asyncio
    async def test_single_path(self, setup_select_value_label_type):
        input_value = {"mykey": ["A", "B", "C", "f"]}
        config = PipelineBuilder.create_single_path("woops", 3, input_value)
        pipeline = Pipeline("single_path", config)
        await pipeline.start(interactive=False)
        actual = await pipeline.clone_results()
        expected = {
            "woops": {**input_value, "node_name": "woops"},
            "woops_1": {**input_value, "node_name": "woops_1"},
            "woops_2": {**input_value, "node_name": "woops_2"},
            "woops_3": {**input_value, "node_name": "woops_3"},
        }
        assert actual == expected

    @pytest.mark.asyncio
    async def test_one_branching_layer_and_one_merge_sink(self, setup_select_value_label_type):
        input_value = {"mykey": ["A", "B", "C", "f"]}
        config = PipelineBuilder.create_branching_layer_with_root_and_sink("woops", 3, input_value)
        pipeline = Pipeline("single_path", config)
        await pipeline.start(interactive=False)
        actual = await pipeline.clone_results()
        expected = {
            "woops": {**input_value, "node_name": "woops"},
            "woops_1": {**input_value, "node_name": "woops_1"},
            "woops_2": {**input_value, "node_name": "woops_2"},
            "woops_3": {**input_value, "node_name": "woops_3"},
            "woops_sink": {**input_value, "node_name": "woops_sink"},
        }
        assert actual == expected
