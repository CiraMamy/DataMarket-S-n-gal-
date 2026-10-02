from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable


@dataclass
class QualityIssue:
    code: str
    severity: str
    message: str


@dataclass
class QualityReport:
    issues: list[QualityIssue] = field(default_factory=list)
    total_rows: int = 0

    @property
    def warning_count(self) -> int:
        return sum(1 for issue in self.issues if issue.severity == "warning")

    @property
    def error_count(self) -> int:
        return sum(1 for issue in self.issues if issue.severity == "error")

    @property
    def is_blocking(self) -> bool:
        if self.total_rows <= 0:
            return False
        return self.error_count > self.warning_count

    @property
    def score(self) -> float:
        if not self.issues:
            return 1.0
        penalty = min(1.0, (self.error_count + self.warning_count) / max(1, self.total_rows))
        return max(0.0, 1.0 - penalty)


class QualityRuleEngine:
    def evaluate(self, rows: Iterable[dict[str, Any]], required_fields: list[str]) -> QualityReport:
        issues: list[QualityIssue] = []
        rows = list(rows)
        total_rows = len(rows)

        for idx, row in enumerate(rows):
            for field in required_fields:
                if field not in row or row.get(field) in (None, ""):
                    issues.append(
                        QualityIssue(
                            code="missing_required_field",
                            severity="warning",
                            message=f"Row {idx + 1} missing required field: {field}",
                        )
                    )
            for field in required_fields:
                value = row.get(field)
                if value is None:
                    issues.append(
                        QualityIssue(
                            code="null_value",
                            severity="warning",
                            message=f"Row {idx + 1} has null value in {field}",
                        )
                    )
                elif isinstance(value, (int, float)) and value < 0:
                    issues.append(
                        QualityIssue(
                            code="negative_value",
                            severity="error",
                            message=f"Row {idx + 1} has negative value in {field}",
                        )
                    )

        return QualityReport(issues=issues, total_rows=total_rows)


__all__ = ["QualityIssue", "QualityReport", "QualityRuleEngine"]
