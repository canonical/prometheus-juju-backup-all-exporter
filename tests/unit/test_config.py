from unittest.mock import mock_open, patch

import pytest

from prometheus_juju_backup_all_exporter.__main__ import Config


class TestConfig:
    """Config test class."""

    @patch("os.path.exists")
    @patch("prometheus_juju_backup_all_exporter.config.safe_load")
    def test_valid_config(self, mock_safe_load, mock_path_exists):
        """Test valid config."""
        mock_path_exists.return_value = True
        with patch("builtins.open", new_callable=mock_open):
            mock_safe_load.return_value = {
                "port": 10000,
                "level": "INFO",
            }
            config = Config.load_config()
            assert config.port == 10000
            assert config.level == "INFO"

    @patch("os.path.exists")
    @patch("prometheus_juju_backup_all_exporter.config.safe_load")
    def test_invalid_config(self, mock_safe_load, mock_path_exists):
        """Test invalid config."""
        mock_path_exists.return_value = True
        with patch("builtins.open", new_callable=mock_open):
            mock_safe_load.return_value = {
                "port": -10000,
                "level": "RANDOM",
            }
            with pytest.raises(ValueError):
                Config.load_config()

    def test_missing_config(self):
        """Test missing config."""
        with pytest.raises(ValueError):
            Config.load_config("random")
