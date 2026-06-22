from __future__ import annotations

import asyncio
from collections.abc import Callable, Coroutine
from typing import Any

JobCallback = Callable[[], Coroutine[Any, Any, Any]]


class IngestQueue:
    """Fila FIFO assíncrona para jobs de ingestão."""

    def __init__(self) -> None:
        self._queue: asyncio.Queue[JobCallback] = asyncio.Queue()

    async def enqueue(self, callback: JobCallback) -> None:
        await self._queue.put(callback)

    async def worker(self) -> None:
        while True:
            callback = await self._queue.get()
            try:
                await callback()
            except Exception:
                pass
            finally:
                self._queue.task_done()
