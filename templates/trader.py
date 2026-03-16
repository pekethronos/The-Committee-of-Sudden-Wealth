from datamodel import Order, TradingState
from tcosw.prosperity_logger import ProsperityLogger
from tcosw.runtime import build_runtime


class Trader:
    def __init__(self) -> None:
        self.logger = ProsperityLogger()
        self.runtime = build_runtime()

    def run(self, state: TradingState):
        result, conversions, trader_data, runtime_log = self.runtime.run(state, Order)
        self.logger.flush(state, result, conversions, trader_data, runtime_log)
        return result, conversions, trader_data
