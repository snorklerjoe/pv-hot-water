"""A simple server implementing the communication scheme."""

from typing import override
import socketserver
import os


class _ThreadedCoreIPCDatagramServer(
        socketserver.ThreadingMixIn,
        socketserver.UnixDatagramServer
):
    pass


class _CoreIPCDatagramServer(socketserver.UnixDatagramServer):
    pass


class CoreIPCHandler(socketserver.DatagramRequestHandler):
    """Datagram-based request handler."""

    @override
    def setup(self) -> None:  # noqa: D102
        pass

    @override
    def handle(self) -> None:  # noqa: D102
        pass

    @override
    def finish(self) -> None:  # noqa: D102
        pass


class CoreIPCServer:
    """Datagram-based request server."""

    def __init__(self, addr: str, secret: bytes, threading: bool = False) -> None:
        """Initializes a server.

        If addr is an existing path, it will be unlinked.

        Args:
            addr (str): Address to bind to and listen at
            secret (bytes): An HMAC secret also possessed by the client
            threading (bool): Spawns threads to handle requests
        """
        if os.path.exists(addr):
            os.unlink(addr)

        self.server: socketserver.UnixDatagramServer = (
            _ThreadedCoreIPCDatagramServer(addr, CoreIPCHandler) if threading
            else _CoreIPCDatagramServer(addr, CoreIPCHandler)
        )
