
import logging
import multiprocessing
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from typing import Any, Callable, Dict, List

import psutil

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("Kernel.ProcessingUnit")

class ProcessingUnit:
    """
    Hardware-Optimized Processing Unit for Intel Core i9-13900H & Iris Xe.
    Manages thread pools, process pools, and resource allocation.
    """

    def __init__(self):
        self._cpu_count = multiprocessing.cpu_count()
        # i9-13900H has 6P + 8E = 14 Physical Cores / 20 Threads.
        # Intel Core Optimization:
        # - High-Priority: 6 P-cores (12 threads)
        # - Background: 8 E-cores
        self._p_core_threads = 12
        self._e_core_threads = 8
        self._max_workers = 18 # Optimized for 20-thread system
        self._memory_limit_gb = 16.0
        self._memory_threshold = 0.85 # 85% usage warning

        logger.info("Initializing Hybrid Processing Unit. i9-13900H P-Cores: 6, E-Cores: 8.")
        logger.info("Core Affinity Strategy: High-Priority (12 threads), Standard (8 threads).")

        # High-Priority Pool (Targeting P-Cores)
        self._hi_prio_pool = ThreadPoolExecutor(
            max_workers=self._p_core_threads,
            thread_name_prefix="P_Core_Worker"
        )

        # Standard/Background Pool (Targeting E-Cores)
        self._std_pool = ThreadPoolExecutor(
            max_workers=self._e_core_threads,
            thread_name_prefix="E_Core_Worker"
        )

        # Process pool for CPU bound tasks
        self._ctx = multiprocessing.get_context("spawn")
        self._cpu_pool = ProcessPoolExecutor(
            max_workers=self._p_core_threads // 2, # Conservative for AI tasks
            mp_context=self._ctx
        )

    def check_system_health(self) -> Dict[str, Any]:
        """
        Monitors system resources and performs cleanup if needed.
        """
        import gc
        mem = psutil.virtual_memory()
        cpu_percent = psutil.cpu_percent(interval=None)

        health_status = {
            "cpu_usage": cpu_percent,
            "memory_percent": mem.percent,
            "memory_available_gb": round(mem.available / (1024**3), 2),
            "status": "HEALTHY"
        }

        # Strict RAM Management: Sweep memory if above threshold
        if mem.percent > (self._memory_threshold * 100):
            logger.warning(f"Memory threshold exceeded ({mem.percent}%). Running optimization sweep...")
            gc.collect()
            health_status["status"] = "RECLAIMING"

        if mem.percent > 95.0:
            logger.error("SYSTEM RAM CRITICAL! Denying all new tasks.")
            health_status["status"] = "CRITICAL"

        return health_status

    def submit_task(self, func: Callable, priority: str = "standard", *args, **kwargs):
        """Intel Optimized task submission."""
        health = self.check_system_health()
        if health["status"] == "CRITICAL":
            raise MemoryError("System RAM exhausted. Failed to allocate resource.")

        executor = self._hi_prio_pool if priority == "high" else self._std_pool
        return executor.submit(func, *args, **kwargs)

    def submit_io_task(self, func: Callable, *args, **kwargs):
        """Submit an I/O bound task (Alias for standard priority)."""
        return self.submit_task(func, priority="standard", *args, **kwargs)

    def _pin_to_p_cores(self):
        """Pin the current process/thread to P-Cores for extreme performance."""
        try:
            p = psutil.Process()
            # P-Cores on 13900H are typically the first 12 logical processors (6 physical * 2 hyperthreads)
            p.cpu_affinity(list(range(self._p_core_threads)))
            logger.info("Thread pinned to P-Cores for Quantum-Speed execution.")
        except Exception as e:
            logger.debug(f"Affinity pinning failed: {e}")

    def submit_cpu_task(self, func: Callable, *args, **kwargs):
        """Submit a CPU bound task to the process pool with P-Core affinity."""
        health = self.check_system_health()
        if health["status"] == "CRITICAL":
            logger.error("System under heavy load. Rejecting new CPU task.")
            raise ResourceWarning("System memory critical. Cannot spawn new CPU task.")

        def wrapped_func(*a, **k):
            self._pin_to_p_cores()
            return func(*a, **k)

        return self._cpu_pool.submit(wrapped_func, *args, **kwargs)

    def parallel_map(self, func: Callable, items: List[Any], use_processes: bool = False) -> List[Any]:
        """
        Maps a function over a list of items using parallel execution.
        """
        executor = self._cpu_pool if use_processes else self._io_pool
        results = []

        with executor as pool:
            # We don't use map directly to handle exceptions better if needed
            future_to_item = {pool.submit(func, item): item for item in items}
            for future in as_completed(future_to_item):
                try:
                    results.append(future.result())
                except Exception as exc:
                    logger.error(f"Task generated an exception: {exc}")
                    raise
        return results

    def shutdown(self):
        """Gracefully shutdown pools."""
        logger.info("Shutting down Processing Unit...")
        self._hi_prio_pool.shutdown(wait=True)
        self._std_pool.shutdown(wait=True)
        self._cpu_pool.shutdown(wait=True)
        logger.info("Processing Unit Shutdown Complete.")

# Singleton instance
kernel_pu = ProcessingUnit()
