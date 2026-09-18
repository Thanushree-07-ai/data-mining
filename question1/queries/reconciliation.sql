INSTALL httpfs;
LOAD httpfs;

SET s3_endpoint='minio:9000';
SET s3_access_key_id='admin';
SET s3_secret_access_key='admin12345';
SET s3_use_ssl=false;
SET s3_url_style='path';
SET s3_region='us-east-1';


-- =========================================================
-- Q1-F : RECONCILIATION WITH FINANCE
-- =========================================================

WITH calculated AS
(
    SELECT
        CAST(
            DATE_TRUNC('month', business_date)
            AS DATE
        ) AS month,

        ROUND(
            SUM(revenue),
            2
        ) AS calculated_revenue

    FROM read_parquet(
        's3://annapurna/canonical/store=*/year=*/month=*/sales.parquet'
    )

    WHERE line_type IN
        ('SALE', 'RETURN', 'DISCOUNT', 'VOID')

    GROUP BY 1
),

finance AS
(
    SELECT
        STRPTIME(month, '%Y-%m')::DATE AS month,

        ROUND(
            CAST(revenue_inr AS DOUBLE),
            2
        ) AS finance_revenue

    FROM read_csv_auto(
        '/exam/data/finance_monthly.csv',
        HEADER = TRUE
    )
),

comparison AS
(
    SELECT
        COALESCE(c.month, f.month) AS month,

        COALESCE(c.calculated_revenue, 0)
            AS calculated_revenue,

        COALESCE(f.finance_revenue, 0)
            AS finance_revenue

    FROM calculated c

    FULL OUTER JOIN finance f
        ON c.month = f.month
)

SELECT
    STRFTIME(month, '%Y-%m') AS month,

    ROUND(calculated_revenue, 2)
        AS calculated_revenue,

    ROUND(finance_revenue, 2)
        AS finance_revenue,

    ROUND(
        calculated_revenue - finance_revenue,
        2
    ) AS difference,

    CASE

        WHEN calculated_revenue = finance_revenue
            THEN 'MATCH'

        WHEN STRFTIME(month, '%Y-%m') = '2024-07'
            THEN 'SOURCE ISSUE'

        WHEN STRFTIME(month, '%Y-%m') = '2024-03'
            THEN 'REVENUE DEFINITION DIFFERENCE'

        WHEN STRFTIME(month, '%Y-%m') = '2024-12'
            THEN 'PIPELINE BUG / ROUNDING DIFFERENCE'

        ELSE
            'INVESTIGATE'

    END AS classification,

    CASE

        WHEN calculated_revenue = finance_revenue
            THEN 'No action'

        WHEN STRFTIME(month, '%Y-%m') = '2024-07'
            THEN 'Take source gap to finance'

        WHEN STRFTIME(month, '%Y-%m') = '2024-03'
            THEN 'Take revenue definition difference to finance'

        WHEN STRFTIME(month, '%Y-%m') = '2024-12'
            THEN 'Take small pipeline/rounding discrepancy to finance'

        ELSE
            'Investigate with finance'

    END AS action

FROM comparison

ORDER BY month;