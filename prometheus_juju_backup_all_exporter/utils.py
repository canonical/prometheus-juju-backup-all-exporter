import json
from logging import getLogger
from pathlib import Path

logger = getLogger(__name__)


def get_result_code_name(result_code):
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

    def __init__(self, config):
        """Initialize and set instance properties."""
        self._duration = 0
        self._status_ok = 0
        self._result_code = 3  # unknown
        stats_file = Path(config.backup_path, "backup_stats.json")
        try:
            if not stats_file.exists():
                logger.error(
                    "Backup stats file: %s does not exist, using default values.",
                    str(stats_file),
                )
            else:
                with open(stats_file, "r") as f:
                    backup_stats = json.load(f)
                    self._duration = backup_stats["duration"]
                    self._status_ok = backup_stats["status_ok"]
                    self._result_code = backup_stats["result_code"]
        except Exception as e:
            logger.error(
                "Invalid backup stats file: %s. %s. Using default values.",
                str(stats_file),
                str(e),
            )

    @property
    def duration(self):
        return self._duration

    @property
    def status_ok(self):
        return self._status_ok

    @property
    def result_code(self):
        return self._result_code


class BackupState:
    """A class representing backup state file."""

    def __init__(self, config):
        """Initialize and set instance properties."""
        self._failed = 0
        self._purged = 0
        self._completed = 0
        state_file = Path(config.backup_path, "backup_state.json")
        try:
            if not state_file.exists():
                logger.warning(
                    "Backup state file: %s does not exist, using default values.",
                    str(state_file),
                )
            else:
                with open(state_file, "r") as f:
                    state = json.load(f)
                    self._failed = state["failed"]
                    self._purged = state["purged"]
                    self._completed = state["completed"]
        except Exception as e:
            logger.error(
                "Invalid backup state file: %s. %s. Using default values.",
                str(state_file),
                str(e),
            )
        finally:
            if state_file.exists():
                logger.info("Removing state file: %s.", str(state_file))
                state_file.unlink()

    @property
    def completed(self):
        return self._completed

    @property
    def failed(self):
        return self._failed

    @property
    def purged(self):
        return self._purged
