"""Module for custom j-b-a metrics."""

from abc import ABC, abstractmethod
from logging import getLogger
from typing import Any, Dict, List, Tuple

from prometheus_client.core import CounterMetricFamily, GaugeMetricFamily

logger = getLogger(__name__)


class MetricBase(ABC):
    """Abstract base class for creating custom metrics.

    All metric classes should add this class as a mixin class, then subclass
    from the appropriate metric family that fits your needs. For example, you
    can have a custom metric that looks like this:

    ```
    from prometheus_client.core import CounterMetricFamily, GaugeMetricFamily

    class CustomCounter(MetricBase, CounterMetricFamily):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        def _process(self, data, old_sample={}):
            # Get previous count value from old_sample and add new count value
            # to the counter.
            for d in data:
                d["value"] += old_sample.get(tuple(d["labels"]), 0.0)
            return data
    ```
    """

    @abstractmethod
    def _process(
        self, data: Dict[str, List[Dict[str, Any]]], old_sample: Dict[Tuple, float]
    ) -> List[Dict[str, Any]]:
        """User defined process method used by `self.add_samples()`.

        Args:
            data: the data to be processed
            old_sample: previous metric sample, useful when implementing counter.

        Returns:
            processed data: list of dictionary containing 'labels' (list of
            str) and 'value' (float).

        Examples:
            returned_processed_data = [
                {"label": [], "value": 10.0}, {"label": ["foo"], "value": 20.0}
            ]
        """
        return []  # pragma: no cover

    @property
    def previous_data(self) -> Dict[Tuple, float]:
        """Return previous sample as a labels <-> value pair."""
        return {
            tuple(sample.labels.values()): sample.value
            for sample in self.samples  # type: ignore[attr-defined] # pylint: disable=E1101
        }

    def __hash__(self) -> int:
        """Return the hash of the custom metric."""
        # pylint: disable=E1101
        return hash(self.name)  # type: ignore[attr-defined] # pragma: no cover

    def add_samples(
        self, metric_data: Dict[str, List[Dict[str, Any]]], old_sample: Dict[Tuple, float]
    ) -> None:
        """Update the metric every time the exporter is queried (internal use).

        Args:
            metric_data: the external data to be passed to custom `_process` function.
            old_sample: previous metric sample to be passed to custom `_process` function.
        """
        for data in self._process(metric_data, old_sample or {}):
            # pylint: disable=E1101
            self.add_metric(data["labels"], data["value"])  # type: ignore[attr-defined]


class BackupDurationMetric(MetricBase, GaugeMetricFamily):
    """The backup duration metric."""

    def __init__(self, *args: Any, **kwargs: Any):
        """Initialize the metric class."""
        super().__init__(*args, **kwargs)

    def _process(
        self, data: Dict[str, List[Dict[str, Any]]], old_sample: Dict[Tuple, float]
    ) -> List[Dict[str, Any]]:
        """Return the backup duration as a metric."""
        return data["duration_metric"]


class BackupStatusOKMetric(MetricBase, GaugeMetricFamily):
    """The backup status ok metric."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the metric class."""
        super().__init__(*args, **kwargs)

    def _process(
        self, data: Dict[str, List[Dict[str, Any]]], old_sample: Dict[Tuple, float]
    ) -> List[Dict[str, Any]]:
        """Return whether or not the command was okay as a metric."""
        return data["status_ok_metric"]


class BackupPurgedMetric(MetricBase, CounterMetricFamily):
    """The backup expiration metric."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the metric class."""
        super().__init__(*args, **kwargs)

    def _process(
        self, data: Dict[str, List[Dict[str, Any]]], old_sample: Dict[Tuple, float]
    ) -> List[Dict[str, Any]]:
        """Return 1 if backup result file is expired, otherwise 0."""
        metric_data = data["purged_metric"]
        for _data in metric_data:
            _data["value"] += old_sample.get(tuple(_data["labels"]), 0.0)
        return metric_data


class BackupFailedMetric(MetricBase, CounterMetricFamily):
    """The backup failures metric."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the metric class."""
        super().__init__(*args, **kwargs)

    def _process(
        self, data: Dict[str, List[Dict[str, Any]]], old_sample: Dict[Tuple, float]
    ) -> List[Dict[str, Any]]:
        """Increase the counter if backup failed."""
        metric_data = data["failed_metric"]
        for _data in metric_data:
            _data["value"] += old_sample.get(tuple(_data["labels"]), 0.0)
        return metric_data


class BackupCompletedMetric(MetricBase, CounterMetricFamily):
    """The backup completed metric."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the metric class."""
        super().__init__(*args, **kwargs)

    def _process(
        self, data: Dict[str, List[Dict[str, Any]]], old_sample: Dict[Tuple, float]
    ) -> List[Dict[str, Any]]:
        """Increase the counter if backup succeed."""
        metric_data = data["completed_metric"]
        for _data in metric_data:
            _data["value"] += old_sample.get(tuple(_data["labels"]), 0.0)
        return metric_data
