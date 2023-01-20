import unittest
from unittest.mock import Mock, patch

import pytest
from prometheus_client.samples import Sample

from prometheus_juju_backup_all_exporter.metrics import MetricBase


class TestMetricsBase(unittest.TestCase):
    """Metrics base test class."""

    def setUp(self):
        self.patch_abstract_method = patch.object(
            MetricBase, "__abstractmethods__", set()
        )
        self.patch_abstract_method.start()
        self.test_subclass = MetricBase()

    def tearDown(self):
        self.patch_abstract_method.stop()

    def test_cannot_init_metric_base(self):
        """Test cannot initialize MetricBase."""
        self.patch_abstract_method.stop()
        with pytest.raises(TypeError):
            MetricBase()

    def test_metric_base_class_add_samples(self):
        """Test metrci base class's add_samples method."""
        self.test_subclass._process = Mock(
            return_value=[{"labels": [Mock()], "value": Mock()}]
        )
        self.test_subclass.add_metric = Mock()

        self.test_subclass.add_samples(Mock(), Mock())

        self.test_subclass._process.assert_called()
        self.test_subclass.add_metric.assert_called()

    def test_metric_base_class_previous_data(self):
        """Test metric base class's previous_data property."""
        name = "metric-name"
        labels = {"labelname_a": "label_a", "labelname_b": "label_b"}
        value = 0.0
        sample = Sample(name, labels, value)
        self.test_subclass.samples = [sample]

        assert list(self.test_subclass.previous_data.keys())[0] == tuple(
            labels.values()
        )
        assert list(self.test_subclass.previous_data.values())[0] == value
