from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class SourceConnector:
    name: str
    source_url: str
    required_columns: list[str] = field(default_factory=list)
    schema_version: str = "v1"


class IngestionPipeline:
    def __init__(self, connector: SourceConnector):
        self.connector = connector

    def process(self, rows: list[dict[str, Any]]) -> dict[str, Any]:
        if not rows:
            return {
                "source_name": self.connector.name,
                "columns_ok": False,
                "valid_rows": 0,
                "invalid_rows": 0,
                "issues": ["empty dataset"],
            }

        required = set(self.connector.required_columns)
        valid_rows = 0
        invalid_rows = 0
        columns_ok = required.issubset(set().union(*(row.keys() for row in rows)))

        normalized_rows: list[dict[str, Any]] = []
        for row in rows:
            if not required.issubset(row.keys()):
                invalid_rows += 1
                continue
            normalized = {
                key: value.strip() if isinstance(value, str) else value for key, value in row.items()
            }
            normalized_rows.append(normalized)
            valid_rows += 1

        return {
            "source_name": self.connector.name,
            "schema_version": self.connector.schema_version,
            "columns_ok": columns_ok,
            "valid_rows": valid_rows,
            "invalid_rows": invalid_rows,
            "normalized_rows": normalized_rows,
            "issues": [] if columns_ok else ["missing required columns"],
        }


__all__ = ["IngestionPipeline", "SourceConnector"]
