import time
import random
import logging
from tenacity import (
    retry,
    wait_random_exponential,
    stop_after_attempt,
    retry_if_exception_type,
    before_sleep_log,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s.%(msecs)03d | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("retry_demo")


class RateLimitError(Exception):
    """Simulates a 429 Too Many Requests response from an LLM API."""
    pass


# --- CONFIGURATION KNOBS (Section 2 formula lives here) ---
MULTIPLIER = 1      # base seconds
MAX_WAIT = 10        # ceiling in seconds
MAX_ATTEMPTS = 5

# Global counter to control simulated failure pattern
call_count = {"n": 0}


def flaky_api_call(fail_until_attempt: int):
    """Simulates an API that returns 429 for the first N calls, then succeeds."""
    call_count["n"] += 1
    attempt_num = call_count["n"]
    if attempt_num < fail_until_attempt:
        logger.info(f"[SIMULATED SERVER] Attempt {attempt_num} -> 429 RATE LIMITED")
        raise RateLimitError(f"429: rate limit exceeded (attempt {attempt_num})")
    logger.info(f"[SIMULATED SERVER] Attempt {attempt_num} -> 200 OK")
    return {"status": 200, "data": "success", "attempt": attempt_num}


@retry(
    retry=retry_if_exception_type(RateLimitError),
    wait=wait_random_exponential(multiplier=MULTIPLIER, max=MAX_WAIT),
    stop=stop_after_attempt(MAX_ATTEMPTS),
    before_sleep=before_sleep_log(logger, logging.WARNING),
    reraise=True,
)
def call_with_retry(fail_until_attempt: int):
    return flaky_api_call(fail_until_attempt)


if __name__ == "__main__":
    print("=" * 70)
    print("RUN 1: succeeds on 3rd attempt (2 retries)")
    print("=" * 70)
    call_count["n"] = 0
    start = time.time()
    result = call_with_retry(fail_until_attempt=3)
    elapsed = time.time() - start
    print(f"RESULT: {result}")
    print(f"TOTAL WALL TIME: {elapsed:.2f}s\n")