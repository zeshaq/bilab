# ADR-0004: Warehouse-native (no data copy)

Status: Accepted

## Context

Traditional ETL-based BI copies data into its own store, adding cost, latency,
and a second place for data to go stale. The customer already owns a warehouse
of record (in the lab: Trino over Iceberg populated by Oracle CDC). bilab
should query that data in place.

## Decision

bilab is a query-in-place layer. It never copies or ETLs data into its own
store. The only materialized state is the semantic layer's pre-aggregation
cache, which is a derived, disposable performance artifact — not the data of
record.

## Consequences

Positive:
- No data duplication, no sync lag, no second source of truth.
- Cheaper and simpler to operate; works with any warehouse the customer has.
- The semantic layer compiles to warehouse SQL, so it inherits the warehouse's
  engine and permissions.

Negative:
- Performance is bounded by the warehouse unless pre-aggregations are tuned;
  "instant dashboards" requires disciplined caching (ADR-0001's pre-aggregations).
- Cross-warehouse joins are not possible without a federation layer; acceptable
  because we assume a single warehouse of record per workspace.

## Alternatives considered

- ETL into an owned store (e.g., DuckDB/ClickHouse): faster queries under our
  control, but reintroduces the copy/staleness problem and makes bilab own data
  it doesn't want to own. Rejected.
- Hybrid (query in place + optional extract): possible later for specific
  high-latency sources, but not the default and not the core architecture.
