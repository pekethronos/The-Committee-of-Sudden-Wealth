import json
from datamodel import Order, TradingState
from tcosw.runtime import build_runtime


class Trader:
    def __init__(self) -> None:
        self.runtime = build_runtime()

    def run(self, state: TradingState):
        result, conversions, trader_data = self.runtime.run(state, Order)
        return result, conversions, trader_data
