import uuid
from datetime import datetime

from sqlalchemy import select

from backend.database import Base, create_db_engine, get_session_factory
from backend.models import Calculation, Dataset, DatasetVersion, Observation, ProvenanceEvent, Source
from backend.registry import DatasetRegistry


def test_backend_tables_can_be_created_and_queryed(tmp_path):
    database_url = f"sqlite:///{tmp_path / 'datamarket.db'}"
    engine = create_db_engine(database_url)
    Base.metadata.create_all(bind=engine)

    session_factory = get_session_factory(engine)
    with session_factory() as session:
        source = Source(
            slug="ansd",
            name="ANSD",
            provider="ANSD",
            source_url="https://example.org",
            license="open",
            access_level="public",
            status="active",
        )
        session.add(source)
        session.flush()

        dataset = Dataset(
            slug="population-regionale",
            name="Population régionale",
            source_id=source.id,
            data_domain="demography",
            status="active",
            description="Population par région",
        )
        session.add(dataset)
        session.flush()

        version = DatasetVersion(
            dataset_id=dataset.id,
            version_label="v1",
            file_hash="abc123",
            storage_uri="s3://bucket/population-regionale.csv",
            status="published",
            published_at=datetime.utcnow(),
        )
        session.add(version)
        session.flush()

        observation = Observation(
            dataset_version_id=version.id,
            indicator_name="population",
            territory_name="Dakar",
            period="2023",
            value_numeric=1200000,
            unit="people",
            quality_score=0.98,
        )
        session.add(observation)

        calculation = Calculation(
            name="tam_local",
            formula="population * spend_per_head",
            result=123456789,
            evidence_distance="D2",
            inputs_json={"population": 1200000, "spend_per_head": 102.88},
            assumptions_json={"source": "reference dataset"},
        )
        session.add(calculation)
        session.commit()

        source_row = session.scalar(select(Source).where(Source.slug == "ansd"))
        dataset_row = session.scalar(select(Dataset).where(Dataset.slug == "population-regionale"))
        observation_row = session.scalar(select(Observation).where(Observation.period == "2023"))
        calculation_row = session.scalar(select(Calculation).where(Calculation.name == "tam_local"))

    assert source_row is not None
    assert dataset_row is not None
    assert dataset_row.source_id == source_row.id
    assert observation_row is not None
    assert observation_row.value_numeric == 1200000
    assert calculation_row is not None
    assert calculation_row.result == 123456789


def test_backend_api_health_and_dataset_list_responds():
    from starlette.testclient import TestClient

    from backend.api import app

    client = TestClient(app)

    health = client.get("/health")
    dataset_list = client.get("/api/v1/datasets")
    source_list = client.get("/api/v1/sources")

    assert health.status_code == 200
    assert health.json()["status"] == "ok"
    assert dataset_list.status_code == 200
    assert isinstance(dataset_list.json(), list)
    assert source_list.status_code == 200
    assert isinstance(source_list.json(), list)


def test_dataset_registry_tracks_version_and_provenance(tmp_path):
    database_url = f"sqlite:///{tmp_path / 'datamarket_provenance.db'}"
    engine = create_db_engine(database_url)
    Base.metadata.create_all(bind=engine)
    session_factory = get_session_factory(engine)

    with session_factory() as session:
        registry = DatasetRegistry(session)
        source = registry.upsert_source(
            slug="ansd",
            name="ANSD",
            provider="Agence Nationale de la Statistique",
            source_url="https://example.org/demography",
            license="open",
        )
        dataset = registry.upsert_dataset(
            slug="population-regionale",
            name="Population régionale",
            source_slug="ansd",
            data_domain="demography",
            description="Population par région",
        )
        version = registry.register_version(
            dataset_slug="population-regionale",
            version_label="v1",
            file_hash="hash-123",
            storage_uri="s3://bucket/population-regionale.csv",
            status="published",
        )

        provenance_event = ProvenanceEvent(
            source_id=source.id,
            dataset_id=dataset.id,
            dataset_version_id=version.id,
            event_type="ingested",
            event_summary="Dataset published",
            checksum="hash-123",
        )
        session.add(provenance_event)
        session.commit()

        stored_event = session.scalar(
            select(ProvenanceEvent).where(ProvenanceEvent.dataset_version_id == version.id)
        )

    assert stored_event is not None
    assert stored_event.event_type == "ingested"
    assert stored_event.checksum == "hash-123"
    assert version.dataset_id == dataset.id


def test_backend_dataset_detail_contains_source_and_versions():
    from starlette.testclient import TestClient

    from backend.api import SessionLocal, app
    from backend.models import Dataset, DatasetVersion, Source

    source_slug = f"demo-source-{uuid.uuid4().hex[:8]}"
    dataset_slug = f"demo-dataset-{uuid.uuid4().hex[:8]}"

    with SessionLocal() as session:
        source = Source(
            slug=source_slug,
            name="Demo Source",
            provider="Demo Provider",
            source_url="https://example.org/source",
            license="open",
            access_level="public",
            status="active",
        )
        session.add(source)
        session.flush()

        dataset = Dataset(
            slug=dataset_slug,
            name="Demo Dataset",
            source_id=source.id,
            data_domain="demography",
            status="active",
            description="Dataset for API contract checks",
        )
        session.add(dataset)
        session.flush()

        version = DatasetVersion(
            dataset_id=dataset.id,
            version_label="v2026.10",
            file_hash="abc123",
            storage_uri="s3://demo/demo-dataset.csv",
            status="published",
        )
        session.add(version)
        session.commit()

    client = TestClient(app)
    response = client.get(f"/api/v1/datasets/{dataset.id}")

    assert response.status_code == 200
    payload = response.json()
    assert payload["slug"] == dataset_slug
    assert payload["source"]["slug"] == source_slug
    assert payload["versions"][0]["version_label"] == "v2026.10"


def test_backend_analysis_endpoints_expose_market_quality_and_comparability():
    from starlette.testclient import TestClient

    from backend.api import app

    client = TestClient(app)

    market_response = client.post(
        "/api/v1/market/evaluate",
        json={
            "market_name": "superette",
            "region": "Dakar",
            "population": 100000,
            "spend_per_head": 500000,
            "market_share": 0.15,
            "assumptions": {"channel": "urban"},
        },
    )
    assert market_response.status_code == 200
    market_payload = market_response.json()
    assert market_payload["tam"] == 50000000000
    assert market_payload["som"] == 1125000000

    quality_response = client.post(
        "/api/v1/quality/evaluate",
        json={
            "rows": [
                {"region": "Dakar", "value": 1200},
                {"region": "", "value": -10},
                {"region": "Thiès", "value": None},
            ],
            "required_fields": ["region", "value"],
        },
    )
    assert quality_response.status_code == 200
    quality_payload = quality_response.json()
    assert quality_payload["total_rows"] == 3
    assert any(issue["code"] == "negative_value" for issue in quality_payload["issues"])

    comparison_response = client.post(
        "/api/v1/comparability/compare",
        json={
            "left": {
                "indicator": "population",
                "unit": "people",
                "territory": "Dakar",
                "period": "2023",
                "value": 1200000,
                "territory_version": "v1",
            },
            "right": {
                "indicator": "population",
                "unit": "people",
                "territory": "Dakar",
                "period": "2023",
                "value": 1215000,
                "territory_version": "v1",
            },
        },
    )
    assert comparison_response.status_code == 200
    comparison_payload = comparison_response.json()
    assert comparison_payload["status"] == "comparable"


def test_backend_registry_endpoints_create_sources_datasets_and_versions():
    from starlette.testclient import TestClient

    from backend.api import app

    client = TestClient(app)
    source_slug = f"source-{uuid.uuid4().hex[:8]}"
    dataset_slug = f"dataset-{uuid.uuid4().hex[:8]}"

    source_create = client.post(
        "/api/v1/sources",
        json={
            "slug": source_slug,
            "name": "API Source",
            "provider": "Test Provider",
            "source_url": "https://example.org/source",
            "license": "open",
            "access_level": "public",
            "status": "active",
        },
    )
    assert source_create.status_code == 201
    assert source_create.json()["slug"] == source_slug

    dataset_create = client.post(
        "/api/v1/datasets",
        json={
            "slug": dataset_slug,
            "name": "API Dataset",
            "source_slug": source_slug,
            "data_domain": "demography",
            "description": "Created via API",
            "status": "active",
        },
    )
    assert dataset_create.status_code == 201
    dataset_payload = dataset_create.json()
    assert dataset_payload["slug"] == dataset_slug
    assert dataset_payload["source"]["slug"] == source_slug

    version_create = client.post(
        f"/api/v1/datasets/{dataset_payload['id']}/versions",
        json={
            "version_label": "v1",
            "file_hash": "hash-456",
            "storage_uri": "s3://demo/api-dataset.csv",
            "status": "published",
        },
    )
    assert version_create.status_code == 201
    version_payload = version_create.json()
    assert version_payload["version_label"] == "v1"
    assert version_payload["dataset_id"] == dataset_payload["id"]
