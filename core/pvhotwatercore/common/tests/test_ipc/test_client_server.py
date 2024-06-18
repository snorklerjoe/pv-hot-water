import logging
import threading
import socket
import os
import tempfile
import pytest
from pvhotwatercore.common.ipc.server import SocketServer
from pvhotwatercore.common.ipc.structs import (
    Message, Response, ResponseType, QueryMessage
)
from pvhotwatercore.common.ipc.client import SocketClient


@pytest.fixture(scope="module")
def server_socket():
    """Create a temp file to be used for a UNIX socket"""
    fd, temp_file = tempfile.mkstemp()
    os.close(fd)
    os.unlink(temp_file)
    yield temp_file
    os.unlink(temp_file)


@pytest.fixture(scope="module")
def server_thread(server_socket):
    socket.setdefaulttimeout(1)
    logging.debug("Init'ing fixture for server thread")

    server = SocketServer(server_socket, b"SuperSecret123")

    @server.on_message(QueryMessage)
    def echo(message: Message[str]) -> Response[str]:
        assert isinstance(message.payload, str)
        return Response(ResponseType.ACK, message.payload)

    def serve_forever():
        logging.debug("Starting server forever")
        server.serve_forever()

    thread = threading.Thread(target=serve_forever)
    thread.start()
    yield
    server.shutdown()
    thread.join()


def test_client(server_socket, caplog, server_thread):
    # with SocketClient(server_socket, b"DifferentSecret456") as bad_auth_client:
    #    bad_auth_client.request(QueryMessage("Hello!"))

    caplog.set_level(logging.DEBUG)

    socket.setdefaulttimeout(1)

    with SocketClient(server_socket, b"SuperSecret123") as client:
        resp = client.request(QueryMessage("Hello!"), retry_time_delay=0.01)
        assert resp.response_type == ResponseType.ACK
        assert resp.payload == "Hello!"
