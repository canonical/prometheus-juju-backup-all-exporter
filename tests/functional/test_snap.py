#!/usr/bin/python3
"""Test exporter snap."""
import os
import re
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


def test_exporter_http_server():
    """Check if http server is running."""
    result = run("curl http://localhost:10000", shell=True, capture_output=True)
    assert result.returncode == 0


def test_exporter_metrics_created(available_metric_names):
    """Check if juju-backup-all related metric is created."""
    result = run("curl http://localhost:10000", shell=True, capture_output=True)
    assert result.returncode == 0

    output = result.stdout.decode().strip()
    for metric_name in available_metric_names:
        pattern = metric_name
        match = re.search(pattern, output).group()
        assert match is not None


def test_backup_stats_collector(backup_stats_data):
    """Check if backup stats collector is working properly."""
    result = run("curl http://localhost:10000", shell=True, capture_output=True)
    assert result.returncode == 0

    output = result.stdout.decode().strip()
    cases = {
        "duration": r"juju_backup_all_command_duration_seconds{.*} [\d].*",
        "status_ok": r"juju_backup_all_command_ok_info{.*} [\d].*",
    }
    for k, v in cases.items():
        match = re.search(v, output)
        assert match is not None and isinstance(match.group(), str)
        match_group = match.group().split()
        assert len(match_group) == 2
        assert float(match_group[1]) == backup_stats_data[k]


def test_backup_state_collector(backup_state_data):
    """Check if backup state collector is working properly."""
    result = run("curl http://localhost:10000", shell=True, capture_output=True)
    assert result.returncode == 0

    output = result.stdout.decode().strip()
    cases = {
        "failed": r"juju_backup_all_backup_failed_total [\d].*",
        "purged": r"juju_backup_all_backup_purged_total [\d].*",
        "completed": r"juju_backup_all_backup_completed_total [\d].*",
    }
    for k, v in cases.items():
        match = re.search(v, output)
        assert match is not None and isinstance(match.group(), str)
        match_group = match.group().split()
        assert len(match_group) == 2
        assert float(match_group[1]) == backup_state_data[k]
