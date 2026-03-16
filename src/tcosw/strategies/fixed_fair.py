from __future__ import annotations

from dataclasses import dataclass

from tcosw.execution import (
    inventory_clearing_order,
    inventory_skewed_quotes,
    take_crossed_edges,
)
from tcosw.models import Order, ProductState


@dataclass(slots=True)
class FixedFairStrategy:
    fair_value: int
    quote_width: int = 1
    quote_clip: int = 5
    min_take_edge: int = 1
    clear_threshold: int = 12
    clear_clip: int = 6
    skew_per_unit: float = 0.05

    def generate_orders(self, state: ProductState) -> list[Order]:
        orders = take_crossed_edges(
            state=state,
            fair_value=float(self.fair_value),
            min_edge=self.min_take_edge,
        )

        clearing = inventory_clearing_order(
            state=state,
            fair_value=float(self.fair_value),
            clip=self.clear_clip,
            clear_threshold=self.clear_threshold,
        )
        if clearing is not None:
            orders.append(clearing)

        orders.extend(
            inventory_skewed_quotes(
                state=state,
                fair_value=float(self.fair_value),
                width=self.quote_width,
                clip=self.quote_clip,
                skew_per_unit=self.skew_per_unit,
            )
        )
        return orders
