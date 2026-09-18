INSTALL httpfs;
LOAD httpfs;

INSTALL postgres;
LOAD postgres;

SET s3_endpoint='minio:9000';
SET s3_access_key_id='admin';
SET s3_secret_access_key='admin12345';
SET s3_use_ssl=false;
SET s3_url_style='path';
SET s3_region='us-east-1';

ATTACH
'host=postgres port=5432 dbname=annapurna user=postgres password=postgres'
AS pg (TYPE POSTGRES, READ_ONLY);


-- =========================================================
-- Q1-A : OBJECT STORE PARTITIONING
-- =========================================================

-- Complete partitioned dataset
SELECT
    COUNT(*) AS parquet_files,
    COALESCE(SUM(file_size_bytes), 0) AS total_bytes
FROM parquet_file_metadata(
    '/workspace/canonical/store=*/year=*/month=*/sales.parquet'
);


-- One store + one month
-- Only the required partition is selected.
SELECT
    COUNT(*) AS files_for_S01_october,
    COALESCE(SUM(file_size_bytes), 0) AS bytes_for_S01_october
FROM parquet_file_metadata(
    '/workspace/canonical/store=S01/year=2024/month=10/sales.parquet'
);


-- Original unpartitioned source
SELECT
    COUNT(*) AS raw_files,
    COALESCE(SUM(size), 0) AS raw_bytes
FROM read_blob('/exam/data/sales/*');


-- =========================================================
-- Q1-B : SAFE RERUN / DEDUPLICATION
-- =========================================================

SELECT
    COUNT(*) AS canonical_rows
FROM read_parquet(
    '/workspace/canonical/store=*/year=*/month=*/sales.parquet'
);


SELECT
    COUNT(DISTINCT
        bill_no || '|' || CAST(line_no AS VARCHAR)
    ) AS unique_bill_line_keys
FROM read_parquet(
    '/workspace/canonical/store=*/year=*/month=*/sales.parquet'
);


SELECT
    COUNT(*) AS duplicate_bill_line_keys
FROM
(
    SELECT
        bill_no,
        line_no
    FROM read_parquet(
        '/workspace/canonical/store=*/year=*/month=*/sales.parquet'
    )
    GROUP BY bill_no, line_no
    HAVING COUNT(*) > 1
);


-- =========================================================
-- Q1-C : DASHBOARD REVENUE
-- =========================================================

CREATE OR REPLACE TEMP VIEW dashboard_revenue AS

WITH sales AS
(
    SELECT
        store_id,
        product_code,
        business_date,
        day_of_week,
        revenue,
        line_type
    FROM read_parquet(
        '/workspace/canonical/store=*/year=*/month=*/sales.parquet'
    )
    WHERE line_type IN
        ('SALE', 'RETURN', 'DISCOUNT', 'VOID')
),

enriched AS
(
    SELECT
        s.store_id,
        p.category_id,
        c.category_name,
        s.business_date,
        s.day_of_week,
        s.revenue
    FROM sales s

    JOIN pg.public.products p
        ON p.product_code = s.product_code
       AND s.business_date >= p.valid_from
       AND s.business_date < p.valid_to

    JOIN pg.public.product_categories c
        ON c.category_id = p.category_id
)

SELECT
    store_id,
    category_id,
    category_name,
    day_of_week,
    CAST(
        DATE_TRUNC('month', business_date)
        AS DATE
    ) AS month,
    SUM(revenue) AS revenue
FROM enriched
GROUP BY
    store_id,
    category_id,
    category_name,
    day_of_week,
    CAST(
        DATE_TRUNC('month', business_date)
        AS DATE
    );


SELECT
    d.store_id,
    st.store_name,
    d.category_id,
    d.category_name,
    d.day_of_week,
    d.month,
    d.revenue
FROM dashboard_revenue d

JOIN pg.public.stores st
    ON st.store_id = d.store_id

ORDER BY
    d.store_id,
    d.month,
    d.category_name,
    d.day_of_week;


-- =========================================================
-- Q1-D : HISTORICAL PRICE
-- Same query for March 2024 and last month.
-- =========================================================

WITH max_data AS
(
    SELECT
        MAX(business_date) AS max_business_date
    FROM read_parquet(
        '/workspace/canonical/store=*/year=*/month=*/sales.parquet'
    )
),

periods AS
(
    SELECT
        DATE '2024-03-01' AS report_month,
        'March 2024' AS period_name

    UNION ALL

    SELECT
        CAST(
            DATE_TRUNC('month', max_business_date)
            - INTERVAL '1 month'
            AS DATE
        ) AS report_month,
        'Last month in dataset' AS period_name
    FROM max_data
)

SELECT
    prd.period_name,
    prd.report_month,
    p.product_sk,
    p.product_code,
    p.product_name,
    p.category_id,
    pr.revision_id,
    pr.mrp,
    pr.selling_price,
    pr.effective_from,
    pr.effective_to

FROM periods prd

JOIN pg.public.products p
    ON prd.report_month >= p.valid_from
   AND prd.report_month < p.valid_to

JOIN pg.public.price_revisions pr
    ON pr.product_sk = p.product_sk
   AND prd.report_month >= pr.effective_from
   AND prd.report_month < pr.effective_to

ORDER BY
    prd.report_month,
    p.product_code,
    pr.effective_from;


-- =========================================================
-- Q1-E : CROSS-SYSTEM QUERY
-- Parquet/MinIO + PostgreSQL
-- =========================================================

EXPLAIN
SELECT
    s.store_id,
    st.store_name,
    SUM(s.revenue) AS revenue

FROM read_parquet(
    's3://annapurna/canonical/store=*/year=*/month=*/sales.parquet'
) s

JOIN pg.public.stores st
    ON st.store_id = s.store_id

WHERE s.line_type IN
    ('SALE', 'RETURN', 'DISCOUNT', 'VOID')

GROUP BY
    s.store_id,
    st.store_name

ORDER BY
    s.store_id;


-- Actual cross-system query
SELECT
    s.store_id,
    st.store_name,
    SUM(s.revenue) AS revenue

FROM read_parquet(
    's3://annapurna/canonical/store=*/year=*/month=*/sales.parquet'
) s

JOIN pg.public.stores st
    ON st.store_id = s.store_id

WHERE s.line_type IN
    ('SALE', 'RETURN', 'DISCOUNT', 'VOID')

GROUP BY
    s.store_id,
    st.store_name

ORDER BY
    s.store_id;


-- =========================================================
-- Q1-F : MONTHLY REVENUE
-- =========================================================

SELECT
    CAST(
        DATE_TRUNC('month', business_date)
        AS DATE
    ) AS month,

    SUM(revenue) AS revenue

FROM read_parquet(
    's3://annapurna/canonical/store=*/year=*/month=*/sales.parquet'
)

WHERE line_type IN
    ('SALE', 'RETURN', 'DISCOUNT', 'VOID')

GROUP BY
    CAST(
        DATE_TRUNC('month', business_date)
        AS DATE
    )

ORDER BY
    month;


-- =========================================================
-- OCTOBER 2024 : DETERMINISTIC REVENUE
-- =========================================================

SELECT
    SUM(revenue) AS october_2024_revenue

FROM read_parquet(
    's3://annapurna/canonical/store=*/year=*/month=*/sales.parquet'
)

WHERE business_date >= DATE '2024-10-01'
  AND business_date < DATE '2024-11-01'

  AND line_type IN
      ('SALE', 'RETURN', 'DISCOUNT', 'VOID');


-- =========================================================
-- FINANCE MONTHLY FILE
-- =========================================================

SELECT *
FROM read_csv_auto(
    '/exam/data/finance_monthly.csv'
);