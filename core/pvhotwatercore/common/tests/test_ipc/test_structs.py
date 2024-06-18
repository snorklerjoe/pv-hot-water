import pytest
from pvhotwatercore.common.ipc.structs import (
    _MessageType, PingMessage, PushMessage, QueryMessage, Message,
    Response, ResponseType, SimpleResponse
)
from typing import override, Type


def test_message():
    class TestMessage(Message[str]):
        def __init__(self):
            super().__init__(
                message_type=_MessageType.PUSH,
                payload="Test Payload"
            )

        @override
        def validate_response(self, response: Response[Type]) -> bool:
            return True

    test_msg = TestMessage()
    assert isinstance(test_msg, Message)
    assert test_msg.message_type == _MessageType.PUSH
    assert test_msg.payload == "Test Payload"
    assert isinstance(test_msg.payload, str)
    assert test_msg.validate_response(None)

    assert not (
        isinstance(test_msg, PingMessage) or isinstance(
            test_msg, PushMessage) or isinstance(test_msg, QueryMessage)
    )

    with pytest.raises(TypeError):
        Message(_MessageType.PING, 123)


def test_ping_message():
    ping = PingMessage()
    assert ping.message_type == _MessageType.PING
    assert ping.payload is None

    assert ping.validate_response(SimpleResponse(True))
    assert not ping.validate_response(SimpleResponse(False))


def test_push_message():
    payload = "Hello, World!"
    push = PushMessage(payload)
    assert push.message_type == _MessageType.PUSH
    assert push.payload == payload

    assert push.validate_response(SimpleResponse(True))
    assert not push.validate_response(SimpleResponse(False))


def test_query_message():
    class MyStr(str):
        pass
    query = MyStr("SELECT * FROM users")
    query_message = QueryMessage(query)
    assert query_message.message_type == _MessageType.QUERY
    assert query_message.payload == query
    assert isinstance(query_message.payload, MyStr)

    assert query_message.expected_response_type is None
    query_message2 = QueryMessage(query, int)
    assert query_message2.expected_response_type is int

    assert query_message.validate_response(SimpleResponse(True))
    assert not query_message.validate_response(SimpleResponse(False))

    assert not query_message2.validate_response(SimpleResponse(True))
    assert not query_message2.validate_response(SimpleResponse(False))

    assert query_message2.validate_response(Response[int](ResponseType.ACK, 73))


def test_response():
    response_type = ResponseType.ACK
    payload = {"status": "success"}
    response = Response(response_type, payload)
    assert response.response_type == response_type
    assert response.payload == payload


def test_simple_response_with_both_types():
    # Test with True value
    simple_response = SimpleResponse(True)
    assert simple_response.response_type == ResponseType.ACK

    # Test with False value
    simple_response = SimpleResponse(False)
    assert simple_response.response_type == ResponseType.NAK

    # Test with ResponseType valuse:
    # Test with ACK value
    simple_response = SimpleResponse(ResponseType.ACK)
    assert simple_response.response_type == ResponseType.ACK

    # Test with NAK value
    simple_response = SimpleResponse(ResponseType.NAK)
    assert simple_response.response_type == ResponseType.NAK
