from __future__ import annotations

from tcosw.models import Order, ProductState
from tcosw.risk import clamp_buy_size, clamp_sell_size


def take_crossed_edges(
    state: ProductState,
    fair_value: float,
    min_edge: int = 1,
) -> list[Order]:
    orders: list[Order] = []
    position = state.position

    for ask in state.book.asks:
        if ask.price > fair_value - min_edge:
            break
        size = clamp_buy_size(ask.quantity, position, state.position_limit)
        if size <= 0:
            break
        orders.append(Order(product=state.product, price=ask.price, quantity=size))
        position += size

    for bid in state.book.bids:
        if bid.price < fair_value + min_edge:
            break
        size = clamp_sell_size(bid.quantity, position, state.position_limit)
        if size <= 0:
            break
        orders.append(Order(product=state.product, price=bid.price, quantity=-size))
        position -= size

    return orders


def inventory_clearing_order(
    state: ProductState,
    fair_value: float,
    clip: int,
    clear_threshold: int,
) -> Order | None:
    if abs(state.position) < clear_threshold:
        return None
    fair_price = int(round(fair_value))
    if state.position > 0:
        size = clamp_sell_size(min(abs(state.position), clip), state.position, state.position_limit)
        if size <= 0:
            return None
        return Order(product=state.product, price=fair_price, quantity=-size)
    size = clamp_buy_size(min(abs(state.position), clip), state.position, state.position_limit)
    if size <= 0:
        return None
    return Order(product=state.product, price=fair_price, quantity=size)


def inventory_skewed_quotes(
    state: ProductState,
    fair_value: float,
    width: int,
    clip: int,
    skew_per_unit: float = 0.0,
) -> list[Order]:
    bid_price = int(fair_value - width - skew_per_unit * state.position)
    ask_price = int(fair_value + width - skew_per_unit * state.position)

    bid_size = clamp_buy_size(clip, state.position, state.position_limit)
    ask_size = clamp_sell_size(clip, state.position, state.position_limit)

    orders: list[Order] = []
    if bid_size > 0:
        orders.append(Order(product=state.product, price=bid_price, quantity=bid_size))
    if ask_size > 0:
        orders.append(Order(product=state.product, price=ask_price, quantity=-ask_size))
    return orders
