import asyncio
from copy import deepcopy
from typing import Coroutine


# MPMC results table. Manages task coroutines
class PipelineResults:
    def __init__(self, labels: list[str]):
        self.started = {x: False for x in labels}
        self.completed = {x: asyncio.Event() for x in labels}
        self.results = {}
        # very coarse grained synchronization currently
        self.started_mutex = asyncio.Lock()
        self.results_mutex = asyncio.Lock()

    # waits for all active writers to be done, and gets all written results
    async def get_all(self, labels: str | list[str] | None = None):
        started = [label for label, is_started in self.started.items() if is_started]
        labels = labels or started
        if isinstance(labels, str):
            labels = [labels]
        for label in labels:
            await self.completed.get(label).wait()
        # get without data race
        # hate that python does this
        results = {label: deepcopy(self.results.get(label)) for label in labels}
        print(results)
        return results

    # registers as a writer, and triggers the event once complete, then deregisters.
    async def exec(self, event_label: str, coroutine: Coroutine):
        async with self.started_mutex:
            self.started[event_label] = True
        result = await coroutine
        async with self.results_mutex:
            # hate that python does this
            self.results[event_label] = deepcopy(result)
            self.completed[event_label].set()
        return result
