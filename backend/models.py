from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    slug: Mapped[str] = mapped_column(String(120), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    provider: Mapped[str] = mapped_column(String(200), nullable=False)
    source_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    license: Mapped[str] = mapped_column(String(100), default="unknown")
    access_level: Mapped[str] = mapped_column(String(50), default="public")
    status: Mapped[str] = mapped_column(String(50), default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    datasets: Mapped[list["Dataset"]] = relationship(back_populates="source")
    provenance_events: Mapped[list["ProvenanceEvent"]] = relationship(back_populates="source")


class Dataset(Base):
    __tablename__ = "datasets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    slug: Mapped[str] = mapped_column(String(120), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"), nullable=False, index=True)
    data_domain: Mapped[str] = mapped_column(String(120), default="general")
    status: Mapped[str] = mapped_column(String(50), default="active")
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    source: Mapped[Source] = relationship(back_populates="datasets")
    versions: Mapped[list["DatasetVersion"]] = relationship(back_populates="dataset")
    provenance_events: Mapped[list["ProvenanceEvent"]] = relationship(back_populates="dataset")


class DatasetVersion(Base):
    __tablename__ = "dataset_versions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    dataset_id: Mapped[int] = mapped_column(ForeignKey("datasets.id"), nullable=False, index=True)
    version_label: Mapped[str] = mapped_column(String(50), nullable=False)
    file_hash: Mapped[str | None] = mapped_column(String(128), nullable=True)
    storage_uri: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="draft")
    published_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    dataset: Mapped[Dataset] = relationship(back_populates="versions")
    observations: Mapped[list["Observation"]] = relationship(back_populates="dataset_version")
    provenance_events: Mapped[list["ProvenanceEvent"]] = relationship(back_populates="dataset_version")


class Observation(Base):
    __tablename__ = "observations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    dataset_version_id: Mapped[int] = mapped_column(ForeignKey("dataset_versions.id"), nullable=False, index=True)
    indicator_name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    territory_name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    period: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    value_numeric: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str] = mapped_column(String(50), default="unit")
    quality_score: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    dataset_version: Mapped[DatasetVersion] = relationship(back_populates="observations")


class Calculation(Base):
    __tablename__ = "calculations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False, unique=True, index=True)
    formula: Mapped[str] = mapped_column(String(500), nullable=False)
    result: Mapped[float] = mapped_column(Float, nullable=False)
    evidence_distance: Mapped[str] = mapped_column(String(20), default="D2")
    inputs_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    assumptions_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


class ProvenanceEvent(Base):
    __tablename__ = "provenance_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    source_id: Mapped[int | None] = mapped_column(ForeignKey("sources.id"), nullable=True, index=True)
    dataset_id: Mapped[int | None] = mapped_column(ForeignKey("datasets.id"), nullable=True, index=True)
    dataset_version_id: Mapped[int | None] = mapped_column(ForeignKey("dataset_versions.id"), nullable=True, index=True)
    event_type: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    event_summary: Mapped[str] = mapped_column(String(500), default="")
    checksum: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    source: Mapped[Source | None] = relationship(back_populates="provenance_events")
    dataset: Mapped[Dataset | None] = relationship(back_populates="provenance_events")
    dataset_version: Mapped[DatasetVersion | None] = relationship(back_populates="provenance_events")


__all__ = [
    "Calculation",
    "Dataset",
    "DatasetVersion",
    "Observation",
    "ProvenanceEvent",
    "Source",
]
