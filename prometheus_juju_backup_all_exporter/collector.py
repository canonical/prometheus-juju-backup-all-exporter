"""Module for j-b-a collecter."""

from abc import ABC, abstractmethod
from logging import getLogger

from .utils import BackupState, BackupStats, get_result_code_name

logger = getLogger(__name__)


class CollectorBase(ABC):  # pylint: disable=R0903
    """Abstract base class for creating custom collector.

    All collector classes should add this class as a mixin class, and you
    should implement the user defined _fetch() method. The _fetch() method will
    pass the data to each custom metric for further processing. For example,
    you can have a custom collector that groups multiple metrics together:

    ```
    class CustomGauge(MetricBase, GaugeMetricFamily):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        def _process(self, data, old_sample={}):
            return data

    class CustomCollector(CollectorBase):
        def __init__(self, *metrics):
            super().__init__(*metrics)

        def _fetch(self):
            data = [
                    {"labels": ["mongodb"], "value": 20},
                    {"labels": ["juju-backup-all"], "value": 10}
                ]
            return data

    exporter = Exporter(config.port)
    exporter.register(
        CustomCollector(
            CustomGauge(
                "custom_gauge_a",
                "Example description of A",
                labels=["app"],
            ),
        )
    )
    exporter.run()
    ```
    """

    def __init__(self, *metrics):
        """Initialze the collector.

        Args:
            metrics: one or more custom metrics
        """
        self._metrics = metrics

    @abstractmethod
    def _fetch(self):
        """User defined _fetch method used by `self._update_metrics()`.

        Return:
            fetched data as a list of dictionary.

        Examples:
            returned_fetched_data = [
                {"label": [], "value": 10.0}, {"label": ["foo"], "value": 20.0}
            ]
        """

    def _update_metrics(self):
        """Create new metrics based on existing metrics.

        This is an internally used function to fetch new samples from the user
        defined `_fetch()` method, and create new metrics based on the new
        samples and the existing metric classes. The internal properties of
        `_metrics` will be updated every time this internal function is called.
        """
        data = self._fetch()
        new_metrics = []
        for metric in self._metrics:
            new_metric = metric.__class__(
                metric.name,
                metric.documentation,
                labels=metric._labelnames,  # pylint: disable=W0212
            )
            new_metric.add_samples(data, metric.previous_data)
            new_metrics.append(new_metric)
        self._metrics = new_metrics

    def collect(self):
        """Fetch data and update the internal metrics.

        This is a callback method that is used internally within
        `prometheus_client` every time the exporter server is queried. There is
        not return values for this method but it needs to yield all the metrics.

        Yields:
            metrics: the internal metrics.
        """
        self._update_metrics()
        for metric in self._metrics:
            yield metric


class BackupStateCollector(CollectorBase):  # pylint: disable=R0903
    """Collector for backup state."""

    def __init__(self, config, *metrics):
        """Initialize the class."""
        super().__init__(*metrics)
        self.config = config

    def _fetch(self):
        """User defined _fetch method used by `self._update_metrics()`."""
        backup_state = BackupState(self.config)
        return {
            "failed_metric": [
                {"labels": [], "value": float(backup_state.failed)},
            ],
            "purged_metric": [
                {"labels": [], "value": float(backup_state.purged)},
            ],
            "completed_metric": [
                {"labels": [], "value": float(backup_state.completed)},
            ],
        }


class BackupStatsCollector(CollectorBase):  # pylint: disable=R0903
    """Collector for backup stats."""

    def __init__(self, config, *metrics):
        """Initialize the class."""
        super().__init__(*metrics)
        self.config = config

    def _fetch(self):
        """User defined _fetch method used by `self._update_metrics()`."""
        backup_stats = BackupStats(self.config)
        return {
            "duration_metric": [
                {
                    "labels": [
                        str(int(backup_stats.status_ok)),
                        get_result_code_name(backup_stats.result_code),
                    ],
                    "value": backup_stats.duration,
                },
            ],
            "status_ok_metric": [
                {
                    "labels": [get_result_code_name(backup_stats.result_code)],
                    "value": backup_stats.status_ok,
                },
            ],
        }
