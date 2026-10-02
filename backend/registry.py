from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import Dataset, DatasetVersion, Source


class DatasetRegistry:
    def __init__(self, session: Session):
        self.session = session

    def upsert_source(
        self,
        slug: str,
        name: str,
        provider: str,
        source_url: str | None = None,
        license: str = "unknown",
        access_level: str = "public",
        status: str = "active",
    ) -> Source:
        source = self.session.scalar(select(Source).where(Source.slug == slug))
        if source is None:
            source = Source(
                slug=slug,
                name=name,
                provider=provider,
                source_url=source_url,
                license=license,
                access_level=access_level,
                status=status,
            )
            self.session.add(source)
            self.session.flush()
        else:
            source.name = name
            source.provider = provider
            source.source_url = source_url
            source.license = license
            source.access_level = access_level
            source.status = status
        self.session.flush()
        return source

    def upsert_dataset(
        self,
        slug: str,
        name: str,
        source_slug: str,
        data_domain: str = "general",
        status: str = "active",
        description: str | None = None,
    ) -> Dataset:
        source = self.session.scalar(select(Source).where(Source.slug == source_slug))
        if source is None:
            source = self.upsert_source(source_slug, source_slug, "unknown")

        dataset = self.session.scalar(select(Dataset).where(Dataset.slug == slug))
        if dataset is None:
            dataset = Dataset(
                slug=slug,
                name=name,
                source_id=source.id,
                data_domain=data_domain,
                status=status,
                description=description,
            )
            self.session.add(dataset)
            self.session.flush()
        else:
            dataset.name = name
            dataset.source_id = source.id
            dataset.data_domain = data_domain
            dataset.status = status
            dataset.description = description
        self.session.flush()
        return dataset

    def register_version(
        self,
        dataset_slug: str,
        version_label: str,
        file_hash: str | None = None,
        storage_uri: str | None = None,
        status: str = "draft",
    ) -> Any:
        dataset = self.session.scalar(select(Dataset).where(Dataset.slug == dataset_slug))
        if dataset is None:
            raise ValueError(f"Dataset '{dataset_slug}' not found")

        version = DatasetVersion(
            dataset_id=dataset.id,
            version_label=version_label,
            file_hash=file_hash,
            storage_uri=storage_uri,
            status=status,
            published_at=datetime.utcnow() if status == "published" else None,
        )
        self.session.add(version)
        self.session.flush()
        return version


__all__ = ["DatasetRegistry"]
