from logging import getLogger

from prometheus_client.core import GaugeMetricFamily

from .metrics import MetricBase

logger = getLogger(__name__)


class BackupStatusCollector(MetricBase, GaugeMetricFamily):
    """A custom collector for backup result."""

    def __init__(self, *args, **kwargs):
        """Initialize the custom colletor in GaugeMetricFamily."""
        super().__init__(*args, **kwargs)

    def _fetch(self, *args, **kwargs):
        """Initialize the custom colletor in GaugeMetricFamily."""
        # FIXME: you need to implement this appropriately.
        labels = []
        value = 10
        return {"labels": labels, "value": value}
