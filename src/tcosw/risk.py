from __future__ import annotations


def buy_capacity(position: int, limit: int) -> int:
    return max(0, limit - position)


def sell_capacity(position: int, limit: int) -> int:
    return max(0, position + limit)


def clamp_buy_size(requested: int, position: int, limit: int) -> int:
    if requested < 0:
        raise ValueError("requested buy size must be non-negative")
    return min(requested, buy_capacity(position, limit))


def clamp_sell_size(requested: int, position: int, limit: int) -> int:
    if requested < 0:
        raise ValueError("requested sell size must be non-negative")
    return min(requested, sell_capacity(position, limit))
