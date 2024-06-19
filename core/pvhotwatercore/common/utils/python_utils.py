"""Generic utils that don't fit in any other category."""

from typing import Callable


def inherit_docstring(superclass_method: Callable) -> Callable:
    """A decorator that copies the docstring from another method.

    This is intended to be used in cases where a method is being overridden
    and there is no sense in writing out the same docstring.

    With Flake8-docstrings, `# noqa: D102` will still need to be present on the
    method declaration line.

    Args:
        superclass_method (Callable): Method to copy the docstring from.
    """
    def _wrapper(method: Callable) -> Callable:
        method.__doc__ = superclass_method.__doc__
        return method
    return _wrapper
