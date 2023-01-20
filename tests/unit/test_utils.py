import unittest
from unittest.mock import Mock, mock_open, patch

import pytest

from prometheus_juju_backup_all_exporter import config, utils
from prometheus_juju_backup_all_exporter.utils import (
    BackupState,
    BackupStats,
    get_result_code_name,
)


@pytest.mark.parametrize(
    "test_input,expected",
    [
        (0.0, "StatusOK"),
        (1.0, "StatusWarning"),
        (2.0, "StatusCritical"),
        (3.0, "StatusUnknown"),
        (4.0, "InvalidResultCode"),
    ],
)
def test_get_result_code_name(test_input, expected):
    assert get_result_code_name(test_input) == expected


class TestBackupStats(unittest.TestCase):
    """BacupStats test class."""

    @classmethod
    def setUpClass(cls):
        cls.patch_open = patch("builtins.open", new_callable=mock_open)
        cls.patch_open.start()

    @classmethod
    def tearDownClass(cls):
        cls.patch_open.stop()

    @patch.object(config, "Config")
    def test_backup_stats_not_exists(self, mock_config):
        """Test backup stats not exists and set default stats."""
        mock_config.backup_path = "non-existing-backup-path"
        backup_stats = BackupStats(mock_config)
        self.assertEqual(backup_stats.duration, utils.DEFAULT_DURATION)
        self.assertEqual(backup_stats.status_ok, utils.DEFAULT_STATUS_OK)
        self.assertEqual(backup_stats.result_code, utils.DEFAULT_RESULT_CODE)

    @patch.object(utils, "Path")
    @patch.object(utils.json, "load")
    @patch.object(config, "Config")
    def test_backup_stats_error(self, mock_config, mock_json_load, mock_pathlib_path):
        """Test backup stats error and set default stats."""
        mock_path = Mock()
        mock_path.exists.return_value = True
        mock_pathlib_path.return_value = mock_path
        mock_json_load.return_value = {"random_data": 123}
        backup_stats = BackupStats(mock_config)
        self.assertEqual(backup_stats.duration, utils.DEFAULT_DURATION)
        self.assertEqual(backup_stats.status_ok, utils.DEFAULT_STATUS_OK)
        self.assertEqual(backup_stats.result_code, utils.DEFAULT_RESULT_CODE)

    @patch.object(utils, "Path")
    @patch.object(utils.json, "load")
    @patch.object(config, "Config")
    def test_backup_stats_success(self, mock_config, mock_json_load, mock_pathlib_path):
        """Test backup stats success."""
        mock_path = Mock()
        mock_path.exists.return_value = True
        mock_pathlib_path.return_value = mock_path
        duration = 1.0
        status_ok = 1.0
        result_code = 1.0
        mock_json_load.return_value = {
            "duration": duration,
            "status_ok": status_ok,
            "result_code": result_code,
        }
        backup_stats = BackupStats(mock_config)
        self.assertEqual(backup_stats.duration, duration)
        self.assertEqual(backup_stats.status_ok, status_ok)
        self.assertEqual(backup_stats.result_code, result_code)


class TestBackupState(unittest.TestCase):
    """BackupState test class."""

    @classmethod
    def setUpClass(cls):
        cls.patch_open = patch("builtins.open", new_callable=mock_open)
        cls.patch_open.start()

    @classmethod
    def tearDownClass(cls):
        cls.patch_open.stop()

    @patch.object(config, "Config")
    def test_backup_state_not_exists(self, mock_config):
        """Test backup state not exists."""
        mock_config.backup_path = "random"
        backup_state = BackupState(mock_config)
        self.assertEqual(backup_state.failed, utils.DEFAULT_FAILED)
        self.assertEqual(backup_state.purged, utils.DEFAULT_PURGED)
        self.assertEqual(backup_state.completed, utils.DEFAULT_COMPLETED)

    @patch.object(utils, "Path")
    @patch.object(utils.json, "load")
    @patch.object(config, "Config")
    def test_backup_state_error(self, mock_config, mock_json_load, mock_pathlib_path):
        """Test backup state error."""
        mock_path = Mock()
        mock_path.exists.return_value = True
        mock_pathlib_path.return_value = mock_path
        mock_json_load.return_value = {"random_data": 123}
        backup_state = BackupState(mock_config)
        self.assertEqual(backup_state.failed, utils.DEFAULT_FAILED)
        self.assertEqual(backup_state.purged, utils.DEFAULT_PURGED)
        self.assertEqual(backup_state.completed, utils.DEFAULT_COMPLETED)

    @patch.object(utils, "Path")
    @patch.object(utils.json, "load")
    @patch.object(config, "Config")
    def test_backup_state_success(self, mock_config, mock_json_load, mock_pathlib_path):
        """Test backup state success."""
        mock_path = Mock()
        mock_path.exists.return_value = True
        mock_pathlib_path.return_value = mock_path
        completed = 1.0
        failed = 1.0
        purged = 1.0
        mock_json_load.return_value = {
            "completed": completed,
            "failed": failed,
            "purged": purged,
        }
        backup_state = BackupState(mock_config)
        self.assertEqual(backup_state.failed, failed)
        self.assertEqual(backup_state.purged, purged)
        self.assertEqual(backup_state.completed, completed)
