import unittest
from unittest.mock import Mock, patch

from prometheus_juju_backup_all_exporter import collector
from prometheus_juju_backup_all_exporter.collector import (
    BackupEventCollector,
    BackupStatsCollector,
)


class TestCustomCollector(unittest.TestCase):
    """Custom test class."""

    @classmethod
    def setUpClass(cls):
        cls.mock_config = Mock()

    @patch.object(collector, "BackupStats")
    def test_backup_stats_collector(self, mock_backup_stats):
        """Test backup stats collector fetch correct information."""
        backup_stats_collector = BackupStatsCollector(self.mock_config)
        payloads = backup_stats_collector.collect()

        available_metrics = [spec.name for spec in backup_stats_collector.specifications]
        self.assertEqual(len(list(payloads)), len(available_metrics))
        for payload in payloads:
            self.assertIn(payload.name, available_metrics)

    @patch.object(collector, "BackupEvent")
    def test_backup_event_collector(self, mock_backup_event):
        """Test backup event collector fetch correct information."""
        backup_event_collector = BackupEventCollector(self.mock_config)
        payloads = backup_event_collector.collect()

        available_metrics = [spec.name for spec in backup_event_collector.specifications]
        self.assertEqual(len(list(payloads)), len(available_metrics))
        for payload in payloads:
            self.assertIn(payload.name, available_metrics)
