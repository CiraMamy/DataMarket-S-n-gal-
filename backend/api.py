import os
from typing import Any

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route

from .comparability import ComparabilityEngine, ComparisonStatus
from .database import create_db_engine, get_session_factory, init_database
from .market_engine import MarketEngine
from .models import Dataset, DatasetVersion, Source
from .quality import QualityRuleEngine
from .registry import DatasetRegistry


class DatasetSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    name: str
    data_domain: str
    status: str
    description: str | None = None


class SourceSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    name: str
    provider: str
    status: str
    license: str


class DatasetVersionSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    dataset_id: int
    version_label: str
    file_hash: str | None = None
    storage_uri: str | None = None
    status: str
    published_at: str | None = None


class DatasetDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    name: str
    data_domain: str
    status: str
    description: str | None = None
    source: SourceSummary | None = None
    versions: list[DatasetVersionSummary] = Field(default_factory=list)


engine = create_db_engine(os.getenv("DATAMARKET_DATABASE_URL", "sqlite:///datamarket.db"))
SessionLocal = get_session_factory(engine)
init_database(engine)


async def health_check(request) -> JSONResponse:
    return JSONResponse({
        "status": "ok",
        "database": os.getenv("DATAMARKET_DATABASE_URL", "sqlite:///datamarket.db"),
    })


async def list_datasets(request) -> JSONResponse:
    with SessionLocal() as session:
        rows = session.scalars(select(Dataset).order_by(Dataset.created_at.desc())).all()
        payload = [DatasetSummary.model_validate(row).model_dump(mode="json") for row in rows]
    return JSONResponse(payload)


async def list_sources(request) -> JSONResponse:
    with SessionLocal() as session:
        rows = session.scalars(select(Source).order_by(Source.created_at.desc())).all()
        payload = [SourceSummary.model_validate(row).model_dump(mode="json") for row in rows]
    return JSONResponse(payload)


async def create_source(request) -> JSONResponse:
    payload = await request.json()
    with SessionLocal() as session:
        registry = DatasetRegistry(session)
        source = registry.upsert_source(
            slug=payload.get("slug"),
            name=payload.get("name", payload.get("slug", "unnamed")),
            provider=payload.get("provider", "unknown"),
            source_url=payload.get("source_url"),
            license=payload.get("license", "unknown"),
            access_level=payload.get("access_level", "public"),
            status=payload.get("status", "active"),
        )
        session.commit()
        response_payload = SourceSummary.model_validate(source).model_dump(mode="json")
    return JSONResponse(response_payload, status_code=201)


async def create_dataset(request) -> JSONResponse:
    payload = await request.json()
    with SessionLocal() as session:
        registry = DatasetRegistry(session)
        dataset = registry.upsert_dataset(
            slug=payload.get("slug"),
            name=payload.get("name", payload.get("slug", "unnamed")),
            source_slug=payload.get("source_slug"),
            data_domain=payload.get("data_domain", "general"),
            status=payload.get("status", "active"),
            description=payload.get("description"),
        )
        session.commit()
        session.refresh(dataset)
        versions = [DatasetVersionSummary.model_validate(version).model_dump(mode="json") for version in dataset.versions]
        response_payload = DatasetDetail(
            id=dataset.id,
            slug=dataset.slug,
            name=dataset.name,
            data_domain=dataset.data_domain,
            status=dataset.status,
            description=dataset.description,
            source=SourceSummary.model_validate(dataset.source).model_dump(mode="json") if dataset.source else None,
            versions=versions,
        ).model_dump(mode="json")
    return JSONResponse(response_payload, status_code=201)


async def get_dataset(request) -> JSONResponse:
    dataset_id = int(request.path_params["dataset_id"])
    with SessionLocal() as session:
        dataset = session.get(Dataset, dataset_id)
        if dataset is None:
            return JSONResponse({"detail": "dataset not found"}, status_code=404)

        versions = [DatasetVersionSummary.model_validate(version).model_dump(mode="json") for version in dataset.versions]
        payload = DatasetDetail(
            id=dataset.id,
            slug=dataset.slug,
            name=dataset.name,
            data_domain=dataset.data_domain,
            status=dataset.status,
            description=dataset.description,
            source=SourceSummary.model_validate(dataset.source).model_dump(mode="json") if dataset.source else None,
            versions=versions,
        ).model_dump(mode="json")
    return JSONResponse(payload)


async def list_dataset_versions(request) -> JSONResponse:
    dataset_id = int(request.path_params["dataset_id"])
    with SessionLocal() as session:
        dataset = session.get(Dataset, dataset_id)
        if dataset is None:
            return JSONResponse({"detail": "dataset not found"}, status_code=404)
        payload = [
            DatasetVersionSummary.model_validate(version).model_dump(mode="json")
            for version in dataset.versions
        ]
    return JSONResponse(payload)


async def create_dataset_version(request) -> JSONResponse:
    dataset_id = int(request.path_params["dataset_id"])
    payload = await request.json()
    with SessionLocal() as session:
        dataset = session.get(Dataset, dataset_id)
        if dataset is None:
            return JSONResponse({"detail": "dataset not found"}, status_code=404)

        version = DatasetVersion(
            dataset_id=dataset.id,
            version_label=payload.get("version_label", "v1"),
            file_hash=payload.get("file_hash"),
            storage_uri=payload.get("storage_uri"),
            status=payload.get("status", "draft"),
            published_at=None,
        )
        session.add(version)
        session.commit()
        response_payload = DatasetVersionSummary.model_validate(version).model_dump(mode="json")
    return JSONResponse(response_payload, status_code=201)


async def evaluate_market(request) -> JSONResponse:
    payload = await request.json()
    engine = MarketEngine()
    result = engine.evaluate(
        market_name=payload.get("market_name", "market"),
        region=payload.get("region", "unknown"),
        population=float(payload.get("population", 0)),
        spend_per_head=float(payload.get("spend_per_head", 0)),
        market_share=float(payload.get("market_share", 0)),
        assumptions=payload.get("assumptions") or {},
    )
    return JSONResponse(result)


async def evaluate_quality(request) -> JSONResponse:
    payload = await request.json()
    rows = payload.get("rows", [])
    required_fields = payload.get("required_fields", [])
    report = QualityRuleEngine().evaluate(rows, required_fields)
    return JSONResponse({
        "total_rows": report.total_rows,
        "issues": [
            {"code": issue.code, "severity": issue.severity, "message": issue.message}
            for issue in report.issues
        ],
        "warning_count": report.warning_count,
        "error_count": report.error_count,
        "score": report.score,
        "is_blocking": report.is_blocking,
    })


async def compare_data(request) -> JSONResponse:
    payload = await request.json()
    result = ComparabilityEngine().compare(payload.get("left", {}), payload.get("right", {}))
    response = {
        "status": result.status.value,
        "reason": result.reason,
    }
    if result.difference is not None:
        response["difference"] = result.difference
    return JSONResponse(response)


async def legacy_health(request) -> JSONResponse:
    return JSONResponse({"status": "ok"})


app = Starlette(
    routes=[
        Route("/health", health_check),
        Route("/api/v1/datasets", list_datasets),
        Route("/api/v1/datasets", create_dataset, methods=["POST"]),
        Route("/api/v1/datasets/{dataset_id:int}", get_dataset),
        Route("/api/v1/datasets/{dataset_id:int}/versions", list_dataset_versions),
        Route("/api/v1/datasets/{dataset_id:int}/versions", create_dataset_version, methods=["POST"]),
        Route("/api/v1/sources", list_sources),
        Route("/api/v1/sources", create_source, methods=["POST"]),
        Route("/api/v1/market/evaluate", evaluate_market, methods=["POST"]),
        Route("/api/v1/quality/evaluate", evaluate_quality, methods=["POST"]),
        Route("/api/v1/comparability/compare", compare_data, methods=["POST"]),
        Route("/api/v1/health", legacy_health),
    ]
)
