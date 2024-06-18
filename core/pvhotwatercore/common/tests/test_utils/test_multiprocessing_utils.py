from threading import Lock, Thread, Event
from pvhotwatercore.common.utils.multiprocessing_utils import lock_wait


def test_lock_wait():
    lock = Lock()
    lock.acquire()

    done_waiting = Event()

    # Start a separate thread to wait for the lock to release
    def wait():
        lock_wait(lock)
        done_waiting.set()

    assert lock.locked()

    t = Thread(target=wait)
    t.start()

    assert lock.locked()
    assert not done_waiting.is_set()

    # Release the lock:
    lock.release()

    # Could potentially fail if running on a severly underclocked 8086...
    # ...or a dorito...
    # But takes one second on fail.
    assert done_waiting.wait(1)

    assert not lock.locked()
