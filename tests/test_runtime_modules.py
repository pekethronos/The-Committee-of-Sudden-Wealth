import json
from types import SimpleNamespace
from pathlib import Path

from tcosw.analysis.backtest_logs import diff_trades, parse_backtest_log
from tcosw.config import load_runtime_config
from tcosw.conversion import (
    ConversionQuote,
    break_even_local_ask,
    break_even_local_bid,
    flatten_conversion_size,
    local_buy_edge,
    local_sell_edge,
    suggested_taker_sell_price,
)
from tcosw.logging_utils import BoundedLogger
from tcosw.models import BookSnapshot, Order, OrderLevel
from tcosw.runtime import BasketSpreadTracker, build_runtime
from tcosw.strategies.basket import BasketSignal
from tcosw.strategies.dominant_liquidity import DominantLiquidityStrategy


def test_dominant_liquidity_strategy_quotes_and_takes() -> None:
    strategy = DominantLiquidityStrategy(min_wall_size=5, quote_clip=2, clear_threshold=99)
    state_book = BookSnapshot(
        bids=(OrderLevel(9998, 2), OrderLevel(9997, 9)),
        asks=(OrderLevel(9999, 1), OrderLevel(10003, 8)),
    )
    from tcosw.models import ProductState

    orders = strategy.generate_orders(
        ProductState(
            product="KELP",
            position=0,
            position_limit=20,
            book=state_book,
        )
    )
    assert any(order.price == 9999 and order.quantity > 0 for order in orders)
    assert any(order.quantity < 0 for order in orders)


def test_basket_tracker_updates_running_premium() -> None:
    tracker = BasketSpreadTracker(weights={"A": 2, "B": 1}, premium_window=3, volatility_window=3)
    signal = None
    for basket_mid in (31.0, 32.0, 33.0):
        signal = tracker.update(
            basket_book=BookSnapshot((OrderLevel(int(basket_mid - 1), 1),), (OrderLevel(int(basket_mid + 1), 1),)),
            component_books={
                "A": BookSnapshot((OrderLevel(9, 1),), (OrderLevel(11, 1),)),
                "B": BookSnapshot((OrderLevel(9, 1),), (OrderLevel(11, 1),)),
            },
        )
    assert isinstance(signal, BasketSignal)
    assert signal.premium_mean > 0


def test_conversion_break_even_and_flattening() -> None:
    quote = ConversionQuote(
        external_bid=105.0,
        external_ask=106.0,
        transport_fees=1.0,
        export_tariff=2.0,
        import_tariff=3.0,
    )
    assert break_even_local_bid(quote) == 110.0
    assert break_even_local_ask(quote) == 102.0
    assert local_sell_edge(111.0, quote) == 1.0
    assert local_buy_edge(100.0, quote) == 2.0
    assert suggested_taker_sell_price(quote) == 105
    assert flatten_conversion_size(position=7, conversion_limit=3) == -3


def test_bounded_logger_truncates_payload() -> None:
    logger = BoundedLogger(max_entries=10, max_payload_chars=60)
    for idx in range(5):
        logger.log("evt", index=idx, payload="abcdefghij")
    serialized = logger.serialize()
    assert "truncated" in serialized or serialized == "[]"


def test_parse_backtest_log_and_diff() -> None:
    summary = parse_backtest_log(Path("artifacts/tutorial/replays/round0.log"))
    assert "KELP" in summary.product_pnl
    diff = diff_trades(summary.trades, summary.trades)
    assert diff["added"] == []
    assert diff["removed"] == []


def test_runtime_config_defaults_are_loadable() -> None:
    config = load_runtime_config()
    assert "RAINFOREST_RESIN" in config.products
    assert "KELP" in config.products


def test_runtime_basket_strategy_uses_trader_data_history() -> None:
    runtime = build_runtime(
        config_override={
            "products": {},
            "baskets": {
                "PICNIC_BASKET1": {
                    "weights": {"CROISSANTS": 2, "JAMS": 1},
                    "position_limit": 10,
                    "component_limits": {"CROISSANTS": 40, "JAMS": 30},
                    "premium_window": 5,
                    "volatility_window": 5,
                    "entry_zscore": 1.5,
                    "exit_zscore": 0.5,
                    "max_units": 3,
                    "hedge_components": True,
                }
            },
        }
    )

    class FakeDepth:
        def __init__(self, buys: dict[int, int], sells: dict[int, int]) -> None:
            self.buy_orders = buys
            self.sell_orders = sells

    state = SimpleNamespace(
        order_depths={
            "PICNIC_BASKET1": FakeDepth({49: 8}, {51: -8}),
            "CROISSANTS": FakeDepth({9: 50}, {11: -50}),
            "JAMS": FakeDepth({9: 50}, {11: -50}),
        },
        position={},
        traderData=json.dumps({"baskets": {"PICNIC_BASKET1": [0.0, 0.0, 0.0, 0.0]}}),
    )

    orders, conversions, trader_data, runtime_log = runtime.run(state, Order)

    assert conversions == 0
    assert [order.quantity for order in orders["PICNIC_BASKET1"]] == [-3]
    assert [order.quantity for order in orders["CROISSANTS"]] == [6]
    assert [order.quantity for order in orders["JAMS"]] == [3]
    assert "basket_signal" in runtime_log

    persisted = json.loads(trader_data)
    assert len(persisted["baskets"]["PICNIC_BASKET1"]) == 5


def test_build_runtime_allows_env_to_override_config_override(monkeypatch) -> None:
    monkeypatch.setenv(
        "TCOSW_TRADER_CONFIG",
        json.dumps({"products": {"EMERALDS": {"quote_clip": 9}}}),
    )
    runtime = build_runtime(
        config_override={
            "products": {
                "EMERALDS": {
                    "strategy": "fixed_fair",
                    "fair_value": 10000,
                    "quote_width": 1,
                    "quote_clip": 4,
                    "min_take_edge": 1,
                    "clear_threshold": 12,
                    "clear_clip": 6,
                    "skew_per_unit": 0.05,
                    "position_limit": 80,
                }
            }
        }
    )
    assert runtime.config.products["EMERALDS"]["quote_clip"] == 9
