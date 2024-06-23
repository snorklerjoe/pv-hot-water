"""Session-layer data structures.

This describes what will be sent across the socket, raw, and how to get from that to a
Python object. It also implements the usage of HMAC for message authentication.

Admittedly, the HMAC authentication is likely unnecessary (using UNIX sockets in
containerised volumes on trusted hardware)... But, it also serves as a checksum
and makes sure anything not coming from one of the containers just gets tossed.

It also means that, in the future, or for development purposes, the scheme could be
modified to use UDP sockets and connect the containers running on separate machines.
(There could be utility, for instance, to having the webapp and api hosted from a
different machine)
"""

import pickle
from typing import TypeVar, Generic, Any, cast
import hashlib
import hmac
import time

T = TypeVar('T')


class _Hmac:
    @staticmethod
    def hash():  # noqa: ANN205
        return hashlib.sha3_256

    @staticmethod
    def digest_len() -> int:
        return 32

    @staticmethod
    def hmac_digest(message: bytes, secret: bytes) -> bytes:
        return hmac.new(secret, message, _Hmac.hash()).digest()


class CoreIPCUnit(Generic[T]):
    """Just a serializable unit of session-layer transmission.

    This will be used for both requests and responses, handle
    timestamps, hmac, and pickling.
    """

    def __init__(self, obj: T, secret: bytes, timestamp_resolution: int = 5) -> None:
        """Instantiates an IPC session unit.

        Args:
            obj (T): Object to be transmitted
            secret (bytes): Secret for the HMAC
            timestamp_resolution (int): The resolution (in seconds) of the associated
                timestamp. The unit must be decoded within this interval of when it is
                encoded for the HMAC to work (and make replay attacks harder).
        """
        super().__init__()

        self.obj = obj
        self.secret = secret
        self.timestamp_resolution: int = timestamp_resolution
        self.timestamp: int | None = None

    def to_bytes(self) -> bytes:
        """Serializes the whole unit with HMAC.

        This also sets the timestamp for the unit, which is relevant to the HMAC.
        Ensure that the unit is transmitted shortly after this is called.

        Returns:
            bytes: a bytes representation of this
        """
        self.timestamp = int(time.time()) % self.timestamp_resolution
        message_bytes = pickle.dumps(self)
        return message_bytes + _Hmac.hmac_digest(message_bytes, self.secret)

    @classmethod
    def from_bytes(cls, ser: bytes, secret: bytes) -> 'CoreIPCUnit[T]':
        """Produces a CoreIPCUnit object from a string of bytes.

        Args:
            ser (bytes): Serialized bytes received
            secret (bytes): HMAC secret used to verify authenticity/no tampering

        Raises:
            TypeError: if an invalid type is unpickled
            ValueError: if the hmac is invalid

        Returns:
            CoreIPCUnit[T]: _description_
        """
        digest_len: int = _Hmac.digest_len()

        obj_bytes: bytes = ser[:digest_len]
        hmac_bytes: bytes = ser[-digest_len:]

        # Check HMAC
        if not hmac.compare_digest(hmac_bytes, _Hmac.hmac_digest(obj_bytes, secret)):
            raise ValueError("Invalid hmac. Message cannot be trusted.")

        obj: Any = pickle.loads(obj_bytes)

        if not isinstance(obj, CoreIPCUnit):
            raise TypeError("Invalid type received.")

        unit: CoreIPCUnit = cast(CoreIPCUnit[T], obj)

        return unit
