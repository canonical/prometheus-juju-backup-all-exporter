"""Module for j-b-a collecter."""

from logging import getLogger
from typing import Dict, List

from prometheus_client.metrics_core import CounterMetricFamily, GaugeMetricFamily

from .core import Payload, Specification, SyncCollector
from .utils import BackupState, BackupStats, get_result_code_name

logger = getLogger(__name__)


class BackupStateCollector(SyncCollector):
    """Collector for backup state."""

    @property
    def specifications(self) -> List[Specification]:
        """Backup state metrics specs."""
        return [
            Specification(
                name="juju_backup_all_backup_failed_total",
                documentation="The number of failed backups.",
                labels=[],
                metric_class=CounterMetricFamily,
            ),
            Specification(
                name="juju_backup_all_backup_purged_total",
                documentation="The number of purged backups.",
                labels=[],
                metric_class=CounterMetricFamily,
            ),
            Specification(
                name="juju_backup_all_backup_completed_total",
                documentation="The number of completed backups.",
                labels=[],
                metric_class=CounterMetricFamily,
            ),
        ]

    def fetch(self) -> List[Payload]:
        """Load the backup state data."""
        backup_state = BackupState(self.config)
        return [
            Payload(
                name="juju_backup_all_backup_failed_total",
                labels=[],
                value=float(backup_state.failed),
            ),
            Payload(
                name="juju_backup_all_backup_purged_total",
                labels=[],
                value=float(backup_state.purged),
            ),
            Payload(
                name="juju_backup_all_backup_completed_total",
                labels=[],
                value=float(backup_state.completed),
            ),
        ]

    def process(self, payloads: List[Payload], datastore: Dict[str, Payload]) -> List[Payload]:
        """Process the backup state data."""
        # Increments the counter according to the payload.
        for payload in payloads:
            payload.value += datastore[payload.uuid].value
        return payloads


class BackupStatsCollector(SyncCollector):
    """Collector for backup stats."""

    @property
    def specifications(self) -> List[Specification]:
        """Backup stats metrics specs."""
        return [
            Specification(
                name="juju_backup_all_command_duration_seconds",
                documentation="Length of time the charm-juju-backup-all backup command took.",
                labels=["status_ok", "result_code"],
                metric_class=GaugeMetricFamily,
            ),
            Specification(
                name="juju_backup_all_command_ok_info",
                documentation=(
                    "Indicates whether or not the charm-juju-backup-all"
                    " backup command was a success."
                ),
                labels=["result_code"],
                metric_class=GaugeMetricFamily,
            ),
        ]

    def fetch(self) -> List[Payload]:
        """Load the backup stats data."""
        backup_stats = BackupStats(self.config)
        return [
            Payload(
                name="juju_backup_all_command_duration_seconds",
                labels=[
                    str(int(backup_stats.status_ok)),
                    get_result_code_name(backup_stats.result_code),
                ],
                value=backup_stats.duration,
            ),
            Payload(
                name="juju_backup_all_command_ok_info",
                labels=[get_result_code_name(backup_stats.result_code)],
                value=backup_stats.status_ok,
            ),
        ]

    def process(self, payloads: List[Payload], datastore: Dict[str, Payload]) -> List[Payload]:
        """Process the backup stats data."""
        # We only need to "set" the metric to whatever the payload says.
        return payloads
