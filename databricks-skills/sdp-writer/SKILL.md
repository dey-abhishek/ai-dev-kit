---
name: sdp-writer
description: "Create, configure, or update Databricks' Lakeflow Spark Declarative Pipelines (SDP), also known as LDP, or historically Delta Live Tables (DLT). User should guide on using SQL or Python syntax."
---

# Lakeflow Spark Declarative Pipelines (SDP) Writer

## Official Documentation

- **[Lakeflow Spark Declarative Pipelines Overview](https://docs.databricks.com/aws/en/ldp/)** - Main documentation hub
- **[Python Language Reference](https://docs.databricks.com/aws/en/ldp/developer/python-ref)** - `pyspark.pipelines` API
- **[SQL Language Reference](https://docs.databricks.com/aws/en/dlt-ref/sql-ref)** - SQL syntax for streaming tables and materialized views
- **[Loading Data](https://docs.databricks.com/aws/en/ldp/load)** - Auto Loader, Kafka, Kinesis ingestion
- **[Change Data Capture (CDC)](https://docs.databricks.com/aws/en/ldp/cdc)** - AUTO CDC, SCD Type 1/2
- **[Developing Pipelines](https://docs.databricks.com/aws/en/ldp/develop)** - File structure, testing, validation
- **[Tutorial: Build an ETL Pipeline](https://docs.databricks.com/aws/en/getting-started/data-pipeline-get-started)** - Step-by-step guide
- **[Liquid Clustering](https://docs.databricks.com/aws/en/delta/clustering)** - Modern data layout optimization
- **[Reference Architecture](https://www.databricks.com/resources/architectures/build-production-etl-with-lakeflow-declarative-pipelines)** - Production patterns

---

## Development Workflow with MCP Tools

This skill uses MCP tools to create and iterate on SDP pipelines. Follow this workflow:

### Step 1: Write Pipeline Files Locally

Create `.sql` or `.py` files in a local folder structure:

```
my_pipeline/
└── transformations/
    ├── bronze/
    │   └── ingest_orders.sql
    ├── silver/
    │   └── clean_orders.sql
    └── gold/
        └── daily_summary.sql
```

**Example bronze layer** (`transformations/bronze/ingest_orders.sql`):
```sql
CREATE OR REPLACE STREAMING TABLE bronze_orders
CLUSTER BY (order_date)
AS
SELECT
  *,
  current_timestamp() AS _ingested_at,
  _metadata.file_path AS _source_file
FROM read_files(
  '/Volumes/catalog/schema/raw/orders/',
  format => 'json',
  schemaHints => 'order_id STRING, customer_id STRING, amount DECIMAL(10,2), order_date DATE'
);
```

### Step 2: Upload Local Folder to Databricks Workspace

Use the **`upload_folder`** tool to upload your local pipeline folder to the Databricks workspace:

```python
# MCP Tool: upload_folder
upload_folder(
    local_folder="/path/to/my_pipeline",
    workspace_folder="/Workspace/Users/user@example.com/my_pipeline"
)
```

This uploads all files in parallel and creates the directory structure automatically.

### Step 3: Create the Pipeline

Use the **`create_pipeline`** tool to create the SDP pipeline:

```python
# MCP Tool: create_pipeline
result = create_pipeline(
    name="my_orders_pipeline",
    root_path="/Workspace/Users/user@example.com/my_pipeline",
    catalog="my_catalog",
    schema="my_schema",
    workspace_notebook_paths=[
        "/Workspace/Users/user@example.com/my_pipeline/transformations/bronze/ingest_orders.sql",
        "/Workspace/Users/user@example.com/my_pipeline/transformations/silver/clean_orders.sql",
        "/Workspace/Users/user@example.com/my_pipeline/transformations/gold/daily_summary.sql"
    ],
    serverless=True
)
pipeline_id = result.pipeline_id
```

### Step 4: Start Pipeline Update and Monitor

Run the pipeline and monitor progress:

```python
# MCP Tool: start_update (dry run first to validate)
update_id = start_update(pipeline_id=pipeline_id, validate_only=True)

# MCP Tool: get_update (poll for status)
status = get_update(pipeline_id=pipeline_id, update_id=update_id)
# Status states: QUEUED, RUNNING, COMPLETED, FAILED

# If validation passes, run the actual update
update_id = start_update(pipeline_id=pipeline_id)
status = get_update(pipeline_id=pipeline_id, update_id=update_id)
```

### Step 5: Debug Errors with Pipeline Events

If the pipeline fails, get error details:

```python
# MCP Tool: get_pipeline_events
events = get_pipeline_events(pipeline_id=pipeline_id, max_results=50)
# Review error messages and stack traces
```

### Step 6: Iterate Until Working

1. Review errors from `get_pipeline_events`
2. Fix issues in local files
3. Re-upload with `upload_folder` (overwrites existing files)
4. Run `start_update` again
5. Repeat until `get_update` shows `COMPLETED`

### Step 7: Verify Output Tables with Table Stats

Once the pipeline completes, **verify the output tables are populated correctly** using `get_table_details`:

```python
# MCP Tool: get_table_details
# Verify bronze table has data
bronze_stats = get_table_details(
    catalog="my_catalog",
    schema="my_schema",
    table_names=["bronze_orders"],
    table_stat_level="SIMPLE"  # or "DETAILED" for column stats
)
# Check: row_count > 0, columns match expected schema

# Verify all pipeline tables
all_stats = get_table_details(
    catalog="my_catalog",
    schema="my_schema",
    table_names=["bronze_*", "silver_*", "gold_*"],  # GLOB patterns
    table_stat_level="DETAILED"
)
```

**Use table stats to debug:**
- **Empty tables**: Check upstream sources, filter conditions
- **Missing columns**: Verify schema hints, column mappings
- **Unexpected row counts**: Review WHERE clauses, deduplication logic
- **Data quality issues**: Check column value distributions with DETAILED stats

---

## Overview

Create SDP pipelines in SQL or Python with 2025 best practices.

**Language Selection** (prompt if not specified):
- **SQL**: Simple transformations, SQL team, declarative style
- **Python**: Complex logic, UDFs, Python team (see [python-api-versions.md](python-api-versions.md) for modern `dp` API)

**Modern Approach (2025)**:
- Use `CLUSTER BY` (Liquid Clustering) not `PARTITION BY`
- Use serverless compute for auto-scaling

---

## Reference Documentation (Local)

Load these modules for detailed patterns:

- **[ingestion-patterns.md](ingestion-patterns.md)** - Auto Loader, Kafka, Event Hub, file formats
- **[streaming-patterns.md](streaming-patterns.md)** - Deduplication, windowing, stateful operations
- **[scd-query-patterns.md](scd-query-patterns.md)** - Querying SCD2 history tables
- **[dlt-migration-guide.md](dlt-migration-guide.md)** - Migrating from DLT Python to SDP SQL
- **[performance-tuning.md](performance-tuning.md)** - Liquid Clustering, optimization, compute config
- **[python-api-versions.md](python-api-versions.md)** - Modern `dp` API vs legacy `dlt` API

---

## Development Environment

### Lakeflow Pipelines Editor (Recommended)

**Use the new Pipelines Editor** (not DLT notebooks):
- Multi-file tabbed editor with .sql/.py files
- Interactive DAG with data preview
- Selective execution (single file or full pipeline)
- Dry run validation without materializing data

**Medallion folder structure**:
```
PipelineName/
└── transformations/
    ├── bronze/    # Raw ingestion
    ├── silver/    # Cleaned, validated
    └── gold/      # Aggregated analytics
```

### ⚠️ API: Always Preserve root_path

When updating pipelines via API, **always include `root_path`**:
- Required for folder structure display in UI
- Required for Python imports from utilities
- Easily lost during PUT requests

```json
{
  "name": "Pipeline",
  "catalog": "my_catalog",
  "target": "my_schema",
  "root_path": "/Workspace/Users/.../PipelineName",
  "libraries": [...]
}
```

### ⚠️ Use .sql/.py Files, Not DLT Notebooks

**Old approach** (avoid):
```python
# MAGIC %sql
# MAGIC CREATE OR REFRESH STREAMING TABLE my_table
# MAGIC AS SELECT * FROM source
```

**New approach** (use):
```sql
-- File: transformations/bronze/my_table.sql
CREATE OR REFRESH STREAMING TABLE my_table
AS SELECT * FROM source;
```

Use `"file"` library type in pipeline config, not `"notebook"` library type.

---

## Core Patterns

All examples use Unity Catalog three-part names: `catalog.schema.table`

### Bronze Layer (Ingestion)

```sql
CREATE OR REPLACE STREAMING TABLE catalog.schema.bronze_orders
CLUSTER BY (order_date, region)
AS
SELECT *, current_timestamp() AS _ingested_at
FROM read_files('/mnt/raw/orders/', format => 'json',
  schemaHints => 'order_id STRING, amount DECIMAL(10,2)');
```

**See [ingestion-patterns.md](ingestion-patterns.md)** for Auto Loader options, Kafka/Event Hub sources, schema evolution

### Silver Layer (Cleansing)

```sql
CREATE OR REPLACE STREAMING TABLE catalog.schema.silver_orders
CLUSTER BY (customer_id, order_date)
AS
SELECT
  CAST(order_id AS STRING) AS order_id,
  customer_id,
  CAST(order_date AS DATE) AS order_date,
  CAST(total_amount AS DECIMAL(10,2)) AS total_amount
FROM STREAM catalog.schema.bronze_orders
WHERE total_amount IS NOT NULL AND order_id IS NOT NULL;
```

**Data Quality**: Use WHERE for filtering. **See [ingestion-patterns.md](ingestion-patterns.md)** for quarantine patterns

### Gold Layer (Aggregation)

```sql
CREATE OR REPLACE MATERIALIZED VIEW catalog.schema.gold_sales_summary
CLUSTER BY (order_day)
AS
SELECT
  date_trunc('day', order_date) AS order_day,
  COUNT(DISTINCT order_id) AS order_count,
  SUM(total_amount) AS daily_sales
FROM catalog.schema.silver_orders
GROUP BY date_trunc('day', order_date);
```

**See [performance-tuning.md](performance-tuning.md)** for clustering strategies, MV refresh optimization

### Temporary View (Intermediate)

```sql
CREATE TEMPORARY VIEW filtered_orders
AS SELECT * FROM catalog.schema.silver_orders
WHERE order_date >= CURRENT_DATE() - INTERVAL 30 DAYS;
```

**Python**:
```python
@dp.temporary_view()
def filtered_orders():
    return spark.read.table("catalog.schema.silver_orders").filter("order_date >= current_date() - interval 30 days")
```

**Use for**: Intermediate transformations not persisted to storage

### Multiple Sources to One Target

```python
dp.create_streaming_table("all_events")

@dp.append_flow(target="all_events")
def source_a_events():
    return spark.readStream.table("catalog.schema.source_a")

@dp.append_flow(target="all_events")
def source_b_events():
    return spark.readStream.table("catalog.schema.source_b")
```

**Use for**: Combining multiple streams into unified table

### SCD Type 1 (Current State Only)

```sql
CREATE OR REFRESH STREAMING TABLE catalog.schema.customers;

CREATE FLOW catalog.schema.customers_cdc_flow AS
AUTO CDC INTO catalog.schema.customers
FROM stream(catalog.schema.customers_cdc_clean)
KEYS (customer_id)
SEQUENCE BY event_timestamp
APPLY AS DELETE WHEN operation = "DELETE"
COLUMNS * EXCEPT (operation, event_timestamp, _rescued_data)
STORED AS SCD TYPE 1;
```

### SCD Type 2 (History Tracking)

```sql
CREATE OR REFRESH STREAMING TABLE catalog.schema.customers_history;

CREATE FLOW catalog.schema.customers_history_cdc AS
AUTO CDC INTO catalog.schema.customers_history
FROM stream(catalog.schema.customers_cdc_clean)
KEYS (customer_id)
SEQUENCE BY event_timestamp
APPLY AS DELETE WHEN operation = "DELETE"
COLUMNS * EXCEPT (operation, event_timestamp, _rescued_data)
STORED AS SCD TYPE 2
TRACK HISTORY ON *;
```

Auto-generates START_AT/END_AT columns. **See [scd-query-patterns.md](scd-query-patterns.md)** for querying patterns

**Selective tracking**: Use `TRACK HISTORY ON price, cost` to track only specific columns

**See [streaming-patterns.md](streaming-patterns.md)** for deduplication, windowing, late-arriving data, joins

### Execution Modes

- **Triggered**: Scheduled batch (lower cost, configure in pipeline settings)
- **Continuous**: Real-time streaming (sub-second latency, configure in pipeline settings)

---

## MCP Tools Reference

### Pipeline Management

| Tool | Description |
|------|-------------|
| `create_pipeline` | Create new pipeline with name, catalog, schema, notebook paths |
| `get_pipeline` | Get pipeline configuration and state |
| `update_pipeline` | Update pipeline configuration |
| `delete_pipeline` | Delete a pipeline |
| `start_update` | Start pipeline run or dry-run validation |
| `get_update` | Get update status (QUEUED, RUNNING, COMPLETED, FAILED) |
| `stop_pipeline` | Stop a running pipeline |
| `get_pipeline_events` | Get error messages and events for debugging |

### File Operations

| Tool | Description |
|------|-------------|
| `upload_folder` | Upload local folder to workspace (parallel) |
| `upload_file` | Upload single file to workspace |

### Data Verification

| Tool | Description |
|------|-------------|
| `get_table_details` | Get table schema and statistics to verify pipeline output |
| `execute_sql` | Run ad-hoc SQL queries to inspect data |

---

## Platform Constraints

| Constraint | Details |
|------------|---------|
| **CDC Features** | Requires serverless or Pro/Advanced edition |
| **Schema Evolution** | Streaming tables require full refresh for incompatible changes |
| **Stream Joins** | Don't recompute when dimension tables change (use MV for that) |
| **Sinks** | Python only, streaming only, append flows only |
| **SQL Limitations** | PIVOT clause unsupported in pipelines |

---

## Common Issues

| Issue | Solution |
|-------|----------|
| **Streaming reads fail** | Use `FROM stream(...)` for append-only sources |
| **Misordered CDC updates** | Use strictly increasing SEQUENCE BY field (non-NULL timestamp) |
| **SCD2 schema errors** | Let SDP infer START_AT/END_AT or include both with SEQUENCE BY type |
| **AUTO CDC target conflicts** | Keep CDC targets exclusive to AUTO CDC flows |
| **MV doesn't refresh incrementally** | Enable Delta row tracking on source, avoid row filters |
| **High latency/cost** | Use triggered mode for batch; continuous only for sub-second SLA |
| **Slow startups** | Use serverless compute (not classic clusters) |
| **Deletes not honored** | Increase `pipelines.cdc.tombstoneGCThresholdInSeconds` |
| **Empty output tables** | Use `get_table_details` to verify data, check upstream sources |

**For detailed troubleshooting**, see individual reference files
