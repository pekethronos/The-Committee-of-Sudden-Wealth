from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ConversionQuote:
    external_bid: float
    external_ask: float
    transport_fees: float
    export_tariff: float
    import_tariff: float


def break_even_local_bid(quote: ConversionQuote) -> float:
    return quote.external_ask + quote.transport_fees + quote.import_tariff


def break_even_local_ask(quote: ConversionQuote) -> float:
    return quote.external_bid - quote.transport_fees - quote.export_tariff


def local_sell_edge(local_bid: float, quote: ConversionQuote) -> float:
    return local_bid - break_even_local_bid(quote)


def local_buy_edge(local_ask: float, quote: ConversionQuote) -> float:
    return break_even_local_ask(quote) - local_ask


def suggested_taker_sell_price(quote: ConversionQuote, max_improving_ticks: float = 0.5) -> int:
    return int(quote.external_bid + max_improving_ticks)


def flatten_conversion_size(position: int, conversion_limit: int) -> int:
    if position == 0:
        return 0
    if position > 0:
        return -min(position, conversion_limit)
    return min(-position, conversion_limit)
