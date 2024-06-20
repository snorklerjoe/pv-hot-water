from pvhotwatercore.common.utils.misc import inherit_docstring


def test_inherit_docstring():
    """Tests the inherit_docstring() decorator."""

    def superclass_method():
        """This is a superclass method."""
        return 1

    @inherit_docstring.inherit_docstring(superclass_method)
    def subclass_method():
        return 2

    assert subclass_method.__doc__ == "This is a superclass method."

    # Test that the method still runs:
    assert 1 == superclass_method()
    assert 2 == subclass_method()
