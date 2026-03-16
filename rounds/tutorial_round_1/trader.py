from datamodel import Order, TradingState
from tcosw.prosperity_logger import ProsperityLogger
from tcosw.runtime import build_runtime


TUTORIAL_ROUND_1_CONFIG = {
    "products": {
        "EMERALDS": {
            "strategy": "fixed_fair",
            "fair_value": 10000,
            "quote_width": 1,
            "quote_clip": 4,
            "min_take_edge": 1,
            "clear_threshold": 12,
            "clear_clip": 6,
            "skew_per_unit": 0.05,
            "position_limit": 80,
        },
        "TOMATOES": {
            "strategy": "dominant_liquidity",
            "quote_width": 1,
            "quote_clip": 3,
            "min_take_edge": 1,
            "clear_threshold": 10,
            "clear_clip": 5,
            "skew_per_unit": 0.04,
            "position_limit": 80,
            "min_wall_size": 6,
        },
    },
    "baskets": {},
}


class Trader:
    def __init__(self) -> None:
        self.logger = ProsperityLogger()
        self.runtime = build_runtime(config_override=TUTORIAL_ROUND_1_CONFIG)

    def run(self, state: TradingState):
        result, conversions, trader_data, runtime_log = self.runtime.run(state, Order)
        self.logger.flush(state, result, conversions, trader_data, runtime_log)
        return result, conversions, trader_data
