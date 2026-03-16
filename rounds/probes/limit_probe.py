from datamodel import Order, TradingState


class Trader:
    def run(self, state: TradingState):
        return {
            "RAINFOREST_RESIN": [
                Order("RAINFOREST_RESIN", 10002, 30),
                Order("RAINFOREST_RESIN", 10002, 30),
            ]
        }, 0, ""
