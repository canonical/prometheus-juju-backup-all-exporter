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
        """Initialize class."""
        self.set_properties(Path(config.backup_path, "backup_stats.json"))

    @property
    def duration(self):
        return self._duration

    @property
    def status_ok(self):
        return self._status_ok

    @property
    def result_code(self):
        return self._result_code

    def set_properties(self, stats_file):
        """Set the instance properties."""
        try:
            if not stats_file.exists():
                logger.error(
                    "Backup stats file: %s does not exist, setting to default values.",
                    str(stats_file),
                )
                self._set_default_stats()
            else:
                with open(stats_file, "r") as f:
                    backup_stats = json.load(f)
                    self._set_properties(backup_stats)
        except Exception as e:
            logger.error(
                "Invalid backup stats file: %s. %s. Setting to default values",
                str(stats_file),
                str(e),
            )
            self._set_default_stats()

    def _set_default_stats(self):
        self._set_properties(
            {
                "duration": 0,
                "status_ok": 0,
                "result_code": 3,  # unknown
            }
        )

    def _set_properties(self, result):
        self._duration = result["duration"]
        self._status_ok = result["status_ok"]
        self._result_code = result["result_code"]


class BackupState:
    """A class representing backup state file."""

    def __init__(self, config):
        """Initialize class."""
        self.set_properties(Path(config.backup_path, "backup_state.json"))

    def set_properties(self, state_file):
        """Set the instance properties and remove the file."""
        try:
            if not state_file.exists():
                logger.warning(
                    "Backup state file: %s does not exist, setting to default values.",
                    str(state_file),
                )
                self._set_default_state()
            else:
                with open(state_file, "r") as f:
                    state = json.load(f)
                    self._set_properties(state)
        except Exception as e:
            self._set_default_state()
            logger.error(
                "Invalid backup command result file: %s. %s",
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

    def _set_properties(self, result):
        self._failed = result["failed"]
        self._purged = result["purged"]
        self._completed = result["completed"]

    def _set_default_state(self):
        self._set_properties(
            {
                "failed": 0.0,
                "purged": 0.0,
                "completed": 0.0,
            }
        )
