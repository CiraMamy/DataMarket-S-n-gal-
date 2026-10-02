from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from math import isclose
from typing import Any


class ComparisonStatus(str, Enum):
    COMPARABLE = "comparable"
    CONDITIONALLY_COMPARABLE = "conditionally_comparable"
    NOT_COMPARABLE = "not_comparable"
    INSUFFICIENT_METADATA = "insufficient_metadata"


@dataclass
class ComparisonResult:
    status: ComparisonStatus
    reason: str = ""
    difference: float | None = None


@dataclass
class ConflictRecord:
    status: str
    source_a: str
    source_b: str
    relative_gap: float
    difference: float
    indicator: str
    territory: str
    period: str


class ComparabilityEngine:
    def compare(self, left: dict[str, Any], right: dict[str, Any]) -> ComparisonResult:
        required = [
            "indicator",
            "unit",
            "territory",
            "period",
            "value",
        ]
        for field in required:
            if field not in left or field not in right:
                return ComparisonResult(
                    status=ComparisonStatus.INSUFFICIENT_METADATA,
                    reason=f"missing required field: {field}",
                )

        if left["indicator"] != right["indicator"]:
            return ComparisonResult(
                status=ComparisonStatus.NOT_COMPARABLE,
                reason="different indicators",
            )

        if left["unit"] != right["unit"]:
            return ComparisonResult(
                status=ComparisonStatus.NOT_COMPARABLE,
                reason="different units",
            )

        if left["territory"] != right["territory"]:
            return ComparisonResult(
                status=ComparisonStatus.NOT_COMPARABLE,
                reason="different territories",
            )

        if left["period"] != right["period"]:
            return ComparisonResult(
                status=ComparisonStatus.CONDITIONALLY_COMPARABLE,
                reason="same indicator but different period",
            )

        if left.get("territory_version") and right.get("territory_version"):
            if left["territory_version"] != right["territory_version"]:
                return ComparisonResult(
                    status=ComparisonStatus.CONDITIONALLY_COMPARABLE,
                    reason="same geographies but different territory version",
                )

        if isclose(float(left["value"]), float(right["value"]), rel_tol=0.0, abs_tol=0.0):
            return ComparisonResult(
                status=ComparisonStatus.COMPARABLE,
                reason="same indicator, unit, territory and period",
                difference=0.0,
            )

        return ComparisonResult(
            status=ComparisonStatus.COMPARABLE,
            reason="same indicator, unit, territory and period",
            difference=abs(float(left["value"]) - float(right["value"])),
        )


class ConflictEngine:
    def detect(self, records: list[dict[str, Any]], threshold: float = 0.2) -> ConflictRecord | None:
        if len(records) < 2:
            return None

        base = records[0]
        for candidate in records[1:]:
            comparison = ComparabilityEngine().compare(base, candidate)
            if comparison.status in (ComparisonStatus.NOT_COMPARABLE, ComparisonStatus.INSUFFICIENT_METADATA):
                continue

            base_value = float(base["value"])
            candidate_value = float(candidate["value"])
            max_value = max(base_value, candidate_value)
            relative_gap = abs(base_value - candidate_value) / max_value if max_value else 0.0
            if relative_gap >= threshold:
                return ConflictRecord(
                    status="detected",
                    source_a=str(base.get("source", "source_a")),
                    source_b=str(candidate.get("source", "source_b")),
                    relative_gap=relative_gap,
                    difference=abs(base_value - candidate_value),
                    indicator=str(base.get("indicator", "unknown")),
                    territory=str(base.get("territory", "unknown")),
                    period=str(base.get("period", "unknown")),
                )

        return None


__all__ = [
    "ComparisonResult",
    "ComparisonStatus",
    "ComparabilityEngine",
    "ConflictEngine",
    "ConflictRecord",
]
