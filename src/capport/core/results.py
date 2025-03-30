import asyncio
from typing import Coroutine

# MPMC results table. Manages task coroutines
class PipelineResults:
    def __init__(self, labels: list[str]):
        self.started = {x: False for x in labels}
        self.completed = {x: asyncio.Event() for x in labels}
        self.results = {}
        # very rough synchronization currently
        self.started_mutex = asyncio.Lock()
        self.results_mutex = asyncio.Lock()
    
    # waits for all active writers to be done, and gets all written results
    async def get_all(self, labels: str | list[str] | None = None):
        labels == labels or list(self.started.keys())
        if isinstance(labels, str):
            labels = [labels]
        # waiting_for = [ self.completed.get(label) for label in labels ]
        # asyncio.gather(waiting_for)
        for label in labels:
            await self.completed.get(label).wait()
        # get without data race
        results = {
            label: self.results.get(label) for label in labels
        }
        return results
    
    # registers as a writer, and triggers the event once complete, then deregisters.
    async def exec(self, event_label: str, coroutine: Coroutine):
        async with self.started_mutex:
            self.started[event_label] = True
        result = await coroutine
        async with self.results_mutex:
            self.results[event_label] = result
            self.completed[event_label].set()
        return result