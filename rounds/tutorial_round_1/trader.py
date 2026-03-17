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

TOMATOES_MODE = "ema_reversion"
TOMATOES_EMA_WINDOW = 10
TOMATOES_REVERSION_BETA = -0.25
TOMATOES_BUY_TAKE_WIDTH = 1
TOMATOES_SELL_TAKE_WIDTH = 3
TOMATOES_CLEAR_WIDTH = 0
TOMATOES_MIN_EDGE = 2
TOMATOES_MIN_WALL_SIZE = 15
TOMATOES_LARGE_LEVEL_EXTRA_EDGE = 2
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


def _empty_state() -> dict[str, float | int | str | None]:
    return {
        "tomatoes_mode": None,
        "tomatoes_ema": None,
        "tomatoes_last_mid": None,
        "tomatoes_last_wall_mid": None,
        "tomatoes_wall_seen_count": 0,
    }


def _load_state(raw: str) -> dict[str, float | int | str | None]:
    state = _empty_state()
    if not raw:
        return state
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return state
    if not isinstance(payload, dict):
        return state
    state["tomatoes_mode"] = payload.get("tomatoes_mode")
    state["tomatoes_ema"] = payload.get("tomatoes_ema")
    state["tomatoes_last_mid"] = payload.get("tomatoes_last_mid")
    state["tomatoes_last_wall_mid"] = payload.get("tomatoes_last_wall_mid")
    wall_seen_count = payload.get("tomatoes_wall_seen_count", 0)
    state["tomatoes_wall_seen_count"] = wall_seen_count if isinstance(wall_seen_count, int) else 0
    return state


def _dump_state(payload: dict[str, float | int | str | None]) -> str:
    return json.dumps(payload, separators=(",", ":"))


def _pick_largest_level(levels: dict[int, int], is_bid: bool) -> tuple[int | None, int]:
    if not levels:
        return None, 0
    price, volume = max(
        levels.items(),
        key=lambda item: (abs(item[1]), item[0] if is_bid else -item[0]),
    )
    return price, abs(volume)


def compute_tomatoes_book_features(depth: OrderDepth) -> dict[str, int | float | None]:
    best_bid = max(depth.buy_orders.keys(), default=None)
    best_ask = min(depth.sell_orders.keys(), default=None)
    raw_mid = None
    spread = None
    if best_bid is not None and best_ask is not None:
        raw_mid = (best_bid + best_ask) / 2.0
        spread = best_ask - best_bid

    largest_bid_price, largest_bid_size = _pick_largest_level(depth.buy_orders, is_bid=True)
    largest_ask_price, largest_ask_size = _pick_largest_level(depth.sell_orders, is_bid=False)

    wall_mid = None
    if (
        largest_bid_price is not None
        and largest_ask_price is not None
        and largest_bid_size >= TOMATOES_MIN_WALL_SIZE
        and largest_ask_size >= TOMATOES_MIN_WALL_SIZE
    ):
        wall_mid = (largest_bid_price + largest_ask_price) / 2.0

    return {
        "best_bid": best_bid,
        "best_ask": best_ask,
        "raw_mid": raw_mid,
        "spread": spread,
        "largest_bid_price": largest_bid_price,
        "largest_bid_size": largest_bid_size,
        "largest_ask_price": largest_ask_price,
        "largest_ask_size": largest_ask_size,
        "wall_mid": wall_mid,
    }


def is_large_tomatoes_level(volume: int) -> bool:
    return abs(volume) >= TOMATOES_MIN_WALL_SIZE


def tomatoes_take_width(base_width: int, volume: int) -> int:
    return base_width + (TOMATOES_LARGE_LEVEL_EXTRA_EDGE if is_large_tomatoes_level(volume) else 0)


def tomatoes_quote_caps(position: int) -> tuple[int, int]:
    abs_position = abs(position)
    if abs_position <= 10:
        increasing_clip, reducing_clip = 20, 20
    elif abs_position <= 25:
        increasing_clip, reducing_clip = 12, 20
    elif abs_position <= 40:
        increasing_clip, reducing_clip = 6, 16
    else:
        increasing_clip, reducing_clip = 0, 12

    buy_clip = reducing_clip if position < 0 else increasing_clip
    sell_clip = reducing_clip if position > 0 else increasing_clip
    return buy_clip, sell_clip


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

    def estimate_tomatoes_fair(
        self,
        features: dict[str, int | float | None],
        persisted: dict[str, float | int | str | None],
        strategy_mode: str,
    ) -> tuple[float, dict[str, float | int | str | None]]:
        raw_mid = features["raw_mid"]
        wall_mid = features["wall_mid"]
        if not isinstance(raw_mid, (int, float)):
            updated = _empty_state()
            updated.update(persisted)
            updated["tomatoes_mode"] = strategy_mode
            return 0.0, updated

        tomatoes_ema = persisted["tomatoes_ema"]
        tomatoes_last_mid = persisted["tomatoes_last_mid"]
        ema_fair, tomatoes_ema, tomatoes_last_mid = self.update_tomatoes_fair(
            float(raw_mid),
            tomatoes_ema if isinstance(tomatoes_ema, (int, float)) else None,
            tomatoes_last_mid if isinstance(tomatoes_last_mid, (int, float)) else None,
        )

        dominant_liquidity_fair = float(wall_mid) if isinstance(wall_mid, (int, float)) else float(raw_mid)
        selected_mode = strategy_mode
        if strategy_mode == "dominant_liquidity":
            fair = dominant_liquidity_fair
        elif strategy_mode == "hybrid":
            if isinstance(wall_mid, (int, float)):
                fair = dominant_liquidity_fair
                selected_mode = "dominant_liquidity"
            else:
                fair = ema_fair
                selected_mode = "ema_reversion"
        else:
            fair = ema_fair
            selected_mode = "ema_reversion"

        updated = _empty_state()
        updated.update(persisted)
        updated["tomatoes_mode"] = selected_mode
        updated["tomatoes_ema"] = tomatoes_ema
        updated["tomatoes_last_mid"] = tomatoes_last_mid
        if isinstance(wall_mid, (int, float)):
            updated["tomatoes_last_wall_mid"] = float(wall_mid)
            updated["tomatoes_wall_seen_count"] = int(updated["tomatoes_wall_seen_count"]) + 1

        return fair, updated

    def compute_orders_tomatoes_baseline(
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
            if is_large_tomatoes_level(ask_vol):
                continue
            qty = min(-ask_vol, buy_capacity)
            if qty <= 0:
                break
            orders.append(Order(TOMATOES, ask_price, qty))
            buy_capacity -= qty

        for bid_price, bid_vol in buy_orders:
            if bid_price < fair + TOMATOES_SELL_TAKE_WIDTH:
                break
            if is_large_tomatoes_level(bid_vol):
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

    def compute_orders_tomatoes_experimental(
        self,
        depth: OrderDepth,
        position: int,
        persisted: dict[str, float | int | str | None],
        strategy_mode: str,
    ) -> tuple[list[Order], dict[str, float | int | str | None]]:
        features = compute_tomatoes_book_features(depth)
        updated_state = _empty_state()
        updated_state.update(persisted)

        best_bid = features["best_bid"]
        best_ask = features["best_ask"]
        if not isinstance(best_bid, int) or not isinstance(best_ask, int):
            updated_state["tomatoes_mode"] = strategy_mode
            return [], updated_state

        fair, updated_state = self.estimate_tomatoes_fair(features, updated_state, strategy_mode)
        fair -= position * TOMATOES_SKEW_FACTOR

        orders: list[Order] = []
        sell_orders = sorted(depth.sell_orders.items())
        buy_orders = sorted(depth.buy_orders.items(), reverse=True)

        buy_capacity = POSITION_LIMIT - position
        sell_capacity = POSITION_LIMIT + position
        projected_position = position

        for ask_price, ask_vol in sell_orders:
            take_width = tomatoes_take_width(TOMATOES_BUY_TAKE_WIDTH, ask_vol)
            if ask_price > fair - take_width:
                break
            qty = min(-ask_vol, buy_capacity)
            if qty <= 0:
                break
            orders.append(Order(TOMATOES, ask_price, qty))
            buy_capacity -= qty
            projected_position += qty

        for bid_price, bid_vol in buy_orders:
            take_width = tomatoes_take_width(TOMATOES_SELL_TAKE_WIDTH, bid_vol)
            if bid_price < fair + take_width:
                break
            qty = min(bid_vol, sell_capacity)
            if qty <= 0:
                break
            orders.append(Order(TOMATOES, bid_price, -qty))
            sell_capacity -= qty
            projected_position -= qty

        clearing_position = projected_position
        if clearing_position > 0:
            clear_price = int(round(fair + TOMATOES_CLEAR_WIDTH))
            for bid_price, bid_vol in buy_orders:
                if bid_price < clear_price:
                    break
                qty = min(bid_vol, sell_capacity, clearing_position)
                if qty <= 0:
                    break
                orders.append(Order(TOMATOES, bid_price, -qty))
                sell_capacity -= qty
                clearing_position -= qty
                projected_position -= qty
        elif clearing_position < 0:
            clear_price = int(round(fair - TOMATOES_CLEAR_WIDTH))
            for ask_price, ask_vol in sell_orders:
                if ask_price > clear_price:
                    break
                qty = min(-ask_vol, buy_capacity, -clearing_position)
                if qty <= 0:
                    break
                orders.append(Order(TOMATOES, ask_price, qty))
                buy_capacity -= qty
                clearing_position += qty
                projected_position += qty

        bid_price = min(best_bid + 1, int(round(fair)) - TOMATOES_MIN_EDGE)
        ask_price = max(best_ask - 1, int(round(fair)) + TOMATOES_MIN_EDGE)
        buy_quote_cap, sell_quote_cap = tomatoes_quote_caps(projected_position)

        if buy_capacity > 0 and buy_quote_cap > 0:
            orders.append(Order(TOMATOES, bid_price, min(buy_capacity, buy_quote_cap)))

        if sell_capacity > 0 and sell_quote_cap > 0:
            orders.append(Order(TOMATOES, ask_price, -min(sell_capacity, sell_quote_cap)))

        return orders, updated_state

    def compute_orders_tomatoes(
        self,
        depth: OrderDepth,
        position: int,
        persisted: dict[str, float | int | str | None],
    ) -> tuple[list[Order], dict[str, float | int | str | None]]:
        features = compute_tomatoes_book_features(depth)
        if TOMATOES_MODE == "baseline":
            baseline_orders, tomatoes_ema, tomatoes_last_mid = self.compute_orders_tomatoes_baseline(
                depth,
                position,
                persisted["tomatoes_ema"] if isinstance(persisted["tomatoes_ema"], (int, float)) else None,
                persisted["tomatoes_last_mid"] if isinstance(persisted["tomatoes_last_mid"], (int, float)) else None,
            )
            updated_state = _empty_state()
            updated_state.update(persisted)
            updated_state["tomatoes_mode"] = "baseline"
            updated_state["tomatoes_ema"] = tomatoes_ema
            updated_state["tomatoes_last_mid"] = tomatoes_last_mid
            wall_mid = features["wall_mid"]
            if isinstance(wall_mid, (int, float)):
                updated_state["tomatoes_last_wall_mid"] = float(wall_mid)
                updated_state["tomatoes_wall_seen_count"] = int(updated_state["tomatoes_wall_seen_count"]) + 1
            return baseline_orders, updated_state

        return self.compute_orders_tomatoes_experimental(depth, position, persisted, TOMATOES_MODE)

    def run(self, state: TradingState) -> tuple[dict[Symbol, list[Order]], int, str]:
        persisted = _load_state(state.traderData)

        orders: dict[Symbol, list[Order]] = {}
        conversions = 0

        emeralds_depth = state.order_depths.get(EMERALDS)
        if emeralds_depth is not None:
            orders[EMERALDS] = self.compute_orders_emeralds(
                emeralds_depth, state.position.get(EMERALDS, 0)
            )

        tomatoes_depth = state.order_depths.get(TOMATOES)
        if tomatoes_depth is not None:
            tomatoes_orders, persisted = self.compute_orders_tomatoes(
                tomatoes_depth,
                state.position.get(TOMATOES, 0),
                persisted,
            )
            orders[TOMATOES] = tomatoes_orders

        trader_data = _dump_state(persisted)
        logger.flush(state, orders, conversions, trader_data)
        return orders, conversions, trader_data
