from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(slots=True)
class ProviderProductAdjustment:
    provider: str
    product_name: str
    production_cost_multiplier: float
    shipping_complexity_multiplier: float
    quality_multiplier: float


class BasePODProviderAdapter(ABC):
    """Provider adapter to support multiple POD backends without changing business logic."""

    name: str = "base_provider"

    @abstractmethod
    def get_adjustment(self, product_name: str) -> ProviderProductAdjustment:
        raise NotImplementedError


class GenericPODProviderAdapter(BasePODProviderAdapter):
    name = "generic_pod"

    def get_adjustment(self, product_name: str) -> ProviderProductAdjustment:
        lower = product_name.lower()
        production = 1.0
        shipping = 1.0
        quality = 1.0

        if any(token in lower for token in ["canvas", "framed", "blanket"]):
            production = 1.08
            shipping = 1.12
        if any(token in lower for token in ["mug", "ornament", "clock"]):
            shipping = 1.10
        if any(token in lower for token in ["premium", "framed"]):
            quality = 1.06

        return ProviderProductAdjustment(
            provider=self.name,
            product_name=product_name,
            production_cost_multiplier=production,
            shipping_complexity_multiplier=shipping,
            quality_multiplier=quality,
        )
