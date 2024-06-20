import pytest
from pvhotwatercore.common.utils.misc.singleton import (
    singleton,
    singleton_argenforce
)

# Example classes to apply the singleton decorators to


@pytest.fixture(scope='function')
def testclasses():
    @singleton
    class RegularSingleton:
        def __init__(self, value=42) -> None:
            self.value = value

    @singleton_argenforce
    class ArgEnforcingSingleton:
        def __init__(self, value=42) -> None:
            self.value = value

    yield RegularSingleton, ArgEnforcingSingleton


def test_regular_singleton_behavior(testclasses):
    instance1 = testclasses[0]()
    instance2 = testclasses[0]()
    assert instance1 is instance2, "Both instances should be the same object"


def test_regular_singleton_with_different_arguments(testclasses):
    instance1 = testclasses[0](1)
    instance2 = testclasses[0](2)
    assert instance1 is instance2, (
        "Both instances should be the same object regardless of args"
    )
    assert instance1.value == 1, "The value should remain from the first instantiation"


def test_arg_enforcing_singleton_with_different_arguments(testclasses):
    _ = testclasses[1](1)
    with pytest.raises(ValueError):
        _ = testclasses[1](2)


def test_arg_enforcing_singleton_with_same_arguments(testclasses):
    instance1 = testclasses[1](3)
    instance2 = testclasses[1](3)
    assert instance1 is instance2, (
        "Both instances should be the same object when instantiated with the same args"
    )
