import asyncio

from capport.core.node import PipelineNode
from capport.core.results import PipelineResults
from capport.tools.logger import Logger


class Pipeline:
    # must validate if it is 1. a DAG; 2. has only unique keys
    def validate(self) -> bool:
        return True

    def __init__(self, name: str, node_configs: list[dict]):
        self.name = name
        self.nodes: dict[str, PipelineNode] = {nc["label"]: PipelineNode(**nc) for nc in node_configs}
        # self.sinks = [label for label, node in self.nodes.items() if node.is_sink()]
        self.results = PipelineResults(list(self.nodes.keys()))

    # async runner.
    async def start(self, interactive: bool = True):
        async with asyncio.TaskGroup() as tg:
            for node in self.nodes.values():
                tg.create_task(node.run(self.results))
        if interactive:
            breakpoint()  # pylint:disable=forgotten-debug-statement

    def print_results(self):
        Logger.info(f"Results of {self.name}:")
        for key, val in self.results.results.items():
            print(f"\n{key}:\n{val}")
