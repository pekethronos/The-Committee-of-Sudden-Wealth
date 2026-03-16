from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class OrderLevel:
    price: int
    quantity: int


@dataclass(frozen=True, slots=True)
class BookSnapshot:
    bids: tuple[OrderLevel, ...]
    asks: tuple[OrderLevel, ...]


@dataclass(frozen=True, slots=True)
class ProductState:
    product: str
    position: int
    position_limit: int
    book: BookSnapshot


@dataclass(frozen=True, slots=True)
class Order:
    product: str
    price: int
    quantity: int

    @property
    def side(self) -> str:
        return "BUY" if self.quantity > 0 else "SELL"
