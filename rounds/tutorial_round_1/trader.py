from __future__ import annotations

import json
from typing import Any

from datamodel import (
    Listing,
    Observation,
    Order,
    OrderDepth,
    ProsperityEncoder,
    Symbol,
    Trade,
    TradingState,
)


EMERALDS: Symbol = "EMERALDS"
TOMATOES: Symbol = "TOMATOES"

POSITION_LIMIT = 80
EMERALDS_FAIR = 10_000

TOMATOES_EMA_WINDOW = 10
TOMATOES_REVERSION_BETA = -0.25
TOMATOES_BUY_TAKE_WIDTH = 1
TOMATOES_SELL_TAKE_WIDTH = 3
TOMATOES_CLEAR_WIDTH = 0
TOMATOES_MIN_EDGE = 2
TOMATOES_ADVERSE_VOLUME = 15
TOMATOES_SKEW_FACTOR = 0.15


class Logger:
    def __init__(self) -> None:
        self.logs = ""
        self.max_log_length = 3750

    def print(self, *objects: Any, sep: str = " ", end: str = "\n") -> None:
        self.logs += sep.join(map(str, objects)) + end

    def flush(
        self,
        state: TradingState,
        orders: dict[Symbol, list[Order]],
        conversions: int,
        trader_data: str,
    ) -> None:
        base_length = len(
            self.to_json(
                [
                    self.compress_state(state, ""),
                    self.compress_orders(orders),
                    conversions,
                    "",
                    "",
                ]
            )
        )

        max_item_length = max(0, (self.max_log_length - base_length) // 3)

        print(
            self.to_json(
                [
                    self.compress_state(state, self.truncate(state.traderData, max_item_length)),
                    self.compress_orders(orders),
                    conversions,
                    self.truncate(trader_data, max_item_length),
                    self.truncate(self.logs, max_item_length),
                ]
            )
        )

        self.logs = ""

    def compress_state(self, state: TradingState, trader_data: str) -> list[Any]:
        return [
            state.timestamp,
            trader_data,
            self.compress_listings(state.listings),
            self.compress_order_depths(state.order_depths),
            self.compress_trades(state.own_trades),
            self.compress_trades(state.market_trades),
            state.position,
            self.compress_observations(state.observations),
        ]

    def compress_listings(self, listings: dict[Symbol, Listing]) -> list[list[Any]]:
        compressed = []
        for listing in listings.values():
            if isinstance(listing, dict):
                compressed.append(
                    [
                        listing["symbol"],
                        listing["product"],
                        listing["denomination"],
                    ]
                )
            else:
                compressed.append([listing.symbol, listing.product, listing.denomination])
        return compressed

    def compress_order_depths(self, order_depths: dict[Symbol, OrderDepth]) -> dict[Symbol, list[Any]]:
        compressed = {}
        for symbol, order_depth in order_depths.items():
            compressed[symbol] = [order_depth.buy_orders, order_depth.sell_orders]
        return compressed

    def compress_trades(self, trades: dict[Symbol, list[Trade]]) -> list[list[Any]]:
        compressed = []
        for arr in trades.values():
            for trade in arr:
                compressed.append(
                    [
                        trade.symbol,
                        trade.price,
                        trade.quantity,
                        trade.buyer,
                        trade.seller,
                        trade.timestamp,
                    ]
                )
        return compressed

    def compress_observations(self, observations: Observation) -> list[Any]:
        conversion_observations = {}
        for product, observation in observations.conversionObservations.items():
            conversion_observations[product] = [
                observation.bidPrice,
                observation.askPrice,
                observation.transportFees,
                observation.exportTariff,
                observation.importTariff,
                observation.sugarPrice,
                observation.sunlightIndex,
            ]

        return [observations.plainValueObservations, conversion_observations]

    def compress_orders(self, orders: dict[Symbol, list[Order]]) -> list[list[Any]]:
        compressed = []
        for arr in orders.values():
            for order in arr:
                compressed.append([order.symbol, order.price, order.quantity])
        return compressed

    def to_json(self, value: Any) -> str:
        return json.dumps(value, cls=ProsperityEncoder, separators=(",", ":"))

    def truncate(self, value: str, max_length: int) -> str:
        lo, hi = 0, min(len(value), max_length)
        out = ""

        while lo <= hi:
            mid = (lo + hi) // 2
            candidate = value[:mid]
            if len(candidate) < len(value):
                candidate += "..."

            encoded_candidate = json.dumps(candidate)

            if len(encoded_candidate) <= max_length:
                out = candidate
                lo = mid + 1
            else:
                hi = mid - 1

        return out


logger = Logger()


def _load_state(raw: str) -> dict[str, float | None]:
    if not raw:
        return {"tomatoes_ema": None, "tomatoes_last_mid": None}
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return {"tomatoes_ema": None, "tomatoes_last_mid": None}
    if not isinstance(payload, dict):
        return {"tomatoes_ema": None, "tomatoes_last_mid": None}
    return {
        "tomatoes_ema": payload.get("tomatoes_ema"),
        "tomatoes_last_mid": payload.get("tomatoes_last_mid"),
    }


def _dump_state(payload: dict[str, float | None]) -> str:
    return json.dumps(payload, separators=(",", ":"))


class Trader:
    def compute_orders_emeralds(self, depth: OrderDepth, position: int) -> list[Order]:
        orders: list[Order] = []
        fair = EMERALDS_FAIR

        sell_orders = sorted(depth.sell_orders.items())
        buy_orders = sorted(depth.buy_orders.items(), reverse=True)

        buy_capacity = POSITION_LIMIT - position
        sell_capacity = POSITION_LIMIT + position

        for ask_price, ask_vol in sell_orders:
            if ask_price < fair and buy_capacity > 0:
                qty = min(-ask_vol, buy_capacity)
                orders.append(Order(EMERALDS, ask_price, qty))
                buy_capacity -= qty
            elif ask_price == fair and position < 0 and buy_capacity > 0:
                qty = min(-ask_vol, buy_capacity, -position)
                orders.append(Order(EMERALDS, ask_price, qty))
                buy_capacity -= qty

        for bid_price, bid_vol in buy_orders:
            if bid_price > fair and sell_capacity > 0:
                qty = min(bid_vol, sell_capacity)
                orders.append(Order(EMERALDS, bid_price, -qty))
                sell_capacity -= qty
            elif bid_price == fair and position > 0 and sell_capacity > 0:
                qty = min(bid_vol, sell_capacity, position)
                orders.append(Order(EMERALDS, bid_price, -qty))
                sell_capacity -= qty

        best_bid = max(depth.buy_orders.keys(), default=None)
        best_ask = min(depth.sell_orders.keys(), default=None)

        bid_price = min(best_bid + 1, fair - 1) if best_bid is not None else fair - 1
        ask_price = max(best_ask - 1, fair + 1) if best_ask is not None else fair + 1

        if buy_capacity > 0:
            orders.append(Order(EMERALDS, bid_price, buy_capacity))

        if sell_capacity > 0:
            orders.append(Order(EMERALDS, ask_price, -sell_capacity))

        return orders

    def update_tomatoes_fair(
        self,
        mid: float,
        tomatoes_ema: float | None,
        tomatoes_last_mid: float | None,
    ) -> tuple[float, float, float]:
        alpha = 2.0 / (TOMATOES_EMA_WINDOW + 1)

        if tomatoes_ema is None:
            tomatoes_ema = mid
        else:
            tomatoes_ema += alpha * (mid - tomatoes_ema)

        fair = tomatoes_ema
        if tomatoes_last_mid is not None:
            last_return = (mid - tomatoes_last_mid) / tomatoes_last_mid
            pred_return = last_return * TOMATOES_REVERSION_BETA
            fair += fair * pred_return

        return fair, tomatoes_ema, mid

    def compute_orders_tomatoes(
        self,
        depth: OrderDepth,
        position: int,
        tomatoes_ema: float | None,
        tomatoes_last_mid: float | None,
    ) -> tuple[list[Order], float, float]:
        best_bid = max(depth.buy_orders.keys(), default=None)
        best_ask = min(depth.sell_orders.keys(), default=None)
        if best_bid is None or best_ask is None:
            if tomatoes_ema is None:
                tomatoes_ema = 0.0
            if tomatoes_last_mid is None:
                tomatoes_last_mid = 0.0
            return [], tomatoes_ema, tomatoes_last_mid

        mid = (best_bid + best_ask) / 2.0
        raw_fair, tomatoes_ema, tomatoes_last_mid = self.update_tomatoes_fair(
            mid, tomatoes_ema, tomatoes_last_mid
        )
        fair = raw_fair - position * TOMATOES_SKEW_FACTOR

        orders: list[Order] = []
        sell_orders = sorted(depth.sell_orders.items())
        buy_orders = sorted(depth.buy_orders.items(), reverse=True)

        buy_capacity = POSITION_LIMIT - position
        sell_capacity = POSITION_LIMIT + position

        for ask_price, ask_vol in sell_orders:
            if ask_price > fair - TOMATOES_BUY_TAKE_WIDTH:
                break
            if abs(ask_vol) >= TOMATOES_ADVERSE_VOLUME:
                continue
            qty = min(-ask_vol, buy_capacity)
            if qty <= 0:
                break
            orders.append(Order(TOMATOES, ask_price, qty))
            buy_capacity -= qty

        for bid_price, bid_vol in buy_orders:
            if bid_price < fair + TOMATOES_SELL_TAKE_WIDTH:
                break
            if bid_vol >= TOMATOES_ADVERSE_VOLUME:
                continue
            qty = min(bid_vol, sell_capacity)
            if qty <= 0:
                break
            orders.append(Order(TOMATOES, bid_price, -qty))
            sell_capacity -= qty

        if position > 0:
            clear_price = int(round(fair + TOMATOES_CLEAR_WIDTH))
            for bid_price, bid_vol in buy_orders:
                if bid_price < clear_price:
                    break
                qty = min(bid_vol, sell_capacity, position)
                if qty <= 0:
                    break
                orders.append(Order(TOMATOES, bid_price, -qty))
                sell_capacity -= qty
                position -= qty
        elif position < 0:
            clear_price = int(round(fair - TOMATOES_CLEAR_WIDTH))
            for ask_price, ask_vol in sell_orders:
                if ask_price > clear_price:
                    break
                qty = min(-ask_vol, buy_capacity, -position)
                if qty <= 0:
                    break
                orders.append(Order(TOMATOES, ask_price, qty))
                buy_capacity -= qty
                position += qty

        bid_price = min(best_bid + 1, int(round(fair)) - TOMATOES_MIN_EDGE)
        ask_price = max(best_ask - 1, int(round(fair)) + TOMATOES_MIN_EDGE)

        if buy_capacity > 0:
            orders.append(Order(TOMATOES, bid_price, buy_capacity))

        if sell_capacity > 0:
            orders.append(Order(TOMATOES, ask_price, -sell_capacity))

        return orders, tomatoes_ema, tomatoes_last_mid

    def run(self, state: TradingState) -> tuple[dict[Symbol, list[Order]], int, str]:
        persisted = _load_state(state.traderData)
        tomatoes_ema = persisted["tomatoes_ema"]
        tomatoes_last_mid = persisted["tomatoes_last_mid"]

        orders: dict[Symbol, list[Order]] = {}
        conversions = 0

        emeralds_depth = state.order_depths.get(EMERALDS)
        if emeralds_depth is not None:
            orders[EMERALDS] = self.compute_orders_emeralds(
                emeralds_depth, state.position.get(EMERALDS, 0)
            )

        tomatoes_depth = state.order_depths.get(TOMATOES)
        if tomatoes_depth is not None:
            tomatoes_orders, tomatoes_ema, tomatoes_last_mid = self.compute_orders_tomatoes(
                tomatoes_depth,
                state.position.get(TOMATOES, 0),
                tomatoes_ema if isinstance(tomatoes_ema, (int, float)) else None,
                tomatoes_last_mid if isinstance(tomatoes_last_mid, (int, float)) else None,
            )
            orders[TOMATOES] = tomatoes_orders

        trader_data = _dump_state(
            {
                "tomatoes_ema": tomatoes_ema,
                "tomatoes_last_mid": tomatoes_last_mid,
            }
        )
        logger.flush(state, orders, conversions, trader_data)
        return orders, conversions, trader_data
