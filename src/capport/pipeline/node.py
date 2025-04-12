from enum import Enum
from typing import Callable, Optional

from capport.pipeline.results import PipelineResults
from capport.tools.constants import TAKE_ALL_KEYWORD
from capport.tools.logger import Logger


class PipelineNodeType(Enum):
    SOURCE = "source"
    SINK = "sink"
    TRANSFORM = "transform"


async def _dummy_fn(*args, **kwargs):
    print(args, kwargs)
    return None


class PipelineNode:
    default_callable: Callable = _dummy_fn

    def _get_node_template(self, use: str, node_type: PipelineNodeType) -> Callable:
        """
        TODO:
        Gets the method of any node by type.
        The signature is always (_this_node: PipelineNode, **kwargs)
        """
        if use == "__noop":
            return self.default_callable
        if node_type == PipelineNodeType.TRANSFORM:
            Logger.debug("lookup transformtable for task")
        elif node_type == PipelineNodeType.SOURCE:
            Logger.debug("lookup sourcetable for task")
        elif node_type == PipelineNodeType.SINK:
            Logger.debug("lookup sinktable for task")
        raise Exception("node not found")

    def __init__(
        self,
        use: str,
        node_type: str | PipelineNodeType,
        label: str,
        take_from: Optional[dict[str, str] | str] = None,
        args: Optional[dict] = None,
    ):
        self.label = label
        self.node_type = node_type if isinstance(node_type, PipelineNodeType) else PipelineNodeType[node_type.upper()]
        self.template_name = use
        take_from = take_from or {}
        self.take_from = take_from if take_from == TAKE_ALL_KEYWORD else take_from
        self.kwargs = args or {}

    def is_source(self) -> bool:
        return self.node_type == PipelineNodeType.SOURCE

    def is_sink(self) -> bool:
        return self.node_type == PipelineNodeType.SINK

    # The coroutine run by results itself
    async def run(self, results: PipelineResults):
        # WARNING: results are by reference, nothing is deepcopied
        # ONLY in this poc, an available result is guaranteed to be immutable after being produced.
        # if there are bugs to do with unstable results, please come back to this
        if "^" in self.take_from:
            myargs = await results.get_all()
        else:
            srcs = list(self.take_from.values())
            deps = await results.get_all(srcs)
            myargs = {new_label: deps.get(result_label) for new_label, result_label in self.take_from.items()}
        kwargs = {**self.kwargs, **myargs}
        use = self._get_node_template(self.template_name, self.node_type)
        await results.exec(self.label, use(**kwargs))
