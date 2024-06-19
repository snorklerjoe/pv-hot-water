"""Base for representing hardware devices and their drivers.

Hardware configuration involves two parts:
    a device configuration (which will specify the driver to use)
    a device driver configuration (which will be passed to the driver)
"""

from abc import ABC
# from ...common.config import Config


class Device:
    """Represents any sort of input and/or output device.

    Subclasses need to be able to statically accept a driver.
    """


class DeviceDriver(ABC):
    """Represents a driver for a Device.

    Different driver types should extend this class.
    There will be one instance for each hardware device using a given driver.

    Driver-subclass code does not need to be thread-safe.
    """

    def __init__(self, locked: bool = True) -> None:
        """Initializes this driver.

        Args:
            locked (bool, optional): Whether or not to rely upon a lock to avoid
                having driver subclass code running concurrently. Defaults to True.
        """
