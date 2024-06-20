"""Implements a simple-to-use decorator to implement the singleton pattern.

This module provides three types of singleton decorators:
`@singleton`, which ignores the arguments to the constructor on subsequent calls
`@singleton_argenforce`, which raises a ValueError if the arguments on subsequent
    calls vary from the initial ones.
"""

import functools
from typing import Type, Tuple, Dict, Generic, TypeVar

__all__ = ['singleton', 'singleton_argenforce']

T = TypeVar('T')


class _SingletonWrapper(Generic[T]):
    def __init__(self, cls: Type[T]) -> None:
        self.__wrapped__: Type[T]
        functools.update_wrapper(self, cls)

        self._instance: T | None = None
        self._args: Tuple = ()
        self._kwargs: Dict = {}

    def __call__(self, *args: Tuple, **kwargs: Dict) -> T:
        if self._instance is None:  # Create the instance
            self._args = args
            self._kwargs = kwargs
            self._instance = self.__wrapped__(*args, **kwargs)
        return self._instance


class _ArgEnforceSingletonWrapper(_SingletonWrapper[T]):
    def __init__(self, cls: Type[T]) -> None:
        super().__init__(cls)
        self._instances: Dict[Tuple, T] = {}

    def __call__(self, *args: Tuple, **kwargs: Dict) -> T:
        if (
            self._instance is not None and (
                args != self._args or kwargs != self._kwargs)
        ):
            raise ValueError("Singleton called with different arguments.")
        return super().__call__(*args, **kwargs)


def singleton(cls: Type[T]) -> _SingletonWrapper[T]:
    """Use this decorator to wrap a class to make it a singleton.

    The first time the wrapped class is instantiated, it will create an object
    with those arguments and store it. Every subsequent instantiation will return
    the stored object, regardless of the provided parameters.

    Args:
        cls (Type[T]): The class to make a singleton

    Returns:
        _SingletonWrapper[T]: The singleton-wrapped class
    """
    return _SingletonWrapper(cls)


def singleton_argenforce(cls: Type[T]) -> _ArgEnforceSingletonWrapper[T]:
    """Use this decorator to wrap a class to make it an arg-enforce singleton.

    The first time the wrapped class is instantiated, it will create an object
    with those arguments and store it. Every subsequent instantiation will return
    the stored object, unless the arguments are different than the first call,
    in which case a ValueError will be thrown.

    Args:
        cls (Type[T]): The class to make a singleton

    Returns:
        _ArgEnforceSingletonWrapper[T]: The singleton-wrapped class
    """
    return _ArgEnforceSingletonWrapper(cls)
