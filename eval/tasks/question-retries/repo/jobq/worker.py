import time

from . import settings
from .backoff import delay_for
from .errors import TransientError


def run_job(fn, sleep=time.sleep):
    """Run `fn`, retrying on TransientError. Any other exception propagates immediately."""
    retries = 0
    while True:
        try:
            return fn()
        except TransientError:
            retries += 1
            if retries > settings.max_retries():
                raise
            sleep(delay_for(retries))
