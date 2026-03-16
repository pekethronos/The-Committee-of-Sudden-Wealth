from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from math import floor
from statistics import fmean

from tcosw.models import BookSnapshot, Order, ProductState
from tcosw.risk import clamp_buy_size, clamp_sell_size


def book_mid(book: BookSnapshot) -> float | None:
    if not book.bids or not book.asks:
        return None
    return (book.bids[0].price + book.asks[0].price) / 2.0


def synthetic_value(component_mids: dict[str, float], weights: dict[str, int]) -> float:
    return sum(component_mids[product] * weight for product, weight in weights.items())


@dataclass(slots=True)
class BasketSignal:
    spread: float
    premium_mean: float
    zscore: float


@dataclass(slots=True)
class BasketSpreadTracker:
    weights: dict[str, int]
    premium_window: int = 50
    volatility_window: int = 25
    history: deque[float] = field(default_factory=deque)

    def update(
        self,
        basket_book: BookSnapshot,
        component_books: dict[str, BookSnapshot],
    ) -> BasketSignal | None:
        basket_mid = book_mid(basket_book)
        if basket_mid is None:
            return None

        component_mids: dict[str, float] = {}
        for product, book in component_books.items():
            mid = book_mid(book)
            if mid is None:
                return None
            component_mids[product] = mid

        raw_spread = basket_mid - synthetic_value(component_mids, self.weights)
        self.history.append(raw_spread)
        max_len = max(self.premium_window, self.volatility_window)
        while len(self.history) > max_len:
            self.history.popleft()

        premium_mean = fmean(list(self.history)[-self.premium_window :])
        centered = raw_spread - premium_mean
        recent = list(self.history)[-self.volatility_window :]
        if len(recent) < 2:
            return BasketSignal(spread=centered, premium_mean=premium_mean, zscore=0.0)

        variance = fmean([(value - fmean(recent)) ** 2 for value in recent])
        std = variance**0.5
        zscore = 0.0 if std == 0 else centered / std
        return BasketSignal(spread=centered, premium_mean=premium_mean, zscore=zscore)

    def restore_history(self, values: list[float]) -> None:
        self.history.clear()
        max_len = max(self.premium_window, self.volatility_window)
        for value in values[-max_len:]:
            self.history.append(float(value))

    def snapshot_history(self) -> list[float]:
        return list(self.history)


@dataclass(frozen=True, slots=True)
class BasketExecutionResult:
    signal: BasketSignal | None
    orders: dict[str, list[Order]]


@dataclass(slots=True)
class BasketArbitrageStrategy:
    basket: str
    weights: dict[str, int]
    tracker: BasketSpreadTracker
    entry_zscore: float = 2.0
    exit_zscore: float = 0.5
    max_units: int = 5
    hedge_components: bool = True
    min_history: int | None = None

    def generate_orders(
        self,
        states: dict[str, ProductState],
    ) -> BasketExecutionResult:
        basket_state = states.get(self.basket)
        if basket_state is None:
            return BasketExecutionResult(signal=None, orders={})

        component_states = {
            product: state for product, state in states.items() if product in self.weights
        }
        if len(component_states) != len(self.weights):
            return BasketExecutionResult(signal=None, orders={})

        signal = self.tracker.update(
            basket_book=basket_state.book,
            component_books={product: state.book for product, state in component_states.items()},
        )
        if signal is None:
            return BasketExecutionResult(signal=None, orders={})

        min_history = self.min_history if self.min_history is not None else self.tracker.volatility_window
        enough_history = len(self.tracker.history) >= min_history

        if enough_history and signal.zscore >= self.entry_zscore:
            orders = self._enter_short_basket(basket_state, component_states)
        elif enough_history and signal.zscore <= -self.entry_zscore:
            orders = self._enter_long_basket(basket_state, component_states)
        elif abs(signal.zscore) <= self.exit_zscore:
            orders = self._flatten_positions(basket_state, component_states)
        else:
            orders = {}

        return BasketExecutionResult(signal=signal, orders=orders)

    def _enter_short_basket(
        self,
        basket_state: ProductState,
        component_states: dict[str, ProductState],
    ) -> dict[str, list[Order]]:
        if not basket_state.book.bids:
            return {}

        limit_units = clamp_sell_size(self.max_units, basket_state.position, basket_state.position_limit)
        book_units = basket_state.book.bids[0].quantity
        units = min(limit_units, book_units)

        if self.hedge_components:
            for product, weight in self.weights.items():
                state = component_states[product]
                if not state.book.asks:
                    return {}
                component_capacity = clamp_buy_size(self.max_units * weight, state.position, state.position_limit)
                units = min(units, floor(component_capacity / weight), floor(state.book.asks[0].quantity / weight))

        if units <= 0:
            return {}

        orders: dict[str, list[Order]] = {
            basket_state.product: [
                Order(product=basket_state.product, price=basket_state.book.bids[0].price, quantity=-units)
            ]
        }
        if not self.hedge_components:
            return orders

        for product, weight in self.weights.items():
            state = component_states[product]
            orders.setdefault(product, []).append(
                Order(product=product, price=state.book.asks[0].price, quantity=units * weight)
            )
        return orders

    def _enter_long_basket(
        self,
        basket_state: ProductState,
        component_states: dict[str, ProductState],
    ) -> dict[str, list[Order]]:
        if not basket_state.book.asks:
            return {}

        limit_units = clamp_buy_size(self.max_units, basket_state.position, basket_state.position_limit)
        book_units = basket_state.book.asks[0].quantity
        units = min(limit_units, book_units)

        if self.hedge_components:
            for product, weight in self.weights.items():
                state = component_states[product]
                if not state.book.bids:
                    return {}
                component_capacity = clamp_sell_size(self.max_units * weight, state.position, state.position_limit)
                units = min(units, floor(component_capacity / weight), floor(state.book.bids[0].quantity / weight))

        if units <= 0:
            return {}

        orders: dict[str, list[Order]] = {
            basket_state.product: [
                Order(product=basket_state.product, price=basket_state.book.asks[0].price, quantity=units)
            ]
        }
        if not self.hedge_components:
            return orders

        for product, weight in self.weights.items():
            state = component_states[product]
            orders.setdefault(product, []).append(
                Order(product=product, price=state.book.bids[0].price, quantity=-(units * weight))
            )
        return orders

    def _flatten_positions(
        self,
        basket_state: ProductState,
        component_states: dict[str, ProductState],
    ) -> dict[str, list[Order]]:
        orders: dict[str, list[Order]] = {}
        basket_order = _flatten_top_of_book(basket_state)
        if basket_order is not None:
            orders.setdefault(basket_state.product, []).append(basket_order)

        if not self.hedge_components:
            return orders

        for state in component_states.values():
            component_order = _flatten_top_of_book(state)
            if component_order is not None:
                orders.setdefault(state.product, []).append(component_order)
        return orders


def _flatten_top_of_book(state: ProductState) -> Order | None:
    if state.position > 0:
        if not state.book.bids:
            return None
        size = clamp_sell_size(min(state.position, state.book.bids[0].quantity), state.position, state.position_limit)
        if size <= 0:
            return None
        return Order(product=state.product, price=state.book.bids[0].price, quantity=-size)
    if state.position < 0:
        if not state.book.asks:
            return None
        size = clamp_buy_size(min(-state.position, state.book.asks[0].quantity), state.position, state.position_limit)
        if size <= 0:
            return None
        return Order(product=state.product, price=state.book.asks[0].price, quantity=size)
    return None
