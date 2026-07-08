from tenacity import retry, wait_random_exponential, stop_after_attempt, retry_if_exception_type, before_sleep_log
import logging, time

logging.basicConfig(level=logging.INFO, format="%(asctime)s.%(msecs)03d | %(message)s", datefmt="%H:%M:%S")
logger = logging.getLogger("break2")

class RateLimitError(Exception):
    pass

class AuthError(Exception):
    """A 401 -- not a rate limit. Retrying this is pointless and wastes time."""
    pass

call_count = {"n": 0}

def flaky_call():
    call_count["n"] += 1
    logger.info(f"[SIMULATED SERVER] Attempt {call_count['n']} -> 401 UNAUTHORIZED")
    raise AuthError("401: invalid API key")

@retry(
    retry=retry_if_exception_type(RateLimitError),  # only retries RateLimitError
    wait=wait_random_exponential(multiplier=1, max=10),
    stop=stop_after_attempt(5),
    before_sleep=before_sleep_log(logger, logging.WARNING),
    reraise=True,
)
def call_with_retry():
    return flaky_call()

print("BREAK TEST 2: server returns AuthError, retry predicate only matches RateLimitError")
start = time.time()
try:
    call_with_retry()
except Exception as e:
    elapsed = time.time() - start
    print(f"\nEXCEPTION TYPE: {type(e).__name__}")
    print(f"TOTAL WALL TIME: {elapsed:.4f}s")
    print(f"TOTAL ATTEMPTS MADE: {call_count['n']}")