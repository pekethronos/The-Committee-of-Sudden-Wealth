from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from tcosw.adapters.prosperity import orders_to_datamodel, product_state_from_order_depth
from tcosw.config import RuntimeConfig, load_runtime_config
from tcosw.logging_utils import BoundedLogger
from tcosw.strategies.basket import BasketArbitrageStrategy, BasketSpreadTracker
from tcosw.strategies.dominant_liquidity import DominantLiquidityStrategy
from tcosw.strategies.fixed_fair import FixedFairStrategy


@dataclass(slots=True)
class StrategyRuntime:
    config: RuntimeConfig

    def run(self, state: object, order_cls: type) -> tuple[dict[str, list[object]], int, str, str]:
        logger = BoundedLogger(
            max_entries=int(self.config.logging["max_entries"]),
            max_payload_chars=int(self.config.logging["max_payload_chars"]),
        )
        result: dict[str, list[object]] = {}
        local_states = self._build_local_states(state)
        persisted_state = self._load_persisted_state(getattr(state, "traderData", ""))

        for product, product_cfg in self.config.products.items():
            local_state = local_states.get(product)
            if local_state is None:
                continue
            strategy = self._build_strategy(product_cfg)
            local_orders = strategy.generate_orders(local_state)
            result[product] = orders_to_datamodel(local_orders, order_cls)
            logger.log(
                "product_orders",
                product=product,
                order_count=len(local_orders),
                position=local_state.position,
            )

        if self.config.baskets:
            basket_state = persisted_state.setdefault("baskets", {})
            for basket, basket_cfg in self.config.baskets.items():
                tracker = BasketSpreadTracker(
                    weights={product: int(weight) for product, weight in basket_cfg["weights"].items()},
                    premium_window=int(basket_cfg["premium_window"]),
                    volatility_window=int(basket_cfg["volatility_window"]),
                )
                tracker.restore_history(basket_state.get(basket, []))
                strategy = BasketArbitrageStrategy(
                    basket=basket,
                    weights={product: int(weight) for product, weight in basket_cfg["weights"].items()},
                    tracker=tracker,
                    entry_zscore=float(basket_cfg["entry_zscore"]),
                    exit_zscore=float(basket_cfg["exit_zscore"]),
                    max_units=int(basket_cfg["max_units"]),
                    hedge_components=bool(basket_cfg["hedge_components"]),
                    min_history=(
                        int(basket_cfg["min_history"])
                        if basket_cfg.get("min_history") is not None
                        else None
                    ),
                )
                execution = strategy.generate_orders(local_states)
                basket_state[basket] = tracker.snapshot_history()

                if execution.signal is not None:
                    logger.log(
                        "basket_signal",
                        basket=basket,
                        spread=round(execution.signal.spread, 4),
                        zscore=round(execution.signal.zscore, 4),
                        premium_mean=round(execution.signal.premium_mean, 4),
                    )

                for product, local_orders in execution.orders.items():
                    result.setdefault(product, [])
                    result[product].extend(orders_to_datamodel(local_orders, order_cls))

        return result, 0, self._dump_persisted_state(persisted_state), logger.serialize()

    def _build_local_states(self, state: object) -> dict[str, Any]:
        local_states: dict[str, Any] = {}
        all_limits = {
            **{
                product: int(product_cfg["position_limit"])
                for product, product_cfg in self.config.products.items()
            },
            **{
                basket: int(basket_cfg["position_limit"])
                for basket, basket_cfg in self.config.baskets.items()
            },
        }
        for basket_cfg in self.config.baskets.values():
            for product, limit in basket_cfg.get("component_limits", {}).items():
                all_limits[product] = int(limit)

        for product, position_limit in all_limits.items():
            if product not in state.order_depths:
                continue
            local_states[product] = product_state_from_order_depth(
                product=product,
                order_depth=state.order_depths[product],
                position=state.position.get(product, 0),
                position_limit=position_limit,
            )
        return local_states

    def _load_persisted_state(self, raw: str) -> dict[str, Any]:
        if not raw:
            return {}
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            return {}
        return payload if isinstance(payload, dict) else {}

    def _dump_persisted_state(self, payload: dict[str, Any]) -> str:
        return json.dumps(payload, separators=(",", ":"))

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


def build_runtime(config_override: dict[str, Any] | None = None) -> StrategyRuntime:
    config = load_runtime_config()
    if config_override:
        from tcosw.config import merge_dicts

        merge_dicts(config.raw, config_override)
    return StrategyRuntime(config=config)


__all__ = [
    "BasketSpreadTracker",
    "StrategyRuntime",
    "build_runtime",
]
