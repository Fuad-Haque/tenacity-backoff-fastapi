from retry_demo import call_with_retry, call_count
import time

print("BREAK TEST 1: fail_until_attempt=99 (never succeeds within 5 attempts)")
call_count["n"] = 0
start = time.time()
try:
    call_with_retry(fail_until_attempt=99)
except Exception as e:
    elapsed = time.time() - start
    print(f"\nEXCEPTION TYPE: {type(e).__name__}")
    print(f"EXCEPTION MSG: {e}")
    print(f"TOTAL WALL TIME: {elapsed:.2f}s")
    print(f"TOTAL ATTEMPTS MADE: {call_count['n']}")