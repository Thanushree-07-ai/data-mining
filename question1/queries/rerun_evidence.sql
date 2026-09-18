SELECT
    COUNT(*) AS canonical_rows,
    SUM(revenue) AS total_revenue,
    MD5(
        STRING_AGG(
            CONCAT(
                store_id, '|',
                business_date, '|',
                bill_no, '|',
                line_no, '|',
                product_code, '|',
                qty, '|',
                unit_price, '|',
                line_type
            ),
            '||'
            ORDER BY
                store_id,
                business_date,
                bill_no,
                line_no
        )
    ) AS checksum
FROM read_parquet(
    's3://annapurna/canonical/store=*/year=*/month=*/sales.parquet'
);