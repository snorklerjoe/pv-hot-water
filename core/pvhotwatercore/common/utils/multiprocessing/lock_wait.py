"""Generic utilities for multiprocessing."""

from threading import Lock

__all__ = ['lock_wait']


def lock_wait(lock: Lock) -> None:
    """Acquires a lock, releases it, then exits."""
    if lock.locked():
        lock.acquire()
        lock.release()
