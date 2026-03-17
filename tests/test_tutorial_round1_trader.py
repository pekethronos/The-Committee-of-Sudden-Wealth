from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import SimpleNamespace


TRADER_PATH = Path("/Users/sb/tcosw/rounds/tutorial_round_1/trader.py")
ROUND_DIR = TRADER_PATH.parent


def load_tutorial_trader_module():
    spec = importlib.util.spec_from_file_location("tutorial_round1_trader", TRADER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load tutorial trader module")

    prior_datamodel = sys.modules.get("datamodel")
    sys.path.insert(0, str(ROUND_DIR))
    try:
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
    finally:
        sys.path.pop(0)
        sys.modules.pop(spec.name, None)
        if prior_datamodel is None:
            sys.modules.pop("datamodel", None)
        else:
            sys.modules["datamodel"] = prior_datamodel
    return module


def test_wall_detection_requires_both_sides_to_meet_threshold() -> None:
    module = load_tutorial_trader_module()

    depth = SimpleNamespace(
        buy_orders={4999: 5, 4998: 15},
        sell_orders={5010: -14, 5011: -16},
    )
    features = module.compute_tomatoes_book_features(depth)
    assert features["wall_mid"] == (4998 + 5011) / 2.0

    no_wall_depth = SimpleNamespace(
        buy_orders={4999: 5, 4998: 14},
        sell_orders={5010: -14, 5011: -16},
    )
    no_wall_features = module.compute_tomatoes_book_features(no_wall_depth)
    assert no_wall_features["wall_mid"] is None


def test_hybrid_fair_falls_back_to_ema_reversion_without_wall() -> None:
    module = load_tutorial_trader_module()
    trader = module.Trader()
    features = {
        "best_bid": 5000,
        "best_ask": 5004,
        "raw_mid": 5002.0,
        "spread": 4,
        "largest_bid_price": 5000,
        "largest_bid_size": 8,
        "largest_ask_price": 5004,
        "largest_ask_size": 9,
        "wall_mid": None,
    }

    fair, updated = trader.estimate_tomatoes_fair(features, module._empty_state(), "hybrid")

    assert fair == 5002.0
    assert updated["tomatoes_mode"] == "ema_reversion"
    assert updated["tomatoes_ema"] == 5002.0
    assert updated["tomatoes_last_mid"] == 5002.0


def test_load_state_accepts_legacy_tomato_payload() -> None:
    module = load_tutorial_trader_module()
    state = module._load_state('{"tomatoes_ema":5000.5,"tomatoes_last_mid":4999.0}')

    assert state["tomatoes_ema"] == 5000.5
    assert state["tomatoes_last_mid"] == 4999.0
    assert state["tomatoes_mode"] is None
    assert state["tomatoes_last_wall_mid"] is None
    assert state["tomatoes_wall_seen_count"] == 0


def test_quote_caps_shrink_only_inventory_increasing_side() -> None:
    module = load_tutorial_trader_module()

    buy_cap, sell_cap = module.tomatoes_quote_caps(30)
    assert buy_cap == 6
    assert sell_cap == 16

    buy_cap, sell_cap = module.tomatoes_quote_caps(-30)
    assert buy_cap == 16
    assert sell_cap == 6


def test_large_levels_require_stricter_taker_edge() -> None:
    module = load_tutorial_trader_module()

    assert module.tomatoes_take_width(module.TOMATOES_BUY_TAKE_WIDTH, -5) == module.TOMATOES_BUY_TAKE_WIDTH
    assert module.tomatoes_take_width(module.TOMATOES_BUY_TAKE_WIDTH, -20) == (
        module.TOMATOES_BUY_TAKE_WIDTH + module.TOMATOES_LARGE_LEVEL_EXTRA_EDGE
    )
