from typing import Callable, Optional

from capport.pipeline.results import PipelineResults
from capport.tools.constants import TAKE_ALL_KEYWORD
from capport.config import StageConfig


async def _dummy_fn(*args, **kwargs):
    print(args, kwargs)
    return None


class PipelineNode:
    default_callable: Callable = _dummy_fn

    def _get_node_template(self, use: str) -> Callable:
        """
        TODO:
        Gets the method of any node by type.
        The signature is always (_this_node: PipelineNode, **kwargs)
        """
        if use == "__noop":
            return self.default_callable
        raise Exception("node not found")

    def __init__(
        self,
        config: StageConfig
    ):
        self.label = config.label
        self.template_name = config.use
        take_from = config.take_from or {}
        self.take_from = take_from if take_from == TAKE_ALL_KEYWORD else take_from
        self.kwargs = config.args or {}

    async def run(self, results: PipelineResults):
        if "^" in self.take_from:
            myargs = await results.get_all()
        else:
            srcs = list(self.take_from.values())
            deps = await results.get_all(srcs)
            myargs = {new_label: deps.get(result_label) for new_label, result_label in self.take_from.items()}
        kwargs = {**self.kwargs, **myargs}
        use = self._get_node_template(self.template_name)
        # The coroutine is executed by `results`
        await results.exec(self.label, use(**kwargs))
