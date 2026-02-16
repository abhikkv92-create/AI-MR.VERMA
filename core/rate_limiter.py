import asyncio
import logging
import time

logger = logging.getLogger("Kernel.RateLimiter")

class TokenBucket:
    """
    Async Token Bucket algorithm for rate limiting.
    """
    def __init__(self, capacity: int, refill_rate: float):
        """
        :param capacity: Max tokens in the bucket.
        :param refill_rate: Tokens added per second.
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity
        self.last_refill = time.monotonic()
        self._lock = asyncio.Lock()

    async def acquire(self, tokens: int = 1):
        """
        Acquire tokens. Blocks if not enough tokens are available.
        """
        async with self._lock:
            while True:
                self._refill()
                if self.tokens >= tokens:
                    self.tokens -= tokens
                    return

                # Wait for enough tokens to accumulate
                needed = tokens - self.tokens
                wait_time = needed / self.refill_rate
                logger.debug(f"Rate Limit hit. Waiting {wait_time:.2f}s")
                await asyncio.sleep(wait_time)

    def _refill(self):
        now = time.monotonic()
        elapsed = now - self.last_refill
        new_tokens = elapsed * self.refill_rate

        if new_tokens > 0:
            self.tokens = min(self.capacity, self.tokens + new_tokens)
            self.last_refill = now

class RateLimiter:
    """
    Global Rate Limiter Registry.
    """
    _buckets = {}

    @classmethod
    def get_limiter(cls, key: str, capacity: int = 10, refill_rate: float = 2.0) -> TokenBucket:
        if key not in cls._buckets:
            cls._buckets[key] = TokenBucket(capacity, refill_rate)
        return cls._buckets[key]
