from datamodel import Order, TradingState


class Trader:
    def run(self, state: TradingState):
        if state.timestamp == 0:
            return {"RAINFOREST_RESIN": [Order("RAINFOREST_RESIN", 10000, 1)]}, 0, ""
        return {}, 0, ""
