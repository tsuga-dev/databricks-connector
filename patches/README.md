# Framework patches

## lakeflow-framework-unique-view-names.patch

**Status: documentation only — not deployed.** Kept as material for an
upstream issue/PR.

Upstream `databricks/labs/community_connector/pipeline/ingestion_pipeline.py`
cannot ingest the same `source_table` twice in one pipeline:

1. The intermediate SDP view name is derived from the source table only
   (`source_{source_table}_{flow_type}`), so two objects sharing a
   `source_table` collide with `Cannot redefine dataset 'source_logs_upsert'`.
   The function's own docstring says the destination should be part of the
   name; this patch fixes that (with identifier sanitization, since the
   destination arrives backtick-qualified).
2. Deeper: `SpecParser.get_table_configurations()` merges configs into one
   dict keyed by source table name, so even with unique view names the second
   object resolves to the first object's configuration.

Because of (2), the workable deployment shape is **one pipeline per logical
table** with one job running the pipeline tasks. Any connector ingesting the same source table twice (GitHub
`issues` for two repos, for example) hits the same limitation upstream.

## Upstream port note — merge exclusion

`tools/scripts/merge_exclude_config.json` in the upstream repo needs a
`"tsuga_logs": ["sample-ingest.py"]` entry under `source_exclude` (precedent:
`microsoft_teams`), or the merge script inlines the notebook sample and fails
on its framework imports.
