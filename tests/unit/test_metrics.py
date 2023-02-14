import unittest
from unittest.mock import Mock, patch

import pytest
from prometheus_client.samples import Sample

from prometheus_juju_backup_all_exporter.metrics import (
    BackupCompletedMetric,
    BackupDurationMetric,
    BackupFailedMetric,
    BackupPurgedMetric,
    BackupStatusOKMetric,
    MetricBase,
)


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


class TestCustomMetrics:
    """Custom metrics test class."""

    def test_backup_duration_metric(self):
        """Test backup duration metric class."""
        duration_metric = BackupDurationMetric("metric_name", "documentation")

        metric_data = []
        returned_data = duration_metric._process({"duration_metric": metric_data}, {})
        assert returned_data == metric_data

    def test_backup_status_ok_metric(self):
        """Test backup status ok metric class."""
        status_ok_metric = BackupStatusOKMetric("metric_name", "documentation")

        metric_data = []
        returned_data = status_ok_metric._process({"status_ok_metric": metric_data}, {})
        assert returned_data == metric_data

    def test_backup_purged_metric(self):
        """Test backup purged metric class."""
        purged_metric = BackupPurgedMetric("metric_name", "documentation")

        value = 0.0
        labels = ["some_label"]
        metric_data = [{"labels": labels, "value": value}]
        returned_data = purged_metric._process({"purged_metric": metric_data}, {})
        assert returned_data == metric_data

        value = 0.0
        pre_value = 2.0
        labels = ["some_label"]
        old_sample = {tuple(labels): pre_value}
        metric_data = [{"labels": labels, "value": value}]
        expected_metric_data = [{"labels": labels, "value": value + pre_value}]
        returned_data = purged_metric._process(
            {"purged_metric": metric_data}, old_sample
        )
        assert returned_data == expected_metric_data

    def test_backup_failed_metric(self):
        """Test backup failed metric class."""
        failed_metric = BackupFailedMetric("metric_name", "documentation")

        # test without old_sample
        value = 0.0
        labels = ["some_label"]
        metric_data = [{"labels": labels, "value": value}]
        returned_data = failed_metric._process({"failed_metric": metric_data}, {})
        assert returned_data == metric_data

        # test with old_sample
        value = 0.0
        pre_value = 2.0
        labels = ["some_label"]
        old_sample = {tuple(labels): pre_value}
        metric_data = [{"labels": labels, "value": value}]
        expected_metric_data = [{"labels": labels, "value": value + pre_value}]
        returned_data = failed_metric._process(
            {"failed_metric": metric_data}, old_sample
        )
        assert returned_data == expected_metric_data

    def test_backup_completed_metric(self):
        """Test backup completed metric class."""
        completed_metric = BackupCompletedMetric("metric_name", "documentation")

        # test without old_sample
        value = 0.0
        labels = ["some_label"]
        metric_data = [{"labels": labels, "value": value}]
        returned_data = completed_metric._process({"completed_metric": metric_data}, {})
        assert returned_data == metric_data

        # test with old_sample
        value = 0.0
        pre_value = 2.0
        labels = ["some_label"]
        old_sample = {tuple(labels): pre_value}
        metric_data = [{"labels": labels, "value": value}]
        expected_metric_data = [{"labels": labels, "value": value + pre_value}]
        returned_data = completed_metric._process(
            {"completed_metric": metric_data}, old_sample
        )
        assert returned_data == expected_metric_data
