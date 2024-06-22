"""For configuration that cannot be reloaded without restarting the system."""

from functools import lru_cache
from typing import override

from .core import ConfigBase


@lru_cache
class StaticConfig(ConfigBase):
    """File-based config that cannot be reloaded during runtime."""

    @override
    def on_load(self) -> None:
        """Runs after the config is loaded.

        Nothing needs to be done if the config is static, but you can override
        this method.
        """
        pass

    @override
    def reload(self) -> None:  # noqa: D102
        raise RuntimeError("Static configuration cannot be reloaded.")
