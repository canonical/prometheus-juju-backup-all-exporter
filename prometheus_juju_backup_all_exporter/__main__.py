"""Package entrypoint."""

import argparse
import logging

from .collector import BackupStateCollector, BackupStatsCollector
from .config import DEFAULT_CONFIG, Config
from .exporter import Exporter
from .metrics import (
    BackupCompletedMetric,
    BackupDurationMetric,
    BackupFailedMetric,
    BackupPurgedMetric,
    BackupStatusOKMetric,
)

root_logger = logging.getLogger()


def parse_command_line() -> argparse.Namespace:
    """Command line parser.

    Parse command line arguments and return the arguments.

    Returns:
        args: Command line arguments.
    """
    parser = argparse.ArgumentParser(
        prog=__package__,
        description=__doc__,
    )
    parser.add_argument("-c", "--config", help="Set configuration file.", default="", type=str)
    args = parser.parse_args()

    return args


def main() -> None:
    """Start the prometheus-juju-backup-all exporter."""
    args = parse_command_line()
    config = Config.load_config(config_file=args.config or DEFAULT_CONFIG)
    root_logger.setLevel(logging.getLevelName(config.level))

    exporter = Exporter(config.port)
    exporter.register(
        BackupStatsCollector(
            config,
            BackupDurationMetric(
                "juju_backup_all_command_duration_seconds",
                "Length of time the charm-juju-backup-all backup command took.",
                labels=["status_ok", "result_code"],
            ),
            BackupStatusOKMetric(
                "juju_backup_all_command_ok_info",
                "Indicates whether or not the charm-juju-backup-all backup command was a success.",
                labels=["result_code"],
            ),
        )
    )
    exporter.register(
        BackupStateCollector(
            config,
            BackupFailedMetric(
                "juju_backup_all_backup_failed_total",
                "The number of failed backups.",
                labels=[],
            ),
            BackupPurgedMetric(
                "juju_backup_all_backup_purged_total",
                "The number of purged backups.",
                labels=[],
            ),
            BackupCompletedMetric(
                "juju_backup_all_backup_completed_total",
                "The number of completed backups.",
                labels=[],
            ),
        )
    )
    exporter.run()


if __name__ == "__main__":  # pragma: no cover
    main()
