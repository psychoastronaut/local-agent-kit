import os

BASE_DELAY = 1.5      # seconds
MAX_DELAY = 10.0      # seconds, cap for the backoff


def max_retries() -> int:
    return int(os.environ.get("JOBQ_MAX_RETRIES", "4"))
