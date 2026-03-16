from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from tcosw.adapters.prosperity import orders_to_datamodel, product_state_from_order_depth
from tcosw.config import RuntimeConfig, load_runtime_config
from tcosw.logging_utils import BoundedLogger
from tcosw.strategies.basket import BasketSpreadTracker
from tcosw.strategies.dominant_liquidity import DominantLiquidityStrategy
from tcosw.strategies.fixed_fair import FixedFairStrategy


@dataclass(slots=True)
class StrategyRuntime:
    config: RuntimeConfig

    def run(self, state: object, order_cls: type) -> tuple[dict[str, list[object]], int, str]:
        logger = BoundedLogger(
            max_entries=int(self.config.logging["max_entries"]),
            max_payload_chars=int(self.config.logging["max_payload_chars"]),
        )
        result: dict[str, list[object]] = {}

        for product, product_cfg in self.config.products.items():
            if product not in state.order_depths:
                continue

            local_state = product_state_from_order_depth(
                product=product,
                order_depth=state.order_depths[product],
                position=state.position.get(product, 0),
                position_limit=int(product_cfg["position_limit"]),
            )
            strategy = self._build_strategy(product_cfg)
            local_orders = strategy.generate_orders(local_state)
            result[product] = orders_to_datamodel(local_orders, order_cls)
            logger.log(
                "product_orders",
                product=product,
                order_count=len(local_orders),
                position=local_state.position,
            )

        return result, 0, logger.serialize()

    def _build_strategy(self, product_cfg: dict[str, Any]) -> Any:
        strategy_name = product_cfg["strategy"]
        if strategy_name == "fixed_fair":
            return FixedFairStrategy(
                fair_value=int(product_cfg["fair_value"]),
                quote_width=int(product_cfg["quote_width"]),
                quote_clip=int(product_cfg["quote_clip"]),
                min_take_edge=int(product_cfg["min_take_edge"]),
                clear_threshold=int(product_cfg["clear_threshold"]),
                clear_clip=int(product_cfg["clear_clip"]),
                skew_per_unit=float(product_cfg["skew_per_unit"]),
            )
        if strategy_name == "dominant_liquidity":
            return DominantLiquidityStrategy(
                quote_width=int(product_cfg["quote_width"]),
                quote_clip=int(product_cfg["quote_clip"]),
                min_take_edge=int(product_cfg["min_take_edge"]),
                clear_threshold=int(product_cfg["clear_threshold"]),
                clear_clip=int(product_cfg["clear_clip"]),
                skew_per_unit=float(product_cfg["skew_per_unit"]),
                min_wall_size=int(product_cfg["min_wall_size"]),
            )
        raise ValueError(f"unknown strategy: {strategy_name}")


def build_runtime() -> StrategyRuntime:
    return StrategyRuntime(config=load_runtime_config())


__all__ = [
    "BasketSpreadTracker",
    "StrategyRuntime",
    "build_runtime",
]
