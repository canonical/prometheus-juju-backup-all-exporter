import unittest
from unittest.mock import Mock, patch

import pytest

from prometheus_juju_backup_all_exporter.collector import CollectorBase


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
