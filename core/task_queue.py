import asyncio
import logging
from typing import Callable

from core.rate_limiter import RateLimiter

logger = logging.getLogger("Kernel.TaskQueue")


class VisionTaskQueue:
    """
    Async queue for managing Vision API requests.
    Decouples ingestion from processing to handle high concurrency.
    """

    def __init__(self, concurrency: int = 5):
        self.queue = asyncio.Queue()
        self.concurrency = concurrency
        self.workers = []
        self.limiter = RateLimiter.get_limiter(
            "vision_api", capacity=10, refill_rate=2.0
        )  # 2 requests/sec max
        self.running = False
        self._tasks_processed = 0
        self._tasks_failed = 0

    async def start(self):
        """Start worker consumers."""
        if self.running:
            return

        self.running = True
        self.workers = [
            asyncio.create_task(self._worker(i)) for i in range(self.concurrency)
        ]
        logger.info(f"Vision Task Queue started with {self.concurrency} workers.")

    async def stop(self):
        """Stop workers."""
        self.running = False
        await self.queue.join()
        for w in self.workers:
            w.cancel()
        logger.info("Vision Task Queue stopped.")

    async def submit(self, task_func: Callable, *args, **kwargs) -> asyncio.Future:
        """
        Submit a task to the queue.
        Returns a Future that will eventually hold the result.
        """
        future = asyncio.get_running_loop().create_future()
        await self.queue.put((task_func, args, kwargs, future))
        return future

    async def _worker(self, worker_id: int):
        logger.debug(f"Worker {worker_id} started.")
        while self.running:
            try:
                # Get task
                func, args, kwargs, future = await self.queue.get()

                # Apply Rate Limiting
                await self.limiter.acquire()

                # Execute
                try:
                    if asyncio.iscoroutinefunction(func):
                        result = await func(*args, **kwargs)
                    else:
                        result = await asyncio.to_thread(func, *args, **kwargs)

                    if not future.cancelled():
                        future.set_result(result)
                    self._tasks_processed += 1
                except Exception as e:
                    logger.error(f"Worker {worker_id} failed task: {e}")
                    if not future.cancelled():
                        future.set_exception(e)
                    self._tasks_failed += 1
                finally:
                    self.queue.task_done()

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Worker {worker_id} crash: {e}")
                await asyncio.sleep(1)  # Backoff before restarting

    def get_stats(self) -> dict:
        """Get queue statistics."""
        return {
            "tasks_processed": self._tasks_processed,
            "tasks_failed": self._tasks_failed,
            "queue_size": self.queue.qsize(),
            "workers": self.concurrency,
            "running": self.running,
        }
