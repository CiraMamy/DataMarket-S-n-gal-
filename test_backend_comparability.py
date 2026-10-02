from backend.comparability import ComparisonStatus, ComparabilityEngine, ConflictRecord, ConflictEngine


def test_comparability_engine_detects_comparable_values():
    engine = ComparabilityEngine()

    source_a = {
        "indicator": "population",
        "unit": "people",
        "territory": "Dakar",
        "period": "2023",
        "value": 1200000,
        "territory_version": "v1",
    }
    source_b = {
        "indicator": "population",
        "unit": "people",
        "territory": "Dakar",
        "period": "2023",
        "value": 1215000,
        "territory_version": "v1",
    }

    result = engine.compare(source_a, source_b)

    assert result.status == ComparisonStatus.COMPARABLE
    assert result.reason == "same indicator, unit, territory and period"


def test_comparability_engine_rejects_different_units_or_territories():
    engine = ComparabilityEngine()

    source_a = {
        "indicator": "population",
        "unit": "people",
        "territory": "Dakar",
        "period": "2023",
        "value": 1200000,
        "territory_version": "v1",
    }
    source_b = {
        "indicator": "population",
        "unit": "fcfa",
        "territory": "Dakar",
        "period": "2023",
        "value": 1200000,
        "territory_version": "v1",
    }

    result = engine.compare(source_a, source_b)
    assert result.status == ComparisonStatus.NOT_COMPARABLE


def test_conflict_engine_detects_significant_divergence():
    engine = ConflictEngine()

    records = [
        {
            "indicator": "population",
            "unit": "people",
            "territory": "Dakar",
            "period": "2023",
            "value": 1000000,
            "source": "A",
            "territory_version": "v1",
        },
        {
            "indicator": "population",
            "unit": "people",
            "territory": "Dakar",
            "period": "2023",
            "value": 1400000,
            "source": "B",
            "territory_version": "v1",
        },
    ]

    conflict = engine.detect(records)

    assert isinstance(conflict, ConflictRecord)
    assert conflict.status == "detected"
    assert conflict.relative_gap > 0.2
    assert conflict.source_a == "A"
    assert conflict.source_b == "B"
