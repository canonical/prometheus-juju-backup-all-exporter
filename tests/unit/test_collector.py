import unittest
from unittest.mock import Mock, patch

import pytest

from prometheus_juju_backup_all_exporter import collector
from prometheus_juju_backup_all_exporter.collector import (
    BackupStateCollector,
    BackupStatsCollector,
    CollectorBase,
)


class TestCollectorBase(unittest.TestCase):
    """Collector base test class."""

    def setUp(self):
        self.patch_abstract_method = patch.object(
            CollectorBase, "__abstractmethods__", set()
        )
        self.patch_abstract_method.start()
        mock_metric = Mock()
        mock_metric.__class__ = Mock()
        mock_metric.add_samples = Mock()
        self.test_subclass = CollectorBase(mock_metric)
        self.addCleanup(self.patch_abstract_method.stop)

    def test_cannot_init_collector_base(self):
        """Test cannot initialize CollectorBase."""
        self.patch_abstract_method.stop()
        with pytest.raises(TypeError):
            CollectorBase()

    def test_collector_base_class_collect(self):
        """Test collector base class's collect method."""
        self.test_subclass._update_metrics = Mock()
        list(self.test_subclass.collect())  # need list() because it's a generator
        self.test_subclass._update_metrics.assert_called()

    def test_collector_base_class_update_metrics(self):
        """Test collector base class's _update_metrics() method."""
        self.test_subclass._fetch = Mock()
        self.test_subclass._update_metrics()
        self.test_subclass._fetch.assert_called()


class TestCustomCollect(unittest.TestCase):
    """Custom test class."""

    @classmethod
    def setUpClass(cls):
        cls.mock_metric = Mock()
        cls.mock_metric.__class__ = Mock()
        cls.mock_metric.add_samples = Mock()

    @patch.object(collector, "BackupStats")
    def test_backup_stats_collector(self, mock_backup_stats):
        """Test backup stats collector fetch correct information."""
        backup_stats_collector = BackupStatsCollector(self.mock_metric)
        fetched_data = backup_stats_collector._fetch()
        mock_backup_stats.assert_called()
        assert "duration_metric" in fetched_data
        assert "status_ok_metric" in fetched_data
        for metric_data in fetched_data.values():
            for sample in metric_data:
                assert "labels" in sample
                assert "value" in sample

    @patch.object(collector, "BackupState")
    def test_backup_state_collector(self, mock_backup_state):
        """Test backup state collector fetch correct information."""
        backup_state_collector = BackupStateCollector(self.mock_metric)
        fetched_data = backup_state_collector._fetch()
        mock_backup_state.assert_called()
        assert "failed_metric" in fetched_data
        assert "purged_metric" in fetched_data
        assert "completed_metric" in fetched_data
        for metric_data in fetched_data.values():
            for sample in metric_data:
                assert "labels" in sample
                assert "value" in sample
