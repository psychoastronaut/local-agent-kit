import pytest

from jobq.errors import PermanentError, TransientError
from jobq.worker import run_job


def test_succeeds_after_transient():
    calls = []

    def flaky():
        calls.append(1)
        if len(calls) < 3:
            raise TransientError()
        return "ok"

    assert run_job(flaky, sleep=lambda s: None) == "ok"


def test_permanent_not_retried():
    with pytest.raises(PermanentError):
        run_job(lambda: (_ for _ in ()).throw(PermanentError()), sleep=lambda s: None)
