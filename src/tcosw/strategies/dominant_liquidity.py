from __future__ import annotations

from dataclasses import dataclass

from tcosw.execution import inventory_clearing_order, inventory_skewed_quotes, take_crossed_edges
from tcosw.fair_value import dominant_liquidity_fair
from tcosw.models import Order, ProductState


@dataclass(slots=True)
class DominantLiquidityStrategy:
    quote_width: int = 1
    quote_clip: int = 4
    min_take_edge: int = 1
    clear_threshold: int = 10
    clear_clip: int = 5
    skew_per_unit: float = 0.04
    min_wall_size: int = 8

    def generate_orders(self, state: ProductState) -> list[Order]:
        fair = dominant_liquidity_fair(state.book, min_depth=self.min_wall_size)
        if fair is None:
            return []

        orders = take_crossed_edges(
            state=state,
            fair_value=fair,
            min_edge=self.min_take_edge,
        )

        clearing = inventory_clearing_order(
            state=state,
            fair_value=fair,
            clip=self.clear_clip,
            clear_threshold=self.clear_threshold,
        )
        if clearing is not None:
            orders.append(clearing)

        orders.extend(
            inventory_skewed_quotes(
                state=state,
                fair_value=fair,
                width=self.quote_width,
                clip=self.quote_clip,
                skew_per_unit=self.skew_per_unit,
            )
        )
        return orders
