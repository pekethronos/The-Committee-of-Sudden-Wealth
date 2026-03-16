from __future__ import annotations

from tcosw.models import BookSnapshot, OrderLevel


def fixed_fair_value(value: int) -> float:
    return float(value)


def top_of_book_mid(book: BookSnapshot) -> float | None:
    if not book.bids or not book.asks:
        return None
    return (book.bids[0].price + book.asks[0].price) / 2.0


def dominant_liquidity_fair(book: BookSnapshot, min_depth: int = 1) -> float | None:
    bid = _deepest_level(book.bids, min_depth)
    ask = _deepest_level(book.asks, min_depth)
    if bid is None or ask is None:
        return top_of_book_mid(book)
    return (bid.price + ask.price) / 2.0


def _deepest_level(levels: tuple[OrderLevel, ...], min_depth: int) -> OrderLevel | None:
    candidates = [level for level in levels if level.quantity >= min_depth]
    if not candidates:
        return None
    return max(candidates, key=lambda level: (level.quantity, level.price))
