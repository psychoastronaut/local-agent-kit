class JobError(Exception):
    """Base class for job failures."""


class TransientError(JobError):
    """Temporary failure (network blip, lock timeout): worth retrying."""


class PermanentError(JobError):
    """Bad input or a bug: retrying cannot help."""
