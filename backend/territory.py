from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class TerritoryMatch:
    canonical_name: str
    territory_type: str
    confidence: float
    aliases: list[str]


class TerritoryResolver:
    _ALIASES = {
        "mbour": {"canonical_name": "Thiès", "territory_type": "region", "confidence": 0.96, "aliases": ["mbour", "Mbour"]},
        "dakar": {"canonical_name": "Dakar", "territory_type": "region", "confidence": 0.99, "aliases": ["dakar"]},
        "saint-louis": {"canonical_name": "Saint-Louis", "territory_type": "region", "confidence": 0.97, "aliases": ["saint-louis", "saint louis"]},
        "thiès": {"canonical_name": "Thiès", "territory_type": "region", "confidence": 0.99, "aliases": ["thiès", "thies"]},
        "kaolack": {"canonical_name": "Kaolack", "territory_type": "region", "confidence": 0.98, "aliases": ["kaolack"]},
    }

    def resolve(self, locality: str) -> dict[str, Any] | None:
        if locality is None:
            return None
        key = locality.strip().lower()
        if not key:
            return None
        match = self._ALIASES.get(key)
        if match is None:
            for alias_key, value in self._ALIASES.items():
                if alias_key in key or key in alias_key:
                    return {
                        "canonical_name": value["canonical_name"],
                        "territory_type": value["territory_type"],
                        "confidence": value["confidence"],
                        "aliases": value["aliases"],
                    }
            return None
        return {
            "canonical_name": match["canonical_name"],
            "territory_type": match["territory_type"],
            "confidence": match["confidence"],
            "aliases": match["aliases"],
        }


__all__ = ["TerritoryMatch", "TerritoryResolver"]
