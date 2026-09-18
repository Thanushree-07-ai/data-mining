SELECT
    COUNT(*) AS partitioned_parquet_files,
    COALESCE(SUM(size), 0) AS partitioned_bytes
FROM glob('/workspace/canonical/store=*/year=*/month=*/sales.parquet');

SELECT
    COUNT(*) AS all_source_files,
    COALESCE(SUM(size), 0) AS all_source_bytes
FROM glob('/exam/data/sales/*');