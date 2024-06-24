import pytest
import os
import tempfile
from pvhotwatercore.common.config.staticconfig import StaticConfig
from pvhotwatercore.common.config import core


@pytest.fixture(scope="module")
def tmp_conf_path():
    """Creates temp dir."""
    # Create temp dir
    dirpath = tempfile.mkdtemp()

    # Populate
    with open(os.path.join(dirpath, "test.json"), 'w') as fp:
        fp.write(
            "{}")

    yield dirpath

    # Clean up
    os.unlink(os.path.join(dirpath, "test.json"))
    os.rmdir(dirpath)


@pytest.fixture(scope="module")
def static_config(tmp_conf_path):
    core._IGNORE_PATH_ACCESSED = True
    core._CONFIG_PATH_ACCESSED = False
    core.ConfigBase.set_config_path(tmp_conf_path)

    yield StaticConfig('test.json')

    core._IGNORE_PATH_ACCESSED = False
    core._CONFIG_PATH_ACCESSED = False


def test_loaded_ok(static_config):
    # Confirms that expected fields are there
    # (sanity check)
    assert static_config.config_str == "{}"


def test_on_load(static_config):
    # Test that on_load does not raise any exceptions
    try:
        static_config.on_load()
    except Exception as e:
        pytest.fail(f"on_load raised an exception {e}")


def test_reload_warns(static_config):
    # Test that calling reload raises a RuntimeError
    with pytest.raises(RuntimeError):
        static_config.reload()
