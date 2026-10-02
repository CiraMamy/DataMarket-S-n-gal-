from backend.quality import QualityIssue, QualityReport, QualityRuleEngine


def test_quality_rule_engine_flags_missing_and_negative_values():
    rows = [
        {"region": "Dakar", "value": 1200},
        {"region": "", "value": -10},
        {"region": "Thiès", "value": None},
    ]

    report = QualityRuleEngine().evaluate(rows, required_fields=["region", "value"])

    assert report.is_blocking is False
    assert any(issue.code == "missing_required_field" for issue in report.issues)
    assert any(issue.code == "negative_value" for issue in report.issues)
    assert any(issue.code == "null_value" for issue in report.issues)


def test_quality_report_summary_exposes_score_and_counts():
    report = QualityReport(
        issues=[
            QualityIssue(code="missing_required_field", severity="warning", message="missing region"),
            QualityIssue(code="negative_value", severity="error", message="negative total"),
        ],
        total_rows=10,
    )

    assert report.score == 0.8
    assert report.error_count == 1
    assert report.warning_count == 1
