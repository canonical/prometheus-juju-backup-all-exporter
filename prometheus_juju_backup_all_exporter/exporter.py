"""Module for j-b-a exporter."""

import socket
import threading
from logging import getLogger
from socketserver import ThreadingMixIn
from typing import Any, Tuple
from wsgiref.simple_server import WSGIRequestHandler, WSGIServer, make_server

from prometheus_client import make_wsgi_app
from prometheus_client.core import REGISTRY
from prometheus_client.registry import Collector

logger = getLogger(__name__)


def _get_best_family(address: str, port: int) -> Tuple[int, str]:
    """Automatically select address family depending on address."""
    # Copied from
    # https://github.com/prometheus/client_python/blob/master/prometheus_client/exposition.py#L152
    infos = socket.getaddrinfo(address, port)
    family, _, _, _, sockaddr = next(iter(infos))
    return family, sockaddr[0]


class ThreadingWSGIServer(ThreadingMixIn, WSGIServer):
    """A WSGI server that handle requests in a separate thread."""

    daemon_threads = True


class SlientRequestHandler(WSGIRequestHandler):
    """A Slient Request handler."""

    def log_message(self, format: str, *args: Any) -> None:  # pylint: disable=W0622
        """Log nothing."""


class Exporter:
    """The exporter class."""

    def __init__(self, port: int, addr: str = "0.0.0.0") -> None:
        """Initialize the exporter class.

        Args:
            port: Start the exporter at this port.
            addr: Start the exporter at this address.
        """
        self.addr = addr
        self.port = int(port)
        self.app = make_wsgi_app()

    def register(self, collector: Collector) -> None:
        """Register collector to the exporter."""
        REGISTRY.register(collector)

    def run(self, daemon: bool = False) -> None:
        """Start the exporter server."""
        addr_family, addr = _get_best_family(self.addr, self.port)

        class TmpServer(ThreadingWSGIServer):
            """Copy of the ThreadingWSGIServer."""

            address_family = addr_family

        httpd = make_server(
            addr,
            self.port,
            self.app,
            server_class=TmpServer,
            handler_class=SlientRequestHandler,
        )
        logger.info("Started promethesus juju-backup-all exporter at %s:%s.", self.addr, self.port)
        thread = threading.Thread(target=httpd.serve_forever)
        thread.daemon = daemon
        thread.start()
