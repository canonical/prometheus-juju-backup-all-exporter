"""Module for loading j-b-a related metrics."""

import json
from logging import getLogger
from pathlib import Path

from .config import Config

logger = getLogger(__name__)

DEFAULT_DURATION = 0
DEFAULT_STATUS_OK = 0
DEFAULT_RESULT_CODE = 3  # unknown

DEFAULT_PURGED = 0
DEFAULT_FAILED = 0
DEFAULT_COMPLETED = 0


def get_result_code_name(result_code: int) -> str:
    """Map result_code to nagio-like string."""
    result_code = int(result_code)
    status_name = {
        0: "StatusOK",
        1: "StatusWarning",
        2: "StatusCritical",
        3: "StatusUnknown",
    }
    return status_name.get(result_code, "InvalidResultCode")


class BackupStats:
    """A class representing backup statistic file."""

    def __init__(self, config: Config) -> None:
        """Initialize and set instance properties."""
        self._duration = DEFAULT_DURATION
        self._status_ok = DEFAULT_STATUS_OK
        self._result_code = DEFAULT_RESULT_CODE
        stats_file = Path(config.backup_path, "backup_stats.json")
        try:
            if not stats_file.exists():
                logger.error(
                    "Backup stats file: %s does not exist, using default values.",
                    str(stats_file),
                )
            else:
                with open(stats_file, "r", encoding="utf-8") as stats:
                    backup_stats = json.load(stats)
                    self._duration = backup_stats["duration"]
                    self._status_ok = backup_stats["status_ok"]
                    self._result_code = backup_stats["result_code"]
        except (KeyError, PermissionError, json.decoder.JSONDecodeError) as err:
            logger.error(
                "Invalid backup stats file: %s. %s. Using default values.",
                str(stats_file),
                str(err),
            )

    @property
    def duration(self) -> int:
        """Return backup duration."""
        return self._duration

    @property
    def status_ok(self) -> int:
        """Return if backup status is okay or not."""
        return self._status_ok

    @property
    def result_code(self) -> int:
        """Return backup result code."""
        return self._result_code


class BackupState:
    """A class representing backup state file."""

    def __init__(self, config: Config) -> None:
        """Initialize and set instance properties."""
        self._failed = DEFAULT_FAILED
        self._purged = DEFAULT_PURGED
        self._completed = DEFAULT_COMPLETED
        state_file = Path(config.backup_path, "backup_state.json")
        try:
            if not state_file.exists():
                logger.warning(
                    "Backup state file: %s does not exist, using default values.",
                    str(state_file),
                )
            else:
                with open(state_file, "r", encoding="utf-8") as state:
                    backup_state = json.load(state)
                    self._failed = backup_state["failed"]
                    self._purged = backup_state["purged"]
                    self._completed = backup_state["completed"]
        except (KeyError, PermissionError, json.decoder.JSONDecodeError) as err:
            logger.error(
                "Invalid backup state file: %s. %s. Using default values.",
                str(state_file),
                str(err),
            )
        finally:
            if state_file.exists():
                logger.info("Removing state file: %s.", str(state_file))
                state_file.unlink()

    @property
    def completed(self) -> int:
        """Return backup completed counts."""
        return self._completed

    @property
    def failed(self) -> int:
        """Return backup failed counts."""
        return self._failed

    @property
    def purged(self) -> int:
        """Return backup purged counts."""
        return self._purged
