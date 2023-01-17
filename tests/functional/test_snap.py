#!/usr/bin/python3
"""Test exporter snap."""
from subprocess import check_call, run

SNAP_NAME = "prometheus-juju-backup-all-exporter"


def test_default_config_installed(snap_config):
    """Check if the snap default config is in active state."""
    assert check_call(f"ls {snap_config}".split()) == 0


def test_snap_active(snap_name):
    """Check if the snap is in active state."""
    result = run(
        f"systemctl is-active snap.{snap_name}.{snap_name}.service",
        shell=True,
        capture_output=True,
    )
    assert result.returncode == 0
    assert result.stdout.decode().strip() == "active"
