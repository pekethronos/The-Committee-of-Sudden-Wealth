from __future__ import annotations

import json
import os
from copy import deepcopy
from dataclasses import dataclass
from typing import Any


DEFAULT_CONFIG: dict[str, Any] = {
    "logging": {
        "max_entries": 64,
        "max_payload_chars": 3500,
    },
    "products": {
        "RAINFOREST_RESIN": {
            "strategy": "fixed_fair",
            "fair_value": 10000,
            "quote_width": 1,
            "quote_clip": 4,
            "min_take_edge": 1,
            "clear_threshold": 12,
            "clear_clip": 6,
            "skew_per_unit": 0.05,
            "position_limit": 50,
        },
        "KELP": {
            "strategy": "dominant_liquidity",
            "quote_width": 1,
            "quote_clip": 3,
            "min_take_edge": 1,
            "clear_threshold": 10,
            "clear_clip": 5,
            "skew_per_unit": 0.04,
            "position_limit": 50,
            "min_wall_size": 8,
        },
    },
}


@dataclass(slots=True)
class RuntimeConfig:
    raw: dict[str, Any]

    @property
    def logging(self) -> dict[str, Any]:
        return self.raw["logging"]

    @property
    def products(self) -> dict[str, dict[str, Any]]:
        return self.raw["products"]


def load_runtime_config(env_var: str = "TCOSW_TRADER_CONFIG") -> RuntimeConfig:
    config = deepcopy(DEFAULT_CONFIG)
    raw = os.environ.get(env_var)
    if raw:
        merge_dicts(config, json.loads(raw))
    return RuntimeConfig(raw=config)


def merge_dicts(base: dict[str, Any], override: dict[str, Any]) -> None:
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            merge_dicts(base[key], value)
        else:
            base[key] = value
