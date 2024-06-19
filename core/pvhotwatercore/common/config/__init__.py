"""Handles configuration for anything and everything here.

Config is stored in toml files.
"""

import os
import pathlib


class Config:
    """Represents a single config file."""

    @staticmethod
    def set_config_path(path: str | pathlib.Path):
        """Sets the global path for configuration files.

        This can only be called before a config object is initialized,
        or else live configuration could break and that would be bad.

        Args:
            path (str | pathlib.Path): A valid path to a directory

        Raises:
            FileNotFoundError: if path does not exist or is not a directory
        """
        if not os.path.isdir(path):
            raise FileNotFoundError("Config path {path} does not exist.")

    def __init__(self, filename: str):
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
