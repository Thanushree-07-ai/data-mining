import os
import re
import hashlib
from pathlib import Path

import pandas as pd
import boto3
from botocore.client import Config


# ============================================================
# CONFIGURATION
# ============================================================

DATA_DIR = Path(
    os.getenv("DATA_DIR", "/exam/data")
)

OUTPUT_DIR = Path(
    os.getenv("OUTPUT_DIR", "/workspace/canonical")
)

MINIO_ENDPOINT = os.getenv(
    "MINIO_ENDPOINT",
    "http://minio:9000"
)

MINIO_USER = os.getenv(
    "MINIO_USER",
    "admin"
)

MINIO_PASSWORD = os.getenv(
    "MINIO_PASSWORD",
    "admin12345"
)

BUCKET = "annapurna"


# ============================================================
# COLUMN NORMALIZATION
# ============================================================

COLUMN_MAP = {
    "bill_no": "bill_no",
    "line_no": "line_no",
    "product_code": "product_code",
    "item_code": "product_code",
    "qty": "qty",
    "quantity": "qty",
    "unit_price": "unit_price",
    "rate": "unit_price",
    "line_type": "line_type",
    "type": "line_type",
    "ts": "ts",
    "txn_time": "ts",
}


def normalize_columns(df):
    rename = {}

    for col in df.columns:
        clean = str(col).replace("\ufeff", "").strip().lower()

        if clean in COLUMN_MAP:
            rename[col] = COLUMN_MAP[clean]

    df = df.rename(columns=rename)

    required = [
        "bill_no",
        "line_no",
        "product_code",
        "qty",
        "unit_price",
        "line_type",
        "ts",
    ]

    missing = [c for c in required if c not in df.columns]

    if missing:
        raise ValueError(
            f"Missing columns {missing}; found {list(df.columns)}"
        )

    return df[required].copy()


# ============================================================
# READ ONE FILE
# ============================================================

def read_file(path):
    suffix = path.suffix.lower()

    if suffix == ".parquet":
        df = pd.read_parquet(path)

    elif suffix == ".csv":

        # S01-S05 = comma
        # S06-S09 = semicolon
        # S10-S12 = comma + BOM

        with open(path, "rb") as f:
            first_bytes = f.read(1000)

        first_line = first_bytes.decode(
            "utf-8-sig",
            errors="replace"
        ).splitlines()[0]

        if ";" in first_line:
            df = pd.read_csv(
                path,
                sep=";",
                encoding="utf-8-sig"
            )
        else:
            df = pd.read_csv(
                path,
                sep=",",
                encoding="utf-8-sig"
            )

    else:
        raise ValueError(f"Unsupported file: {path}")

    df = normalize_columns(df)

    return df


# ============================================================
# BUSINESS DATE FROM FILENAME
# ============================================================

def get_business_date(path):

    name = path.name

    match = re.search(
        r"SALES_([A-Za-z0-9]+)_(\d{8})",
        name,
        re.IGNORECASE
    )

    if not match:
        raise ValueError(
            f"Cannot determine store/date from filename: {name}"
        )

    store = match.group(1)
    business_date = pd.to_datetime(
        match.group(2),
        format="%Y%m%d"
    )

    return store, business_date


# ============================================================
# PROCESS ALL FILES
# ============================================================

def build_canonical():

    files = sorted(
        list(DATA_DIR.joinpath("sales").glob("*.csv"))
        + list(DATA_DIR.joinpath("sales").glob("*.parquet"))
    )

    if not files:
        raise FileNotFoundError(
            f"No sales files found in {DATA_DIR / 'sales'}"
        )

    print(f"Source files found: {len(files)}")

    frames = []

    for i, path in enumerate(files, 1):

        store, business_date = get_business_date(path)

        df = read_file(path)

        df["store_id"] = store
        df["business_date"] = business_date

        # Convert types
        df["bill_no"] = df["bill_no"].astype(str).str.strip()
        df["line_no"] = pd.to_numeric(
            df["line_no"],
            errors="coerce"
        )

        df["product_code"] = (
            df["product_code"]
            .astype(str)
            .str.strip()
        )

        df["qty"] = pd.to_numeric(
            df["qty"],
            errors="coerce"
        )

        df["unit_price"] = pd.to_numeric(
            df["unit_price"],
            errors="coerce"
        )

        df["line_type"] = (
            df["line_type"]
            .astype(str)
            .str.strip()
            .str.upper()
        )

        # Remove unusable rows
        df = df.dropna(
            subset=[
                "bill_no",
                "line_no",
                "qty",
                "unit_price",
                "line_type"
            ]
        )

        frames.append(df)

        if i % 250 == 0:
            print(f"Processed {i}/{len(files)} files")

    all_data = pd.concat(
        frames,
        ignore_index=True
    )

    print(f"Raw rows: {len(all_data):,}")

    # ========================================================
    # CRITICAL: DEDUPLICATE RE-SENDS
    # ========================================================
    #
    # Safe business key:
    # (bill_no, line_no)
    #
    # A re-send may be incomplete, so we union lines rather
    # than choosing newest/oldest file.
    # ========================================================

    all_data = all_data.drop_duplicates(
        subset=["bill_no", "line_no"],
        keep="first"
    )

    print(
        f"Rows after line-level deduplication: "
        f"{len(all_data):,}"
    )

    # ========================================================
    # REVENUE
    # ========================================================

    # SALE, RETURN, DISCOUNT and VOID count.
    # TAX and TENDER do NOT count.
    #
    # Keeping VOID together with original SALE means cancelled
    # bills naturally net to zero.

    revenue_types = {
        "SALE",
        "RETURN",
        "DISCOUNT",
        "VOID",
    }

    all_data["revenue"] = 0.0

    mask = all_data["line_type"].isin(
        revenue_types
    )

    all_data.loc[mask, "revenue"] = (
        all_data.loc[mask, "qty"]
        * all_data.loc[mask, "unit_price"]
    )

    # ========================================================
    # DAY / MONTH ATTRIBUTES
    # ========================================================

    all_data["day_of_week"] = (
        all_data["business_date"]
        .dt.day_name()
    )

    all_data["year"] = (
        all_data["business_date"]
        .dt.year
    )

    all_data["month"] = (
        all_data["business_date"]
        .dt.month
    )

    # ========================================================
    # SORT
    # ========================================================

    all_data = all_data.sort_values(
        [
            "store_id",
            "business_date",
            "bill_no",
            "line_no"
        ]
    )

    # ========================================================
    # WRITE PARTITIONED PARQUET
    # ========================================================

    if OUTPUT_DIR.exists():
        import shutil
        shutil.rmtree(OUTPUT_DIR)

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    for (
        store,
        year,
        month
    ), group in all_data.groupby(
        ["store_id", "year", "month"]
    ):

        partition = (
            OUTPUT_DIR
            / f"store={store}"
            / f"year={year}"
            / f"month={month:02d}"
        )

        partition.mkdir(
            parents=True,
            exist_ok=True
        )

        output_file = (
            partition / "sales.parquet"
        )

        group.to_parquet(
            output_file,
            index=False
        )

    # ========================================================
    # CHECKSUM
    # ========================================================

    canonical = all_data[
        [
            "bill_no",
            "line_no",
            "product_code",
            "qty",
            "unit_price",
            "line_type",
            "store_id",
            "business_date",
            "revenue",
        ]
    ].copy()

    checksum_input = (
        canonical
        .astype(str)
        .to_csv(index=False)
        .encode("utf-8")
    )

    checksum = hashlib.sha256(
        checksum_input
    ).hexdigest()

    checksum_file = (
        OUTPUT_DIR / "_checksum.txt"
    )

    checksum_file.write_text(
        checksum,
        encoding="utf-8"
    )

    print()
    print("========== INGESTION RESULT ==========")
    print(f"Raw rows:       {sum(len(x) for x in frames):,}")
    print(f"Canonical rows: {len(all_data):,}")
    print(f"Revenue:        {all_data['revenue'].sum():,.2f}")
    print(f"Checksum:       {checksum}")
    print(f"Output:         {OUTPUT_DIR}")
    print("=======================================")


# ============================================================
# UPLOAD TO MINIO
# ============================================================

def upload_to_minio():

    s3 = boto3.client(
        "s3",
        endpoint_url=MINIO_ENDPOINT,
        aws_access_key_id=MINIO_USER,
        aws_secret_access_key=MINIO_PASSWORD,
        config=Config(signature_version="s3v4"),
        region_name="us-east-1",
    )

    buckets = s3.list_buckets()["Buckets"]

    if not any(
        b["Name"] == BUCKET
        for b in buckets
    ):
        s3.create_bucket(
            Bucket=BUCKET
        )

    count = 0

    for file in OUTPUT_DIR.rglob("*"):

        if not file.is_file():
            continue

        key = (
            "canonical/"
            + str(file.relative_to(OUTPUT_DIR))
            .replace("\\", "/")
        )

        s3.upload_file(
            str(file),
            BUCKET,
            key
        )

        count += 1

    print(
        f"Uploaded {count} objects to "
        f"s3://{BUCKET}/canonical/"
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print("Starting Annapurna ingestion...")
    print(f"DATA_DIR = {DATA_DIR}")

    build_canonical()

    # Upload only when MinIO is reachable.
    try:
        upload_to_minio()
    except Exception as e:
        print(
            f"MinIO upload failed: {e}"
        )
        print(
            "Canonical data was still created locally."
        )