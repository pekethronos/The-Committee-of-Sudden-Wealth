from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from statistics import fmean

from tcosw.models import BookSnapshot


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
