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
from tcosw.models import BookSnapshot, OrderLevel
from tcosw.runtime import BasketSpreadTracker
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
