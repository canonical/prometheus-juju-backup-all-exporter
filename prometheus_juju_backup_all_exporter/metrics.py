from abc import ABC, abstractmethod
from logging import getLogger

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
    def _process(self, data, old_sample):
        """User defined process method used by `self.add_samples()`.

        Args:
            data: the data to be processed
            old_sample: previous metric sample, useful when implementing counter.

        Returns:
            processed data: list of dictionary containing 'labels' (list of str) and 'value' (float).

        Examples:
            returned_processed_data = [{"label": [], "value": 10.0}, {"label": ["foo"], "value": 20.0}]
        """
        pass  # pragma: no cover

    @property
    def previous_data(self):
        """Return previous sample as a labels <-> value pair."""
        return {tuple(sample.labels.values()): sample.value for sample in self.samples}

    def __hash__(self):
        """Return the hash of the custom metric."""
        return hash(self.name)  # pragma: no cover

    def add_samples(self, metric_data, old_sample=None):
        """Update the metric every time the exporter is queried (internal use).

        Args:
            metric_data: the external data to be passed to custom `_process` function.
            old_sample: previous metric sample to be passed to custom `_process` function.
        """
        for data in self._process(metric_data, old_sample or {}):
            self.add_metric(data["labels"], data["value"])


#
# TODO: implement the your custom metrics
#
