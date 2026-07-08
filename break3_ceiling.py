from tenacity import retry, wait_random_exponential, stop_after_attempt, retry_if_exception_type, before_sleep_log
import logging, time

logging.basicConfig(level=logging.INFO, format="%(asctime)s.%(msecs)03d | %(message)s", datefmt="%H:%M:%S")
logger = logging.getLogger("break3")

class RateLimitError(Exception):
    pass

call_count = {"n": 0}

def flaky_call():
    call_count["n"] += 1
    logger.info(f"[SIMULATED SERVER] Attempt {call_count['n']} -> 429 RATE LIMITED")
    raise RateLimitError(f"429 (attempt {call_count['n']})")

# multiplier=5 means exponential growth is aggressive: 5, 10, 20, 40 seconds theoretically
# but max=8 caps it hard -- proving the ceiling actually clips growth
@retry(
    retry=retry_if_exception_type(RateLimitError),
    wait=wait_random_exponential(multiplier=5, max=8),
    stop=stop_after_attempt(6),
    before_sleep=before_sleep_log(logger, logging.WARNING),
    reraise=True,
)
def call_with_retry():
    return flaky_call()

print("BREAK TEST 3: multiplier=5 (aggressive growth), max=8 (hard ceiling)")
print("Uncapped exponential would demand 5s, 10s, 20s, 40s, 80s -- watch the actual waits below\n")
start = time.time()
try:
    call_with_retry()
except RateLimitError:
    pass
elapsed = time.time() - start
print(f"\nTOTAL WALL TIME: {elapsed:.2f}s (would be ~155s if uncapped and jitter-free)")