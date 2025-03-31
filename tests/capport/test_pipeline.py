from typing import Optional

import pytest
import pytest_asyncio

from capport.pipeline.node import PipelineNode, PipelineNodeType
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
        response["node_type"] = _node.node_type
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
        node_type: str,
        args: Optional[dict] = None,
        take_from: Optional[dict] = None,
        use: str = default_use,
    ):
        return {
            "label": label,
            "node_type": node_type,
            "use": use,
            "args": args or {},
            "take_from": take_from,
        }

    @classmethod
    def branch_to_children(
        cls, label_prefix: str, node_type: str, select_key: str, count: int, parent_conf: dict
    ) -> list[dict]:
        return [
            cls.create_node_config(
                label=f"{label_prefix}_{idx}",
                node_type=node_type,
                args={"select": select_key},  # this becomes kwargs in the node.
                # i.e. parent must produce a dict with the select_key
                take_from={"value": parent_conf.get("label")},  # this becomes args in the node.
            )
            for idx in range(1, count + 1)
        ]

    @classmethod
    def merge_to_child(cls, label: str, node_type: str, parent_confs: list[dict]) -> dict:
        chosen_idx = len(parent_confs) // 2
        take_from = {("value" if i == chosen_idx else f"{i}"): node.get("label") for i, node in enumerate(parent_confs)}
        return cls.create_node_config(
            label=label,
            node_type=node_type,
            args={"select": "return_whole_value"},  # this becomes kwargs in the node.
            take_from=take_from,
        )

    @classmethod
    def create_single_path(cls, label: str, levels: int, input_value: any):
        nodelist = [cls.create_node_config(label, "source", args={"value": input_value})]
        for i in range(1, levels):
            nodelist.append(
                cls.create_node_config(
                    f"{label}_{i}",
                    "transform",
                    args={"select": "?"},
                    take_from={"value": nodelist[-1].get("label")},
                )
            )
        nodelist.append(
            cls.create_node_config(
                f"{label}_{levels}",
                "sink",
                args={"select": "?"},
                take_from={"value": nodelist[-1].get("label")},
            )
        )
        return nodelist

    @classmethod
    def create_branching_layer_with_root_and_sink(cls, label: str, count: int, input_value: any):
        nodelist = [cls.create_node_config(label, "source", args={"value": input_value})]
        children = cls.branch_to_children(
            label,
            "transform",
            count=count,
            select_key="?",
            parent_conf=nodelist[0],
        )
        nodelist.extend(children)
        nodelist.append(cls.merge_to_child(label=f"{label}_sink", node_type="sink", parent_confs=children))
        return nodelist


class TestPipeline:
    @pytest.mark.asyncio
    async def test_single_path(self, setup_select_value_label_type):
        input_value = {"mykey": ["A", "B", "C", "f"]}
        config = PipelineBuilder.create_single_path("woops", 3, input_value)
        pipeline = Pipeline("single_path", config)
        await pipeline.start(interactive=False)
        actual = await pipeline.clone_results()
        expected = {
            "woops": {**input_value, "node_type": PipelineNodeType.SOURCE, "node_name": "woops"},
            "woops_1": {**input_value, "node_type": PipelineNodeType.TRANSFORM, "node_name": "woops_1"},
            "woops_2": {**input_value, "node_type": PipelineNodeType.TRANSFORM, "node_name": "woops_2"},
            "woops_3": {**input_value, "node_type": PipelineNodeType.SINK, "node_name": "woops_3"},
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
            "woops": {**input_value, "node_type": PipelineNodeType.SOURCE, "node_name": "woops"},
            "woops_1": {**input_value, "node_type": PipelineNodeType.TRANSFORM, "node_name": "woops_1"},
            "woops_2": {**input_value, "node_type": PipelineNodeType.TRANSFORM, "node_name": "woops_2"},
            "woops_3": {**input_value, "node_type": PipelineNodeType.TRANSFORM, "node_name": "woops_3"},
            "woops_sink": {**input_value, "node_type": PipelineNodeType.SINK, "node_name": "woops_sink"},
        }
        assert actual == expected
