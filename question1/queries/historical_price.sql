INSTALL postgres;
LOAD postgres;

ATTACH
'host=postgres port=5432 dbname=annapurna user=postgres password=postgres'
AS pg (TYPE POSTGRES, READ_ONLY);

-- Change this one date to test another reporting period.
WITH params AS (
    SELECT DATE '2024-03-01' AS report_month
),

report_date AS (
    SELECT
        report_month,
        LAST_DAY(report_month) AS report_end
    FROM params
)

SELECT
    p.product_code,
    p.product_name,
    p.product_sk,
    pr.mrp,
    pr.selling_price,
    pr.effective_from,
    pr.effective_to
FROM pg.main.products p
JOIN pg.main.price_revisions pr
    ON pr.product_sk = p.product_sk
CROSS JOIN report_date r
WHERE r.report_end >= p.valid_from
  AND r.report_end < p.valid_to
  AND r.report_end >= pr.effective_from
  AND r.report_end < pr.effective_to
ORDER BY
    p.product_code,
    p.product_sk;