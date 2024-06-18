# TODO: Change debug to trace with better logging library
""" Tools for sending messages over a UNIX Domain Socket.
"""
from threading import Event, Lock
from multiprocessing.connection import Listener
from typing import (
    Any, Callable, ContextManager, Dict, Type, Self, override, TypeVar, cast
)
import logging
from pvhotwatercore.common.utils.multiprocessing_utils import lock_wait

from .structs import Message, Response


# New Python type aliases (not yet supported by mypy, so the old way for now...)
type Timeout = float | int | None  # type: ignore [valid-type]
type MessageCallback = Callable[[Message[Type]],  # type: ignore [valid-type]
                                Response[Any]]

T = TypeVar("T")


class SocketServer(ContextManager):
    """A simple unthreaded server that can watch for incoming information and respond
    with the return value of a callback.

    This implements the context manager protocol (reusable, but not reentrant) and is
    expected to be used as such.
    A listener is not opened until the __enter__() method is called.
    """

    def __init__(self, addr: str, authkey: bytes) -> None:
        """Initializes the server with a given bind address and authentication secret.
        """
        self.listener: Listener | None = None
        self.addr: str = addr
        self.authkey: bytes = authkey

        # Maps a T of Message[T] to a callback
        self.callbacks: Dict[Type[Message], MessageCallback] = {}

        # Bind lock
        self._lock: Lock = Lock()
        # Secondary lock for serve_forever()
        self._forever_lock: Lock = Lock()

        # Shutdown flag
        self._shutdown: Event = Event()

        logging.debug(f"Initialized socket server to listen on {addr}")

    def _close(self) -> None:
        """Should be used when done with the object after calling serve_once.
        This is handled automatically if using the typical context manager pattern.

        This should not be called until after all locks are released. Otherwise,
        it will raise a RuntimeError.
        """
        if self._lock.locked() or self._forever_lock.locked():
            raise RuntimeError(
                "Socket Server cannot be closed while serving clients."
                "Please shutdown() first.")
        if self.listener is not None:
            self.listener.close()
            self.listener = None
        logging.debug("Closed socket server")

    def _create_listener(self) -> Listener:
        logging.debug(f"Creating socket listener for {self.addr}")
        return Listener(self.addr, family='AF_UNIX', authkey=self.authkey)

    @override
    def __enter__(self) -> Self:
        self.listener = self._create_listener()
        return self

    @override
    def __exit__(self, exc_type, exc_value, exc_traceback) -> None:
        self._close()

    def shutdown(self) -> None:
        """Blocks until any server stuff finishes and then returns.
        """
        # Tell everything it's time to wrap up...
        self._shutdown.set()
        # Wait until locks are freed up
        lock_wait(self._lock)
        lock_wait(self._forever_lock)
        # Close the listener
        self._close()
        logging.debug("Shut down socket server.")

    def on_message(self, response_type: Type[Any]):
        """A decorator for the callback to process a Message and return a Response."""
        def _wrapper(callback: MessageCallback):
            # Registers a callback for this type:
            self.callbacks[response_type] = callback
            logging.debug(f"Registered socket server callback for type {response_type}")
        return _wrapper

    def _choose_callback(  # type: ignore [valid-type]
        self,
        obj: Message[Any]
    ) -> MessageCallback | None:
        """Choose a callback appropriate for handling a given object.
        returns None if none can be found.
        """
        # If one exists for this specific subclass, go with it
        if type(obj) in self.callbacks:
            return self.callbacks[
                cast(Type[Message], type(obj))
            ]
        # Otherwise, see if there is a registered callback for a supertype
        for key in self.callbacks:
            if isinstance(obj, key):
                return self.callbacks[key]

        # None found; return None
        return None

    def serve_once(self, recv_timeout: Timeout = None) -> None:
        """Blocks until the next message is received, then processes it via registered
        callbacks.

        Waiting to accept a connection from the client will block until the
        socket default timeout (see socket.setdefaulttimeout()).

        A connection will be dropped if it is initiated but nothing is received
        within `recv_timeout` seconds.

        Because a lock is accquired, multiple instances of this cannot run concurrently.

        Raises EOFError if the client disconnects early.
        Raises KeyError if an appropriate callback is not registered.
        Raises AuthenticationError if a client is improperly authenticated.
        """
        logging.debug("Waiting for server lock")
        with self._lock:
            if self.listener is None:
                self.listener = self._create_listener()

            logging.debug(f"Listening for one connection on {self.addr}")

            with self.listener.accept() as connection:
                logging.debug(f"Accepted connection from {self.listener.last_accepted}")
                if recv_timeout is not None and not connection.poll(recv_timeout):
                    return
                recvd_object: Any = connection.recv()
                callback: MessageCallback | None = self._choose_callback(recvd_object)
                if callback is None:
                    raise KeyError("No suitable callback found for received object.")

                # Run the callback to process the request
                logging.debug("Processing request")
                response: Response[Any] = callback(recvd_object)

                # Return the response back to the client
                # (the callback is responsible for making sure it makes sense!)
                logging.debug(f"Sending response to {self.listener.last_accepted}")
                connection.send(response)

    def serve_forever(self) -> None:
        """ Serves "forever."
        Upon receiving a shutdown signal, it will wait until the last transaction is
        finished and then it will return. If it is waiting to accept a new client
        connection, it will take at least the default socket timeout to shutdown.

        While waiting for a connection from a client, it will poll the shutdown flag
        at the poll interval. A poll interval of None will not check the shutdown flag.

        This must only be run from a single thread.
        """
        with self._forever_lock:
            logging.debug(f"Serving forever on {self.addr}")
            while not self._shutdown.is_set():
                # Serve a client:
                self.serve_once()
