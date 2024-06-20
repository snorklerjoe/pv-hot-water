import os
import tempfile
import pytest
import importlib
import pvhotwatercore.common.config.core as core


class SimpleConfig(core.ConfigBase):
    """A test class, the most basic subclass of ConfigBase."""

    def on_load(self) -> None:
        """Do nothing here..."""
        pass


@pytest.fixture(scope="module")
def tmp_conf_path():
    """Creates temp dir."""
    # Create temp dir
    dirpath = tempfile.mkdtemp()

    # Populate
    with open(os.path.join(dirpath, "test.toml"), 'w') as fp:
        fp.write(
            """
                [Test]
                a=1
                b="bumble"
                [Test.today.napoleon]
                plan="whateverIFeelLikeGosh"
            """)

    yield dirpath

    # Clean up
    os.unlink(os.path.join(dirpath, "test.toml"))
    os.rmdir(dirpath)


def test_default_config_path(monkeypatch):
    # Ensure the environment variable is not set
    monkeypatch.delenv('PVHOTWATER_CONF_DIR', raising=False)
    assert SimpleConfig.get_config_path(
    ) == '.', "The default config.Config path should be '.'"


def test_env_config_path(monkeypatch):
    # Ensure the environment variable is not set
    monkeypatch.setenv('PVHOTWATER_CONF_DIR', '/some/crazy/dir')
    importlib.reload(core)
    assert SimpleConfig.get_config_path() == '/some/crazy/dir'


def test_setting_and_getting_config_path(tmp_conf_path):
    core.ConfigBase._CONFIG_PATH_ACCESSED = False  # Resetting for test
    test_path = str(tmp_conf_path)

    # Does not exist
    with pytest.raises(FileNotFoundError):
        SimpleConfig.set_config_path(
            '/invalid/directory/that/cannot/exist/possibly/aoisdfasdufoaisgipadhfib'
        )

    # Is a directory
    with pytest.raises(FileNotFoundError):
        SimpleConfig.set_config_path(os.path.join(tmp_conf_path, 'test.toml'))

    # Set properly
    SimpleConfig.set_config_path(test_path)
    assert SimpleConfig.get_config_path() == test_path

    # Already accessed
    with pytest.raises(ValueError):
        SimpleConfig.set_config_path('.')
    core.ConfigBase._CONFIG_PATH_ACCESSED = False  # Resetting for test

    _ = SimpleConfig("test.toml")

    # Already accessed
    with pytest.raises(ValueError):
        SimpleConfig.set_config_path('.')


def test_config_path_persistence(tmp_conf_path):
    core.ConfigBase._CONFIG_PATH_ACCESSED = False  # Resetting for test
    test_path = str(tmp_conf_path)
    SimpleConfig.set_config_path(test_path)
    # Attempt to set the path again should either fail or be ignored
    new_test_path = str(tmp_conf_path + "/new_dir")
    with pytest.raises((ValueError, FileNotFoundError)):
        SimpleConfig.set_config_path(new_test_path)
    assert SimpleConfig.get_config_path() == test_path


def test_config_load(tmp_conf_path):
    core.ConfigBase._CONFIG_PATH_ACCESSED = False
    SimpleConfig.set_config_path(tmp_conf_path)

    a = SimpleConfig("test.toml")

    assert a['Test']['a'] == 1
    assert a['Test']['b'] == "bumble"
    assert a['Test']['today']['napoleon']['plan'] == "whateverIFeelLikeGosh"

    a.reload()

    assert a['Test']['a'] == 1
    assert a['Test']['b'] == "bumble"
    assert a['Test']['today']['napoleon']['plan'] == "whateverIFeelLikeGosh"

    # Try changing the file:
    with open(os.path.join(tmp_conf_path, "test.toml"), 'w') as fp:
        fp.write(
            """
                [Test]
                a=2
                b="bumble"
                [Test.today.napoleon]
                plan="whateverIFeelLikeGosh"
            """)

    assert a['Test']['a'] == 1

    a.reload()

    assert a['Test']['a'] == 2
    assert a['Test']['b'] == "bumble"
    assert a['Test']['today']['napoleon']['plan'] == "whateverIFeelLikeGosh"


def test_instantiation_with_fullpath():
    with pytest.raises(ValueError):
        SimpleConfig("a" + os.sep + "b.toml")  # Contains os.sep

    try:
        assert SimpleConfig("b.toml") is not None
    except FileNotFoundError:
        pass


def test_instantiation_with_badext():
    with pytest.raises(ValueError):
        SimpleConfig("test.conf")
    with pytest.raises(ValueError):
        SimpleConfig("test.yaml")
    with pytest.raises(ValueError):
        SimpleConfig("test.json")
    with pytest.raises(ValueError):
        SimpleConfig("test.ini")

    try:
        assert SimpleConfig("test.toml") is not None
    except FileNotFoundError:
        pass


def test_abstract_on_load(tmp_conf_path):
    core.ConfigBase._CONFIG_PATH_ACCESSED = False
    SimpleConfig.set_config_path(tmp_conf_path)

    class Counter:
        counter = 0

    class MyConfig(core.ConfigBase):
        def on_load(self) -> None:
            Counter.counter += 1

    a = MyConfig("test.toml")

    assert Counter.counter == 1

    a.reload()

    assert Counter.counter == 2

    a.reload()

    assert Counter.counter == 3
