from . import settings


def delay_for(retry: int) -> float:
    """Delay in seconds before retry number `retry` (1-based): exponential, capped."""
    return min(settings.BASE_DELAY * 2 ** (retry - 1), settings.MAX_DELAY)
