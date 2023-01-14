import socket
import threading
from logging import getLogger
from socketserver import ThreadingMixIn
from wsgiref.simple_server import WSGIRequestHandler, WSGIServer, make_server

from prometheus_client import make_wsgi_app
from prometheus_client.core import REGISTRY

logger = getLogger(__name__)


def _get_best_family(address, port):
    """Automatically select address family depending on address."""
    # Copied from
    # https://github.com/prometheus/client_python/blob/master/prometheus_client/exposition.py#L152
    infos = socket.getaddrinfo(address, port)
    family, _, _, _, sockaddr = next(iter(infos))
    return family, sockaddr[0]


def _get_exporter_server(address, port):
    """Return a threaded HTTP server with best address family."""
    addr_family, addr = _get_best_family(str(address), int(port))

    class ThreadedWSGIServer(ThreadingMixIn, WSGIServer):
        """A WSGI server that handle requests in a separate thread."""

        address_family = addr_family

    return ThreadedWSGIServer, addr


class SlientRequestHandler(WSGIRequestHandler):
    """A Slient Request handler."""

    def log_message(self, format, *args):
        """Log nothing."""
        pass  # pragma: no cover


class Exporter(object):
    """The exporter class."""

    def __init__(self, port, addr="0.0.0.0"):
        """Initialize the exporter class.

        Args:
            port: Start the exporter at this port.
            addr: Start the exporter at this address.
        """
        self.port = int(port)
        self.app = make_wsgi_app()
        self.server_class, self.addr = _get_exporter_server(addr, port)

    def register(self, collector):
        """Register collector to the exporter."""
        REGISTRY.register(collector)

    def run(self, daemon=False):
        """Start the exporter server."""
        httpd = make_server(
            self.addr,
            self.port,
            self.app,
            self.server_class,
            handler_class=SlientRequestHandler,
        )
        logger.info(
            "Started promethesus juju-backup-all exporter at {}:{}.".format(
                self.addr, self.port
            )
        )
        t = threading.Thread(target=httpd.serve_forever)
        t.daemon = daemon
        t.start()
