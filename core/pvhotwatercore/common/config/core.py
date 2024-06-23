"""Config core.

Ultimately, this just serves as a file-handling wrapper for tomlkit.
A tomlkit-generated mapping is the interface to the data, through all core config code.
This allows for config validation without writing a file and thus bypassing all of this
code that would be extraneous to simple validation.
"""

import os
import pathlib
import logging
from abc import ABC, abstractmethod

from tomlkit import load, TOMLDocument
from tomlkit.container import Container
from tomlkit.items import Item

# Valid config files will end with this
VALID_CONFIG_EXTENSION = '.toml'

# Name of conf-dir-setting env variable
CONF_DIR_ENV_NAME = 'PVHOTWATER_CONF_DIR'

# If the conf dir was set by an env var, make sure it actually exists:
if (
    CONF_DIR_ENV_NAME in os.environ and not os.path.exists(
        str(os.getenv(CONF_DIR_ENV_NAME)))
):
    raise FileNotFoundError(
        f"Config directory {os.getenv(CONF_DIR_ENV_NAME)} does not exist."
    )

# The path of a directory containing all configuration files
_CONFIG_PATH: str = os.getenv(CONF_DIR_ENV_NAME, '.')

# Stores True once the config path has been accessed.
_CONFIG_PATH_ACCESSED: bool = False

# To be used only for unit testing.
_IGNORE_PATH_ACCESSED: bool = False


class ConfigBase(ABC):
    """Represents a single config file.

    This representation is READ ONLY.
    Config files should be changed on disk by other means and then reloaded.

    This means that normal access to the configuration is read-only,
    which lessens the possibility of catastrophic failure.  :)
    """

    @classmethod
    def get_config_path(cls) -> str:
        """Returns the config path.

        This value can never change once this method is called.

        Returns:
            str | None: The path to a folder with all toml configuration files, or None
                if no folder has been set with set_config_path() yet.
        """
        global _CONFIG_PATH
        global _CONFIG_PATH_ACCESSED
        global _IGNORE_PATH_ACCESSED
        if cls.__name__ != 'ConfigBase':
            logging.warning(f"{cls.__name__} -> Going to superclass")
            return ConfigBase.get_config_path()
        if not _CONFIG_PATH_ACCESSED:
            _CONFIG_PATH_ACCESSED = True
        return _CONFIG_PATH

    @classmethod
    def set_config_path(cls, path: str | pathlib.Path) -> None:
        """Sets the global path for configuration files.

        This can only be called before a Config object is created and before
        get_config_path() is called. After that, the config dir cannot be changed.

        Args:
            path (str | pathlib.Path): A valid path to a directory

        Raises:
            FileNotFoundError: if path does not exist or is not a directory
            ValueError: if the config path has already been set
        """
        global _CONFIG_PATH
        global _CONFIG_PATH_ACCESSED
        global _IGNORE_PATH_ACCESSED
        if cls.__name__ != 'ConfigBase':
            raise NotImplementedError(
                "You cannot set the config path from a subclass. "
                "Please use ConfigBase.set_config_path()"
            )
        if not os.path.isdir(path):
            raise FileNotFoundError("Config path `{path}` does not exist.")

        if (not _CONFIG_PATH_ACCESSED) or _IGNORE_PATH_ACCESSED:
            logging.info(f"Setting config path to {str(path)}.")
            _CONFIG_PATH = str(path)
        else:
            raise ValueError("The config path has already been accessed.")

    def __init__(self, filename: str) -> None:
        """Initializes a given set of configuration.

        Args:
            filename (str): Filename of toml config file, without a path

        Raises:
            ValueError: if filename contains a path separator or does not have the
                right extension
        """
        if os.sep in filename:
            raise ValueError("Filename cannot contain a path. "
                             "The config search path should be established statically"
                             "with Config.set_config_path()")

        if not filename.endswith(VALID_CONFIG_EXTENSION):
            raise ValueError(
                f"The filename must end in {VALID_CONFIG_EXTENSION}."
            )

        self._conf_file_path: str = os.path.join(ConfigBase.get_config_path(), filename)

        if not os.path.isfile(self._conf_file_path):
            raise FileNotFoundError(
                f"The config file `{filename}` does not exist in the config directory "
                f"{ConfigBase.get_config_path()}."
            )

        self.toml_obj: TOMLDocument

        self._load()

    @property
    def conf_path(self) -> str:
        """The absolute configuration path."""
        return os.path.abspath(self._conf_file_path)

    def _load(self) -> None:
        """Loads and parses the config file."""
        with open(self._conf_file_path, 'rb') as fp:
            self.toml_obj = load(fp)

        self.on_load()

    def reload(self) -> None:
        """Reloads configuration from disk."""
        self._load()

    # Dictionary access method...
    def __getitem__(self, key: str) -> Item | Container:
        """Returns self[key]."""
        return self.toml_obj.__getitem__(key)

    @abstractmethod
    def on_load(self) -> None:
        """This function is executed after each time this config loads from disk."""
