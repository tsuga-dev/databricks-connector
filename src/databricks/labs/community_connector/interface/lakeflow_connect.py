from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Iterator

try:
    from pyspark.sql.types import StructType
except ModuleNotFoundError:  # pragma: no cover - local test fallback
    StructType = Any  # type: ignore[assignment]


class LakeflowConnect(ABC):
    """Minimal standalone copy of the Lakeflow connector contract."""

    def __init__(self, options: dict[str, str]) -> None:
        self.options = options

    @abstractmethod
    def list_tables(self) -> list[str]:
        """List supported source tables."""

    @abstractmethod
    def get_table_schema(
        self, table_name: str, table_options: dict[str, str]
    ) -> StructType:
        """Return the Spark schema for the requested table."""

    @abstractmethod
    def read_table_metadata(
        self, table_name: str, table_options: dict[str, str]
    ) -> dict:
        """Return metadata such as ingestion type and cursor field."""

    @abstractmethod
    def read_table(
        self, table_name: str, start_offset: dict, table_options: dict[str, str]
    ) -> tuple[Iterator[dict], dict]:
        """Return records and an end offset."""

    def read_table_deletes(
        self, table_name: str, start_offset: dict, table_options: dict[str, str]
    ) -> tuple[Iterator[dict], dict]:
        raise NotImplementedError(
            "read_table_deletes() is only required for cdc_with_deletes sources"
        )

