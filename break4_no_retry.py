from tenacity import retry, wait_random_exponential, stop_after_attempt, retry_if_exception_type, before_sleep_log
import logging, time

logging.basicConfig(level=logging.INFO, format="%(asctime)s.%(msecs)03d | %(message)s", datefmt="%H:%M:%S")
logger = logging.getLogger("break4")

class RateLimitError(Exception):
    pass

call_count = {"n": 0}

def flaky_call():
    call_count["n"] += 1
    logger.info(f"[SIMULATED SERVER] Attempt {call_count['n']} -> 429 RATE LIMITED")
    raise RateLimitError(f"429 (attempt {call_count['n']})")

@retry(
    retry=retry_if_exception_type(RateLimitError),
    wait=wait_random_exponential(multiplier=1, max=10),
    stop=stop_after_attempt(1),  # only 1 attempt total -- zero retries
    before_sleep=before_sleep_log(logger, logging.WARNING),
    reraise=True,
)
def call_with_retry():
    return flaky_call()

print("BREAK TEST 4: stop_after_attempt=1 -- the decorator is present but retry never fires")
start = time.time()
try:
    call_with_retry()
except RateLimitError as e:
    elapsed = time.time() - start
    print(f"\nEXCEPTION: {e}")
    print(f"TOTAL WALL TIME: {elapsed:.4f}s")
    print(f"TOTAL ATTEMPTS MADE: {call_count['n']}")
    print("Decorator present but functionally inert -- looks like retry logic, behaves like none")