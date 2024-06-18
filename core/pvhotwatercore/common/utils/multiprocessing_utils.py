""" Some generic utilities for multiprocessing-related stuff
"""

from threading import Lock

__all__ = ['lock_wait']


def lock_wait(lock: Lock):
    """Acquires a lock, releases it, then exits."""
    if lock.locked():
        lock.acquire()
        lock.release()
