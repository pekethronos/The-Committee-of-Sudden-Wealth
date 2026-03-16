from __future__ import annotations

from tcosw.models import BookSnapshot, Order, OrderLevel, ProductState


def product_state_from_order_depth(
    product: str,
    order_depth: object,
    position: int,
    position_limit: int,
) -> ProductState:
    bids = tuple(
        OrderLevel(price=price, quantity=quantity)
        for price, quantity in sorted(order_depth.buy_orders.items(), reverse=True)
        if quantity > 0
    )
    asks = tuple(
        OrderLevel(price=price, quantity=-quantity)
        for price, quantity in sorted(order_depth.sell_orders.items())
        if quantity < 0
    )
    return ProductState(
        product=product,
        position=position,
        position_limit=position_limit,
        book=BookSnapshot(bids=bids, asks=asks),
    )


def orders_to_datamodel(orders: list[Order], order_cls: type) -> list[object]:
    return [order_cls(order.product, order.price, order.quantity) for order in orders]
