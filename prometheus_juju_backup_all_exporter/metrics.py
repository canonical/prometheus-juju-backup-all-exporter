from abc import ABC, abstractmethod
from logging import getLogger

logger = getLogger(__name__)


class MetricBase(ABC):
    """Abstract base class for creating custom collectors.

    All collector classes should add this class as a mixin class, then subclass
    from the appropriate metric family that fits your needs. For example, you
    can have a custom collector that looks like this:

    ```
    class CustomCollector(MetricBase, GaugeMetricFamily):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        def _fetch(self, *args, **kwargs):
            labels = ["test_label", "test_label_2"]
            value = 10.0
            return {"labels": labels, "value": value}
    ```
    """

    @abstractmethod
    def _fetch(self):
        """User defined fetch method used by `self.collect()`."""
        pass

    def __new__(cls, *args, **kwargs):
        """Add logging message when creating new metrics."""
        obj = super().__new__(cls)
        logger.debug("Created new metric '{}'.".format(args[0]))
        return obj

    def __hash__(self):
        """Return the hash of the custom collector."""
        return hash(self.name)

    def collect(self):
        """Update the metric every time the exporter is queried."""
        self.add_metric(**self._fetch())
        logger.debug("Added sample to {}: {}".format(self.name, self.samples[-1:]))
        yield self
