# Databricks notebook source
"""Tsuga Logs ingestion pipeline — ready to run.

The Tsuga configuration (API key, query, cluster) lives on the Unity Catalog
connection created in the wizard. This file discovers that connection
automatically; if you have several tsuga_logs connections, set
`connection_name` explicitly below.
"""

from databricks.labs.community_connector import register
from databricks.labs.community_connector.pipeline import ingest

# Enable the injection of Unity Catalog connection properties into the connector
spark.conf.set("spark.databricks.unityCatalog.connectionDfOptionInjection.enabled", "true")

connection_name = None  # set to pin a specific connection, e.g. "my_tsuga_conn"

if connection_name is None:
    # SHOW CONNECTIONS is blocked in pipelines; the workspace API is not.
    try:
        from databricks.sdk import WorkspaceClient

        matches = [
            c.name
            for c in WorkspaceClient().connections.list()
            if str(getattr(c, "connection_type", "")).endswith("GENERIC_LAKEFLOW_CONNECT")
            and (c.options or {}).get("sourceName") == "tsuga_logs"
        ]
    except Exception as discovery_error:  # noqa: BLE001 — any failure falls back to manual pinning
        raise ValueError(
            "Could not discover the tsuga_logs connection automatically "
            f"({discovery_error!r}). Set connection_name explicitly above."
        ) from discovery_error
    if len(matches) != 1:
        raise ValueError(
            f"Found {len(matches)} tsuga_logs connections {matches}; "
            "set connection_name explicitly above."
        )
    connection_name = matches[0]

register(spark, "tsuga_logs")

ingest(spark, {
    "connection_name": connection_name,
    "objects": [{"table": {"source_table": "logs"}}],
})
