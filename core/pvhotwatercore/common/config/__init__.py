"""Handles configuration for anything and everything here.

Config is stored in a directory of toml files.
By default, the config directory is given by the environment variable
`PVHOTWATER_CONF_DIR`, or '.' if none is provided.

"""

import os
import pathlib
import logging

from tomlkit import load, TOMLDocument
from tomlkit.container import Container
from tomlkit.items import Item


class Config:
    """Represents a single config file.

    This representation is READ ONLY.
    Config files should be changed on disk by other means and then reloaded.

    This means that normal access to the configuration is read-only,
    which lessens the possibility of catastrophic failure.  :)
    """

    # The path of a directory containing all configuration files
    _CONFIG_PATH: str = os.getenv('PVHOTWATER_CONF_DIR', '.')

    # Stores True once the config path has been accessed.
    _CONFIG_PATH_ACCESSED: bool = False

    @staticmethod
    def get_config_path() -> str:
        """Returns the config path.

        This value can never change once this method is called.

        Returns:
            str | None: The path to a folder with all toml configuration files, or None
                if no folder has been set with set_config_path() yet.
        """
        if not Config._CONFIG_PATH_ACCESSED:
            Config._CONFIG_PATH_ACCESSED = True
        return Config._CONFIG_PATH

    @staticmethod
    def set_config_path(path: str | pathlib.Path) -> None:
        """Sets the global path for configuration files.

        This can only be called before a Config object is created and before
        get_config_path() is called. After that, the config dir cannot be changed.

        Args:
            path (str | pathlib.Path): A valid path to a directory

        Raises:
            FileNotFoundError: if path does not exist or is not a directory
            ValueError: if the config path has already been set
        """
        if not os.path.isdir(path):
            raise FileNotFoundError("Config path `{path}` does not exist.")
        if not Config._CONFIG_PATH_ACCESSED:
            logging.info(f"Setting config path to {str(path)}.")
            Config._CONFIG_PATH = str(path)
        else:
            raise ValueError("The config path has already been accessed.")

    def __init__(self, filename: str) -> None:
        """Initializes a given set of configuration.

        Args:
            filename (str): Filename of toml config file, without a path

        Raises:
            ValueError: if filename contains a path separator
        """
        if os.sep in filename:
            raise ValueError("Filename cannot contain a path. "
                             "The config search path should be established statically"
                             "with Config.set_config_path()")

        Config._CONFIG_PATH_ACCESSED = True

        self._conf_file_path: str = os.path.join(Config._CONFIG_PATH, filename)

        if not os.path.isfile(self._conf_file_path):
            raise FileNotFoundError(
                f"The config file `{filename}` does not exist in the config directory."
            )

        self.toml_obj: TOMLDocument

        self._load()

    def _load(self) -> None:
        """Loads and parses the config file."""
        with open(self._conf_file_path, 'rb') as fp:
            self.toml_obj = load(fp)

    def reload(self) -> None:
        """Reloads configuration from disk."""
        self._load()

    # Dictionary access method...
    def __getitem__(self, key: str) -> Item | Container:
        """Returns self[key]."""
        return self.toml_obj.__getitem__(key)
