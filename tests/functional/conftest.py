import json
import logging
import os
import time
from pathlib import Path
from subprocess import check_call

import pytest

TMP_DIR = "/tmp"
SETUP_TIMEOUT = 5


def prepare_sample_data(data, dest):
    """Prepare sample data."""
    temp_file = Path(TMP_DIR, "sample_data.json")
    with open(temp_file, "w") as fp:
        json.dump(data, fp)

    dest = Path(dest)
    assert check_call(f"sudo mv {str(temp_file)} {str(dest)}".split()) == 0
    assert dest.exists()


@pytest.fixture()
def available_metric_names():
    return [
        "juju_backup_all_command_duration_seconds",
        "juju_backup_all_command_ok_info",
        "juju_backup_all_backup_failed_total",
        "juju_backup_all_backup_purged_total",
        "juju_backup_all_backup_completed_total",
    ]


@pytest.fixture(scope="session")
def backup_stats_data():
    return {
        "duration": 100,
        "status_ok": 0,
        "result_code": 3,
    }


@pytest.fixture(scope="session")
def backup_state_data():
    return {
        "failed": 10,
        "purged": 3,
        "completed": 1,
    }


@pytest.fixture(scope="session")
def snap_name():
    return "prometheus-juju-backup-all-exporter"


@pytest.fixture(scope="session")
def snap_config(snap_name):
    return f"/var/snap/{snap_name}/current/config.yaml"


@pytest.fixture(scope="session")
def snap_common_dir(snap_name):
    return f"/var/snap/{snap_name}/common/"


@pytest.fixture(scope="session", autouse=True)
def setup_snap(snap_name, snap_common_dir, backup_stats_data, backup_state_data):
    """Install the package to the system and cleanup afterwards.

    Note: an environment variable TEST_SNAP is needed to install the snap.
    """
    test_snap = os.environ.get("TEST_SNAP", None)
    if test_snap:
        logging.info("Installing %s snap package...", test_snap)
        assert os.path.isfile(test_snap)
        assert (
            check_call(f"sudo snap install --dangerous {test_snap}".split())
            == 0  # noqa
        )
        prepare_sample_data(
            backup_stats_data, Path(snap_common_dir, "backup_stats.json")
        )
        prepare_sample_data(
            backup_state_data, Path(snap_common_dir, "backup_state.json")
        )
        assert check_call(f"sudo snap start {snap_name}".split()) == 0
    else:
        logging.error(
            "Could not find %s snap package for testing. Needs to build it first.",
            snap_name,
        )

    down = 1
    stime = time.time()
    while time.time() - stime < SETUP_TIMEOUT and down:
        try:
            down = check_call("curl http://localhost:10000".split())
        except Exception:
            time.sleep(0.5)
    assert not down, "Snap is not up."

    yield test_snap

    if test_snap:
        logging.info("Removing %s snap package...", snap_name)
        check_call(f"sudo snap remove {snap_name}".split())
