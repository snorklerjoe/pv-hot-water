# TODO: Change debug to trace with better logging library
""" Tools for sending messages over a UNIX Domain Socket.
"""

from time import sleep
from multiprocessing.connection import Client
from threading import Lock
from typing import Any, ContextManager, Type, Self, override
import logging
from .structs import Message, Response, InvalidResponseException


__all__ = ['SocketClient']


class SocketClient(ContextManager):
    """A simple client intended for use with SocketServer.

    This implements the context manager protocol (reusable, but not reentrant) and is
    expected to be used as such.
    """

    def __init__(self, addr: str, authkey: bytes) -> None:
        """Initializes the server with a given bind address and authentication secret.
        """
        self.addr: str = addr
        self.authkey: bytes = authkey

        self._lock = Lock()

    def _close(self) -> None:
        """Should be used when done with the object after calling serve_once.
        This is handled automatically if using the typical context manager pattern.

        This should not be called until after all locks are released. Otherwise,
        it will raise a RuntimeError.
        """
        if self._lock.locked():
            raise RuntimeError(
                "Socket Client cannot be closed while a request is underway."
            )

    @override
    def __enter__(self) -> Self:
        return self

    @override
    def __exit__(self, exc_type, exc_value, exc_traceback) -> None:
        self._close()

    def request(
        self,
        message: Message[Type],
        validate_response: bool = True,
        num_retries: int = 10,
        retry_time_delay: float | int = 0
    ) -> Response:
        """Sends a given message and returns the response, if a valid one exists.
        num_retries can be any integer [0,oo)
        TypeError is raised if the response received is not a Response object
        EOFError is raised if the response is unable to be collected
        InvalidResponseException is raised if validate_response is True and the
            validation method in the message object fails.
        """
        response: Response[Any] | None = None
        with self._lock:
            logging.debug(f"Making request to socket at {self.addr}")
            for i in range(num_retries):
                logging.debug(f"Request attempt #{i}")
                try:
                    # Send request; collect response
                    with Client(
                        self.addr,
                        family='AF_UNIX',
                        authkey=self.authkey
                    ) as connection:
                        connection.send(message)
                        resp_unchecked = connection.recv()

                        if isinstance(resp_unchecked, Response):
                            response = resp_unchecked
                        else:
                            raise TypeError(
                                "Response from server is of illegal type "
                                "(not instance of Response)."
                            )

                        # We were successful, no need to retry
                        break
                except ConnectionError as e:
                    if i == num_retries - 1:
                        raise e
                    else:
                        sleep(retry_time_delay)

            # Validate the response
            if response is None:
                raise EOFError("No intelligble response received from server.")

            if (
                validate_response
                and not message.validate_response(response)
            ):
                raise InvalidResponseException(
                    "The Message response validator failed to validate response."
                )

        return response
