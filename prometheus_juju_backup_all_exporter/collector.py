from abc import ABC, abstractmethod
from logging import getLogger

logger = getLogger(__name__)


class CollectorBase(ABC):
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
        """User defined _fetch method used by `self._update_metrics()`."""
        pass

    def _update_metrics(self):
        """Create new metrics based on existing metrics."""
        data = self._fetch()
        new_metrics = []
        for metric in self._metrics:
            new_metric = metric.__class__(
                metric.name, metric.documentation, labels=metric._labelnames
            )
            new_metric.add_samples(data, metric.previous_data)
            new_metrics.append(new_metric)
        self._metrics = new_metrics

    def collect(self):
        """Scrape data that will be used by prometheus_client when the exporter is queried."""
        self._update_metrics()
        for metric in self._metrics:
            yield metric


#
# TODO: implement the your custom collector
#
