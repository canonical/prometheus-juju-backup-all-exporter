from unittest.mock import Mock, patch

import pytest

import prometheus_juju_backup_all_exporter
from prometheus_juju_backup_all_exporter.collector import CollectorBase


class TestCollector:
    """Collector test class."""

    def test_cannot_init_collector_base(self):
        """Test cannot initialize CollectorBase."""
        with pytest.raises(TypeError):
            CollectorBase()

    @patch.object(
        prometheus_juju_backup_all_exporter.collector.CollectorBase,
        "__abstractmethods__",
        set(),
    )
    def test_collector_base_class_collect(self):
        """Test collector base class's collect method."""
        mock_metric = Mock()
        mock_metric.add_samples = Mock()
        subclass = CollectorBase(mock_metric)
        subclass._update_metrics = Mock()

        list(subclass.collect())  # need list() because it's a generator

        subclass._update_metrics.assert_called()

    @patch.object(
        prometheus_juju_backup_all_exporter.collector.CollectorBase,
        "__abstractmethods__",
        set(),
    )
    def test_collector_base_class_update_metrics(self):
        """Test collector base class's _update_metrics() method."""
        mock_metric = Mock()
        mock_metric.__class__ = Mock()
        mock_metric.add_samples = Mock()

        subclass = CollectorBase(mock_metric)
        subclass._fetch = Mock()
        subclass._update_metrics()

        subclass._fetch.assert_called()
