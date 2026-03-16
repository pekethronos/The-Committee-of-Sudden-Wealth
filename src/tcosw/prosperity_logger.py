from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class ProsperityLogger:
    max_payload_chars: int = 3750

    def flush(
        self,
        state: Any,
        orders: dict[str, list[Any]],
        conversions: int,
        trader_data: str,
        logs: str,
    ) -> None:
        base_payload = [
            self._compress_state(state, ""),
            self._compress_orders(orders),
            conversions,
            "",
            "",
        ]
        base_length = len(self._to_json(base_payload))
        max_item_length = max(0, (self.max_payload_chars - base_length) // 3)

        payload = [
            self._compress_state(state, self._truncate(getattr(state, "traderData", ""), max_item_length)),
            self._compress_orders(orders),
            conversions,
            self._truncate(trader_data, max_item_length),
            self._truncate(logs, max_item_length),
        ]
        print(self._to_json(payload))

    def _compress_state(self, state: Any, trader_data: str) -> list[Any]:
        return [
            state.timestamp,
            trader_data,
            self._compress_listings(state.listings),
            self._compress_order_depths(state.order_depths),
            self._compress_trades(state.own_trades),
            self._compress_trades(state.market_trades),
            state.position,
            self._compress_observations(state.observations),
        ]

    def _compress_listings(self, listings: dict[str, Any]) -> list[list[Any]]:
        return [
            [listing.symbol, listing.product, listing.denomination]
            for listing in listings.values()
        ]

    def _compress_order_depths(self, order_depths: dict[str, Any]) -> dict[str, list[Any]]:
        return {
            symbol: [order_depth.buy_orders, order_depth.sell_orders]
            for symbol, order_depth in order_depths.items()
        }

    def _compress_trades(self, trades: dict[str, list[Any]]) -> list[list[Any]]:
        compressed: list[list[Any]] = []
        for bucket in trades.values():
            compressed.extend(
                [trade.symbol, trade.price, trade.quantity, trade.buyer, trade.seller, trade.timestamp]
                for trade in bucket
            )
        return compressed

    def _compress_observations(self, observations: Any) -> list[Any]:
        conversion_observations = {
            product: [
                observation.bidPrice,
                observation.askPrice,
                observation.transportFees,
                observation.exportTariff,
                observation.importTariff,
                observation.sugarPrice,
                observation.sunlightIndex,
            ]
            for product, observation in observations.conversionObservations.items()
        }
        return [observations.plainValueObservations, conversion_observations]

    def _compress_orders(self, orders: dict[str, list[Any]]) -> list[list[Any]]:
        compressed: list[list[Any]] = []
        for bucket in orders.values():
            compressed.extend([order.symbol, order.price, order.quantity] for order in bucket)
        return compressed

    def _to_json(self, value: Any) -> str:
        return json.dumps(value, separators=(",", ":"))

    def _truncate(self, value: str, max_length: int) -> str:
        lo = 0
        hi = min(len(value), max_length)
        out = ""
        while lo <= hi:
            mid = (lo + hi) // 2
            candidate = value[:mid]
            if len(candidate) < len(value):
                candidate += "..."
            if len(json.dumps(candidate)) <= max_length:
                out = candidate
                lo = mid + 1
            else:
                hi = mid - 1
        return out
