from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class MarketEvaluation:
    market_name: str
    region: str
    population: float
    spend_per_head: float
    market_share: float
    tam: float
    sam: float
    som: float
    evidence_distance: str = "D2"
    assumptions: dict[str, Any] | None = None
    formula: str | None = None


class MarketEngine:
    def evaluate(
        self,
        market_name: str,
        region: str,
        population: float,
        spend_per_head: float,
        market_share: float,
        assumptions: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        tam = float(population) * float(spend_per_head)
        sam = tam * 0.15
        som = sam * float(market_share)

        return {
            "market_name": market_name,
            "region": region,
            "population": float(population),
            "spend_per_head": float(spend_per_head),
            "market_share": float(market_share),
            "tam": int(tam),
            "sam": int(sam),
            "som": int(som),
            "evidence_distance": "D2",
            "assumptions": assumptions or {},
            "formula": "TAM = population * spend_per_head; SAM = TAM * 0.15; SOM = SAM * market_share",
        }


__all__ = ["MarketEvaluation", "MarketEngine"]
