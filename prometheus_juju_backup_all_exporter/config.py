import os
from logging import getLogger

from pydantic import BaseModel, validator
from yaml import safe_load

logger = getLogger(__name__)

DEFAULT_CONFIG = os.path.join(os.environ.get("SNAP_DATA", "./"), "config.yaml")


class Config(BaseModel):
    port: int = 10000
    level: str = "DEBUG"

    @validator("port")
    def validate_port_range(cls, port):  # noqa: N805
        if not 1 <= port <= 65535:
            msg = "Port must be in [1, 65535]."
            logger.error(msg)
            raise ValueError(msg)
        return port

    @validator("level")
    def validate_level_choice(cls, level):  # noqa: N805
        level = level.upper()
        choices = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if level not in choices:
            msg = "Level must be in {} (case-insensitive).".format(choices)
            logger.error(msg)
            raise ValueError(msg)
        return level

    @classmethod
    def load_config(cls, config_file=DEFAULT_CONFIG):
        if not os.path.exists(config_file):
            msg = "Configuration file: {} not exists.".format(config_file)
            logger.error(msg)
            raise ValueError(msg)
        with open(config_file, "r") as f:
            logger.info("Loaded exporter configuration: {}.".format(config_file))
            data = safe_load(f) or {}
            return cls(**data)
