import asyncio
from copy import deepcopy

from capport.pipeline.node import PipelineNode
from capport.pipeline.results import PipelineResults
from capport.tools.logger import Logger


class Pipeline:
    def validate(self) -> bool:
        """
        TODO:
        Must meet 2 conditions:
        1. is DAG
        2. all keys are unique
        """
        return True

    def __init__(self, name: str, node_configs: list[dict]):
        """
        node_configs must alr be fully unpacked
        """
        self.name = name
        self.nodes: dict[str, PipelineNode] = {nc["label"]: PipelineNode(**nc) for nc in node_configs}
        self.results = PipelineResults(list(self.nodes.keys()))

    # async runner.
    async def start(self, interactive: bool = True):
        async with asyncio.TaskGroup() as tg:
            for node in self.nodes.values():
                tg.create_task(node.run(self.results))
        if interactive:
            breakpoint()  # pylint:disable=forgotten-debug-statement

    async def clone_results(self):
        Logger.info(f"Results of {self.name}:")
        async with self.results.results_mutex:
            return deepcopy(self.results.results)
