"""An IPC message protocol."""

from dataclasses import dataclass
from enum import Enum, auto, unique
from typing import TypeVar, Generic, Type, override
from abc import ABC, abstractmethod


class InvalidResponseException(Exception):
    """An illegal or otherwise invalid response was received."""

    def __init__(self, *args: object) -> None:
        """Inits an InvalidResponseException.

        Passes all args to Exception.__init__().
        """
        super().__init__(*args)


@unique
class _MessageType(Enum):
    """Types of messages.

    These convey what sort of response is to be expected within this protocol
    """
    PING = auto()
    PUSH = auto()
    QUERY = auto()


T = TypeVar("T")
U = TypeVar("U")


@unique
class ResponseType(Enum):
    """Types of responses.

    An ACK is always expected if the message was received and successfully
    authenticated and validated. A NAK is not otherwise necessarily expected.
    An ACK does not mean the response was processed successfully. Only that the
    information got across.
    """
    ACK = auto()
    NAK = auto()


@dataclass
class Response(Generic[T]):
    """A response to a Message."""
    response_type: ResponseType
    payload: T


class SimpleResponse(Response[None]):
    """A simple, ACK or NAK response."""

    def __init__(self, value: bool | ResponseType) -> None:
        """Specify either True or ACK, or False or NAK."""
        if isinstance(value, ResponseType):
            super().__init__(value, None)
        else:
            super().__init__(ResponseType.ACK if value else ResponseType.NAK, None)


@dataclass
class Message(Generic[T], ABC):
    """A message to be sent between processes."""
    message_type: _MessageType
    payload: T

    @abstractmethod
    def validate_response(self, response: Response[Type]) -> bool:
        """Returns True if valid response to this Message."""


class PingMessage(Message[None]):
    """An empty test message that expects an ACK back and nothing more."""

    def __init__(self) -> None:
        """Initializes a PingMessage with an empty payload."""
        super().__init__(message_type=_MessageType.PING, payload=None)

    @override
    def validate_response(self, response: Response[Type]) -> bool:
        """Returns True if valid response to this Message.

        Specifically, for PingMessage objects, a response will be valid if it is an ACK.

        Args:
            response (Response[Type]): Response to validate

        Returns:
            bool: True if valid.
        """
        return response.response_type == ResponseType.ACK


class PushMessage(Generic[U], Message[U]):
    """A message that just drops off an object and expects an empty ACK or NAK back."""

    def __init__(self, payload: U) -> None:
        """Initializes a PushMessage with a given payload.

        Args:
            payload (U): the data to push in the message.
        """
        super().__init__(message_type=_MessageType.PUSH, payload=payload)

    @override
    def validate_response(self, response: Response[Type]) -> bool:
        """Returns True if valid response to this Message.

        Specifically, for PushMessage objects, a response will be valid if it is an ACK.

        Args:
            response (Response[Type]): Response to validate

        Returns:
            bool: True if valid.
        """
        return response.response_type == ResponseType.ACK


class QueryMessage(Message[U]):
    """A message eliciting a specific type of payload back."""

    def __init__(self, query: U, response_payload_type: Type | None = None) -> None:
        """Initializes a QueryMessage.

        The query (whatever type that may be is not specific to this transport layer)
        and, optionally, the expected type of the response must be provided.

        Args:
            query (U): The query to be given to the server.
            response_payload_type (Type | None, optional): The type of response
                expected. Defaults to None.
        """
        super().__init__(message_type=_MessageType.QUERY, payload=query)
        self.expected_response_type: Type | None = response_payload_type

    @override
    def validate_response(self, response: Response[Type]) -> bool:
        """Returns True if valid response to this Message.

        Specifically, for QueryMessage objects, a response will be valid if it is an ACK
        and the payload is of a specific type (if applicable).

        Args:
            response (Response[Type]): Response to validate

        Returns:
            bool: True if valid.
        """
        return (
            response.response_type == ResponseType.ACK
            and (
                self.expected_response_type is None
                or isinstance(response.payload, self.expected_response_type)
            )
        )
