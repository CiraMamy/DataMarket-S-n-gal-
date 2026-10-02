from backend.ingestion import IngestionPipeline, SourceConnector


def test_ingestion_pipeline_validates_and_normalizes_row_data():
    connector = SourceConnector(
        name="ansd-demo",
        source_url="https://example.org/demo.csv",
        required_columns=["region", "population", "year"],
    )
    pipeline = IngestionPipeline(connector=connector)

    rows = [
        {"region": "Dakar", "population": 1200000, "year": 2023},
        {"region": "Thiès", "population": 850000, "year": 2023},
    ]

    result = pipeline.process(rows)

    assert result["valid_rows"] == 2
    assert result["invalid_rows"] == 0
    assert result["columns_ok"] is True
    assert result["source_name"] == "ansd-demo"


def test_ingestion_pipeline_rejects_missing_required_columns():
    connector = SourceConnector(
        name="ansd-demo",
        source_url="https://example.org/demo.csv",
        required_columns=["region", "population", "year"],
    )
    pipeline = IngestionPipeline(connector=connector)

    rows = [
        {"region": "Dakar", "population": 1200000},
    ]

    result = pipeline.process(rows)

    assert result["valid_rows"] == 0
    assert result["invalid_rows"] == 1
    assert result["columns_ok"] is False
