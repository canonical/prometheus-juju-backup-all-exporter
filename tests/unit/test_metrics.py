from unittest.mock import Mock, patch

import pytest
from prometheus_client.samples import Sample

import prometheus_juju_backup_all_exporter
from prometheus_juju_backup_all_exporter.metrics import MetricBase


class TestMetrics:
    """Metrics test class."""

    def test_cannot_init_metric_base(self):
        """Test cannot initialize MetricBase."""
        with pytest.raises(TypeError):
            MetricBase()

    @patch.object(
        prometheus_juju_backup_all_exporter.metrics.MetricBase,
        "__abstractmethods__",
        set(),
    )
    def test_metric_base_class_add_samples(self):
        """Test metrci base class's add_samples method."""
        subclass = MetricBase()
        subclass._process = Mock(return_value=[{"labels": [Mock()], "value": Mock()}])
        subclass.add_metric = Mock()

        subclass.add_samples(Mock(), Mock())

        subclass._process.assert_called()
        subclass.add_metric.assert_called()

    @patch.object(
        prometheus_juju_backup_all_exporter.metrics.MetricBase,
        "__abstractmethods__",
        set(),
    )
    def test_metric_base_class_previous_data(self):
        """Test metric base class's previous_data property."""
        subclass = MetricBase()

        name = "metric-name"
        labels = {"labelname_a": "label_a", "labelname_b": "label_b"}
        value = 0.0
        sample = Sample(name, labels, value)
        subclass.samples = [sample]

        assert list(subclass.previous_data.keys())[0] == tuple(labels.values())
        assert list(subclass.previous_data.values())[0] == value
