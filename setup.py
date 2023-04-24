"""Entrypoint for python package."""

from setuptools import setup

configs = {
    "name": "prometheus-juju-backup-all-exporter",
    "description": "collects backup results and exports them as metrics",
    "use_scm_version": True,
    "setup_requires": ["setuptools_scm", "pyyaml"],
    "author": "Canonical BootStack DevOps Centres",
    "packages": ["prometheus_juju_backup_all_exporter"],
    "url": "https://github.com/canonical/prometheus-juju-backup-all-exporter",
    "entry_points": {
        "console_scripts": [
            "prometheus-juju-backup-all-exporter="
            + "prometheus_juju_backup_all_exporter.__main__:main",
        ]
    },
}

with open("LICENSE", encoding="utf-8") as f:
    configs.update({"license": f.read()})

with open("README.md", encoding="utf-8") as f:
    configs.update({"long_description": f.read()})


if __name__ == "__main__":
    setup(**configs)
