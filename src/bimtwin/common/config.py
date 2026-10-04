"""YAML config loading. Device defaults to CPU; GPU is opt-in."""

from pathlib import Path

import yaml

DEFAULTS = {"device": "cpu", "paths": {"data": "data", "outputs": "outputs"}}


def load_config(path=None) -> dict:
    cfg = {**DEFAULTS, "paths": dict(DEFAULTS["paths"])}
    if path is not None:
        with open(Path(path), encoding="utf-8") as f:
            user = yaml.safe_load(f) or {}
        paths = {**cfg["paths"], **user.pop("paths", {})}
        cfg.update(user)
        cfg["paths"] = paths
    return cfg
