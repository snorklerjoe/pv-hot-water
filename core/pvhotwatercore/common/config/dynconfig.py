"""Config that can be reloaded."""

from typing import override, TYPE_CHECKING
import logging

from watchdog.observers.inotify import InotifyObserver
from watchdog.observers.polling import PollingObserver
from watchdog.events import FileSystemEventHandler
if TYPE_CHECKING:
    from watchdog.observers.api import BaseObserver
    from watchdog.events import FileSystemEvent

from .core import ConfigBase


class _DynamicConfigFileSystemEventHandler(FileSystemEventHandler):
    def __init__(self, config_obj: 'DynamicConfig') -> None:
        self._config_obj = config_obj

    @override
    def on_modified(self, event: FileSystemEvent) -> None:
        self._config_obj._on_file_modify()


class DynamicConfig(ConfigBase):
    """Reloads the config when the file changes.

    This starts a thread watching for changes (via inotify on Linux platforms).
    When this config file changes, the config is updated.

    If there is any trouble using inotify, it will poll instead.

    Callbacks to run on reload can also be registered.
    """

    def __init__(self, filename: str) -> None:
        """Initializes the dynamic config object with a given config file name.

        It also initializes (but does not start) an observer to watch for changes.

        Args:
            filename (str): the name of the config file represented by this object.
        """
        super().__init__(filename)

        self._file_event_handler = _DynamicConfigFileSystemEventHandler(self)
        self._file_observer: BaseObserver = self._get_file_observer()

    def _get_file_observer(self) -> BaseObserver:
        """Tries to return an InotifyObserver instance.

        ... Or a PollingObserver if it fails.
        """
        observer: BaseObserver

        # Initialize observer
        try:
            observer = InotifyObserver()
        except OSError:
            observer = PollingObserver()

        # Register the event handler
        observer.schedule(self._file_event_handler, self.conf_path)

        return observer

    def _on_file_modify(self) -> None:
        """Runs when the config file is modified."""
        self.reload()

    @override
    def on_load(self) -> None:
        """Run after the config is loaded.

        This sets up the thread to wait for file change and update when appropriate.
        """
        if self._file_observer.is_alive():
            return
        try:
            self._file_observer.start()
        except RuntimeError as e:
            logging.error(
                "RuntimeError when trying to start the file observer for config"
                f"{self._conf_file_path}"
            )
            logging.error(e)
            logging.error("Joining the file observer to restart it.")
            self._file_observer.join()
            self._file_observer = self._get_file_observer()

            # It shouldn't fail this time...
            self._file_observer.start()
