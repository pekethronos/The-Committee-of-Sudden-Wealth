from tcosw.fair_value import dominant_liquidity_fair, top_of_book_mid
from tcosw.models import BookSnapshot, OrderLevel, ProductState
from tcosw.risk import clamp_buy_size, clamp_sell_size
from tcosw.strategies.fixed_fair import FixedFairStrategy


def test_dominant_liquidity_fair_uses_deepest_levels() -> None:
    book = BookSnapshot(
        bids=(OrderLevel(price=9998, quantity=3), OrderLevel(price=9997, quantity=12)),
        asks=(OrderLevel(price=10002, quantity=2), OrderLevel(price=10003, quantity=11)),
    )
    assert dominant_liquidity_fair(book) == 10000.0


def test_top_of_book_mid_returns_none_without_both_sides() -> None:
    book = BookSnapshot(bids=(OrderLevel(price=9999, quantity=4),), asks=())
    assert top_of_book_mid(book) is None


def test_risk_clamps_to_position_limit() -> None:
    assert clamp_buy_size(10, position=17, limit=20) == 3
    assert clamp_sell_size(10, position=-18, limit=20) == 2


def test_fixed_fair_strategy_takes_obvious_edges() -> None:
    state = ProductState(
        product="AMETHYSTS",
        position=0,
        position_limit=20,
        book=BookSnapshot(
            bids=(OrderLevel(price=10002, quantity=4),),
            asks=(OrderLevel(price=9998, quantity=5),),
        ),
    )
    strategy = FixedFairStrategy(fair_value=10000, quote_width=1, quote_clip=2)

    orders = strategy.generate_orders(state)

    assert (9998, 5) in {(order.price, order.quantity) for order in orders}
    assert (10002, -4) in {(order.price, order.quantity) for order in orders}


def test_fixed_fair_strategy_adds_clearing_order_when_inventory_is_large() -> None:
    state = ProductState(
        product="AMETHYSTS",
        position=15,
        position_limit=20,
        book=BookSnapshot(
            bids=(OrderLevel(price=9999, quantity=3),),
            asks=(OrderLevel(price=10001, quantity=3),),
        ),
    )
    strategy = FixedFairStrategy(
        fair_value=10000,
        quote_width=1,
        quote_clip=2,
        clear_threshold=12,
        clear_clip=4,
    )

    orders = strategy.generate_orders(state)

    assert any(order.price == 10000 and order.quantity == -4 for order in orders)
    assert any(order.quantity < 0 for order in orders)
