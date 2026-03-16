from __future__ import annotations

import json
from typing import Any, Dict, List, Tuple

from prosperity3bt.datamodel import (
    Listing,
    Observation,
    Order,
    OrderDepth,
    ProsperityEncoder,
    Symbol,
    Trade,
    TradingState,
)


class Logger:
    def __init__(self) -> None:
        self.logs = ""
        self.max_log_length = 3750

    def print(self, *objects: Any, sep: str = " ", end: str = "\n") -> None:
        self.logs += sep.join(map(str, objects)) + end

    def flush(self, state: TradingState, orders: dict[Symbol, list[Order]], conversions: int, trader_data: str) -> None:
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

        max_item_length = (self.max_log_length - base_length) // 3

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


EMERALDS: Symbol = "EMERALDS"
TOMATOES: Symbol = "TOMATOES"


POSITION_LIMIT = 80
EMERALDS_FAIR = 10_000

TOMATOES_EMA_WINDOW = 10
TOMATOES_REVERSION_BETA = -0.25
TOMATOES_TAKE_WIDTH = 1
TOMATOES_CLEAR_WIDTH = 0
TOMATOES_MIN_EDGE = 2
TOMATOES_ADVERSE_VOLUME = 15
TOMATOES_SKEW_FACTOR = 0.15


class Trader:
    def __init__(self) -> None:
        self.tomatoes_ema: float | None = None
        self.tomatoes_last_mid: float | None = None

    # ------------------------------------------------------------------
    # EMERALDS  –  fixed fair value market-maker  (take / clear / make)
    # ------------------------------------------------------------------

    def compute_orders_emeralds(
        self, depth: OrderDepth, position: int
    ) -> list[Order]:
        orders: list[Order] = []
        fair = EMERALDS_FAIR

        sell_orders = sorted(depth.sell_orders.items())            # ascending
        buy_orders = sorted(depth.buy_orders.items(), reverse=True)  # descending

        buy_capacity = POSITION_LIMIT - position
        sell_capacity = POSITION_LIMIT + position

        # --- Phase 1: TAKE mispriced liquidity ---

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

        # --- Phase 2: MAKE the market (penny the spread) ---

        best_bid = max(depth.buy_orders.keys(), default=None)
        best_ask = min(depth.sell_orders.keys(), default=None)

        if best_bid is not None:
            bid_price = min(best_bid + 1, fair - 1)
        else:
            bid_price = fair - 1

        if best_ask is not None:
            ask_price = max(best_ask - 1, fair + 1)
        else:
            ask_price = fair + 1

        if buy_capacity > 0:
            orders.append(Order(EMERALDS, bid_price, buy_capacity))

        if sell_capacity > 0:
            orders.append(Order(EMERALDS, ask_price, -sell_capacity))

        return orders

    # ------------------------------------------------------------------
    # TOMATOES  –  EMA + mean-reversion dynamic market-maker
    # ------------------------------------------------------------------

    def _update_tomatoes_fair(self, mid: float) -> float:
        alpha = 2.0 / (TOMATOES_EMA_WINDOW + 1)

        if self.tomatoes_ema is None:
            self.tomatoes_ema = mid
        else:
            self.tomatoes_ema += alpha * (mid - self.tomatoes_ema)

        fair = self.tomatoes_ema

        if self.tomatoes_last_mid is not None:
            last_return = (mid - self.tomatoes_last_mid) / self.tomatoes_last_mid
            pred_return = last_return * TOMATOES_REVERSION_BETA
            fair = fair + fair * pred_return

        self.tomatoes_last_mid = mid
        return fair

    def compute_orders_tomatoes(
        self, depth: OrderDepth, position: int
    ) -> list[Order]:
        best_bid = max(depth.buy_orders.keys(), default=None)
        best_ask = min(depth.sell_orders.keys(), default=None)
        if best_bid is None or best_ask is None:
            return []

        mid = (best_bid + best_ask) / 2.0
        raw_fair = self._update_tomatoes_fair(mid)

        skewed_fair = raw_fair - position * TOMATOES_SKEW_FACTOR
        fair = skewed_fair

        orders: list[Order] = []
        sell_orders = sorted(depth.sell_orders.items())
        buy_orders = sorted(depth.buy_orders.items(), reverse=True)

        buy_capacity = POSITION_LIMIT - position
        sell_capacity = POSITION_LIMIT + position

        # --- Phase 1: TAKE mispriced (with adverse-selection filter) ---

        for ask_price, ask_vol in sell_orders:
            if ask_price > fair - TOMATOES_TAKE_WIDTH:
                break
            if abs(ask_vol) >= TOMATOES_ADVERSE_VOLUME:
                continue
            qty = min(-ask_vol, buy_capacity)
            if qty <= 0:
                break
            orders.append(Order(TOMATOES, ask_price, qty))
            buy_capacity -= qty

        for bid_price, bid_vol in buy_orders:
            if bid_price < fair + TOMATOES_TAKE_WIDTH:
                break
            if bid_vol >= TOMATOES_ADVERSE_VOLUME:
                continue
            qty = min(bid_vol, sell_capacity)
            if qty <= 0:
                break
            orders.append(Order(TOMATOES, bid_price, -qty))
            sell_capacity -= qty

        # --- Phase 2: CLEAR inventory toward zero ---

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

        # --- Phase 3: MAKE the market ---

        bid_price = min(best_bid + 1, int(round(fair)) - TOMATOES_MIN_EDGE)
        ask_price = max(best_ask - 1, int(round(fair)) + TOMATOES_MIN_EDGE)

        if buy_capacity > 0:
            orders.append(Order(TOMATOES, bid_price, buy_capacity))

        if sell_capacity > 0:
            orders.append(Order(TOMATOES, ask_price, -sell_capacity))

        return orders

    # ------------------------------------------------------------------
    # Main entry point
    # ------------------------------------------------------------------

    def run(self, state: TradingState) -> tuple[dict[Symbol, list[Order]], int, str]:
        orders: dict[Symbol, list[Order]] = {}
        conversions = 0
        trader_data = ""

        emeralds_depth = state.order_depths.get(EMERALDS)
        if emeralds_depth is not None:
            orders[EMERALDS] = self.compute_orders_emeralds(
                emeralds_depth, state.position.get(EMERALDS, 0)
            )

        tomatoes_depth = state.order_depths.get(TOMATOES)
        if tomatoes_depth is not None:
            orders[TOMATOES] = self.compute_orders_tomatoes(
                tomatoes_depth, state.position.get(TOMATOES, 0)
            )

        logger.flush(state, orders, conversions, trader_data)
        return orders, conversions, trader_data

