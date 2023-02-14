import unittest
from unittest.mock import patch

import pytest

from prometheus_juju_backup_all_exporter.__main__ import Config


class TestConfig(unittest.TestCase):
    """Config test class."""

    def setUp(self):
        self.patch_open_file = patch("builtins.open")
        self.patch_os_path_exists = patch("os.path.exists", return_value=True)
        self.patch_open_file.start()
        self.patch_os_path_exists.start()

    def tearDown(self):
        self.patch_open_file.stop()
        self.patch_os_path_exists.stop()

    @patch("prometheus_juju_backup_all_exporter.config.safe_load")
    def test_valid_config(self, mock_safe_load):
        """Test valid config."""
        mock_safe_load.return_value = {
            "port": 10000,
            "level": "INFO",
            "backup_path": "./",
        }
        config = Config.load_config()
        assert config.port == 10000
        assert config.level == "INFO"
        assert config.backup_path == "./"

    @patch("prometheus_juju_backup_all_exporter.config.safe_load")
    def test_invalid_config(self, mock_safe_load):
        """Test invalid config."""
        mock_safe_load.return_value = {
            "port": -10000,
            "level": "RANDOM",
            "backup_path": "./aaa",
        }
        with pytest.raises(ValueError):
            Config.load_config()

    @patch("prometheus_juju_backup_all_exporter.config.safe_load")
    def test_invalid_backup_path(self, mock_safe_load):
        """Test invalid backup_path."""
        mock_safe_load.return_value = {
            "port": 10000,
            "level": "INFO",
            "backup_path": "./test_config.py",
        }
        with pytest.raises(ValueError, match=r".*Backup path.*"):
            Config.load_config()

    def test_missing_config(self):
        """Test missing config."""
        self.patch_open_file.stop()
        self.patch_os_path_exists.stop()
        with pytest.raises(ValueError):
            Config.load_config("random")
