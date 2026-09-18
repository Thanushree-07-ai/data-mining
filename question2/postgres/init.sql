CREATE TABLE IF NOT EXISTS notices (
    notice_id TEXT PRIMARY KEY,
    portal_id TEXT,
    published_at TIMESTAMP,
    title TEXT,
    body TEXT,
    estimated_value NUMERIC,
    closing_date DATE
);

CREATE TABLE IF NOT EXISTS lsh_buckets (
    band INTEGER NOT NULL,
    bucket TEXT NOT NULL,
    notice_id TEXT NOT NULL,
    PRIMARY KEY (band, bucket, notice_id)
);

CREATE INDEX IF NOT EXISTS idx_lsh_band_bucket
ON lsh_buckets (band, bucket);