INSTALL httpfs;
LOAD httpfs;

SET s3_endpoint='minio:9000';
SET s3_access_key_id='admin';
SET s3_secret_access_key='admin12345';
SET s3_use_ssl=false;
SET s3_url_style='path';
SET s3_region='us-east-1';

INSTALL postgres;
LOAD postgres;

ATTACH
'host=postgres port=5432 dbname=annapurna user=postgres password=postgres'
AS pg (TYPE POSTGRES, READ_ONLY);

EXPLAIN
SELECT
    s.store_id,
    st.store_name,
    SUM(s.revenue) AS revenue
FROM read_parquet(
    's3://annapurna/canonical/store=*/year=*/month=*/sales.parquet'
) s
JOIN pg.main.stores st
    ON st.store_id = s.store_id
WHERE s.line_type IN ('SALE', 'RETURN', 'DISCOUNT', 'VOID')
GROUP BY
    s.store_id,
    st.store_name
ORDER BY
    s.store_id;

SELECT
    s.store_id,
    st.store_name,
    SUM(s.revenue) AS revenue
FROM read_parquet(
    's3://annapurna/canonical/store=*/year=*/month=*/sales.parquet'
) s
JOIN pg.main.stores st
    ON st.store_id = s.store_id
WHERE s.line_type IN ('SALE', 'RETURN', 'DISCOUNT', 'VOID')
GROUP BY
    s.store_id,
    st.store_name
ORDER BY
    s.store_id;