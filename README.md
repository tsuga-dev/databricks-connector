# Tsuga Logs — Databricks Lakeflow Community Connector

Ingest [Tsuga](https://www.tsuga.com) logs into Delta tables you own in Unity Catalog, on a schedule.

## Set up in Databricks (5 minutes)

> Prerequisite: a workspace where Lakeflow community connectors are enabled (the `generic_lfc` workspace setting on older workspaces).

1. In your workspace: **Add data → + Add Community Connector** — source name `tsuga_logs`, this repository's URL, branch `master`.
2. **Create connection**: keep Auth Type `USES_ANY_STATIC_CREDENTIAL`, name the connection, switch **Additional Options** to **JSON** and paste (fill in your key; `query`/`cluster_id` are optional defaults — see the connector README):

```json
{
  "sourceName": "tsuga_logs",
  "operation_api_key": "<YOUR_OPERATION_API_KEY>",
  "base_url": "https://api.tsuga.com",
  "query": "<YOUR_TSUGA_QUERY>",
  "cluster_id": "<YOUR_CLUSTER_ID_IF_MULTI_CLUSTER>",
  "externalOptionsAllowList": "tableName,tableNameList,tableConfigs,isDeleteFlow,query,cluster_id,initial_lookback_seconds,incremental_overlap_seconds,window_seconds,page_size,max_concurrency,max_events_per_sync,request_timeout_seconds,allow_truncated_seconds"
}
```

3. **Ingestion setup**: pipeline name; event log location (any catalog/schema you can write to — ingested tables land there by default); root path like `/Users/<you>/tsuga_connector/src` — **the folder must already exist** (the wizard creates a Git folder inside it but not the directories above).
4. In the generated `ingest.py`, replace the placeholder objects with the one real table (the connection name is already filled in):

```python
"objects": [{"table": {"source_table": "logs"}}],
```

5. **Run pipeline.** Logs matching your connection's `query` land in a Delta table named `logs` and stay current on every run.

Full reference — per-table options, output schema, pagination semantics, pitfalls:
[`src/databricks/labs/community_connector/sources/tsuga_logs/README.md`](src/databricks/labs/community_connector/sources/tsuga_logs/README.md)

## What it does

- Pulls logs from Tsuga's public `GET /v1/logs/search` API with an operation API key
- Incremental sync with a checkpointed cursor: missed runs self-heal, overlap re-reads deduplicate via the CDC key
- Paginates around the public API's 1000-row cap by recursive time-splitting; optional `allow_truncated_seconds` for burst-heavy sources
- Multi-cluster organizations supported via `cluster_id`
- Stable output schema (`event_time`, `level`, `message`, `service_name`, `team`, `env`, `raw_json`, `extracted_at`); heterogeneous payloads ride in `raw_json` without schema churn
- Several differently-filtered log tables can share one connection (per-table `query` overrides) — one pipeline per table (upstream framework keys configs by source table; see `patches/`)

## Repository layout

Mirrors the [databrickslabs/lakeflow-community-connectors](https://github.com/databrickslabs/lakeflow-community-connectors) layout so the Databricks UI and tooling work against it directly:

```
src/databricks/labs/community_connector/
├── sources/tsuga_logs/                  # the connector (README = full reference)
├── source_simulator/specs/tsuga_logs/   # offline test fixtures (upstream test harness)
└── interface/ libs/ pipeline/ sparkpds/ # framework vendored from databrickslabs/
                                         # lakeflow-community-connectors (see NOTICE) —
                                         # required: the custom-connector UI clones only
                                         # this repo, so all runtime imports must resolve here
tests/                                   # unit tests (pure Python, no Spark needed)
patches/                                 # notes on upstream framework limitations
```

## Development

```bash
python3 -m pytest tests/        # client, pagination, and connector contract tests
```

`tests/unit/` mirrors the upstream repo's harness layout and runs inside a checkout of `databrickslabs/lakeflow-community-connectors`.

An example pipeline spec for the CLI deployment path is in [`pipeline_spec.example.yaml`](pipeline_spec.example.yaml).
