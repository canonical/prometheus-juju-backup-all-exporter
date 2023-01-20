#!/usr/bin/python3
"""Test exporter snap."""
import os
from subprocess import run

SNAP_NAME = "prometheus-juju-backup-all-exporter"


def test_default_config_installed(snap_config):
    """Check if the snap default config exists."""
    assert os.path.exists(snap_config)


def test_snap_active(snap_name):
    """Check if the snap is in active state."""
    result = run(
        f"systemctl is-active snap.{snap_name}.{snap_name}.service",
        shell=True,
        capture_output=True,
    )
    assert result.returncode == 0
    assert result.stdout.decode().strip() == "active"
