from enum import Enum
from typing import Callable

from capport.core.results import PipelineResults
from capport.tools.constants import TAKE_ALL_KEYWORD


class PipelineNodeType(Enum):
    SOURCE = "source"
    SINK = "sink"
    TRANSFORM = "transform"


class PipelineNode:
    @classmethod
    async def _dummy_fn(cls, *args, **kwargs):
        print(args, kwargs)
        return None

    default_callable: Callable = _dummy_fn

    def _get_node_template(self, use: str, node_type: PipelineNodeType) -> Callable:
        if node_type == PipelineNodeType.TRANSFORM:
            print("lookup transformtable for task")
        elif node_type == PipelineNodeType.SOURCE:
            print("lookup sourcetable for task")
        elif node_type == PipelineNodeType.SINK:
            print("lookup sinktable for task")
        # raise Exception("node not found")
        return self.default_callable

    def __init__(
        self,
        use: str,
        node_type: str | PipelineNodeType,
        label: str,
        take_from: dict[str, str] | str = {},
        args: dict = {},
    ):
        self.label = label
        self.node_type = node_type if isinstance(node_type, PipelineNodeType) else PipelineNodeType[node_type.upper()]
        self.template_name = use
        self.take_from = take_from if take_from == TAKE_ALL_KEYWORD else take_from
        self.kwargs = args

    def is_source(self) -> bool:
        return self.node_type == PipelineNodeType.SOURCE

    def is_sink(self) -> bool:
        return self.node_type == PipelineNodeType.SINK

    # The coroutine run by results itself
    async def run(self, results: PipelineResults):
        # waits for events
        # WARNING: results are by reference, nothing is deepcopied
        # ONLY in this poc, an available result is guaranteed to be immutable after being produced.
        # if there are bugs to do with unstable results, please come back to this
        if "^" in self.take_from:
            args = await results.get_all()
        else:
            srcs = list(self.take_from.values())
            args = await results.get_all(srcs)
            print('args', args)
        kwargs = self.kwargs
        use = self._get_node_template(self.template_name, self.node_type)
        await results.exec(self.label, use(*args, **kwargs))