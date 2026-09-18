import os
import re
import time
import hashlib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOTICE_DIR = os.path.join(BASE_DIR, "data", "notices")
LABEL_FILE = os.path.join(BASE_DIR, "data", "labelled_pairs.csv")
RESULTS_DIR = os.path.join(BASE_DIR, "results")

os.makedirs(RESULTS_DIR, exist_ok=True)

# ---------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------
print("=" * 70)
print("SECTION E - CORPUS SKEW AND MITIGATION")
print("=" * 70)

files = sorted([
    os.path.join(NOTICE_DIR, f)
    for f in os.listdir(NOTICE_DIR)
    if f.lower().endswith(".csv")
])

df = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)
labels = pd.read_csv(LABEL_FILE)

print(f"Notices: {len(df)}")
print(f"Labelled pairs: {len(labels)}")

texts = df["title"].fillna("") + " " + df["body"].fillna("")

# ---------------------------------------------------------
# NORMALIZATION
# ---------------------------------------------------------
BOILERPLATE = [
    "national procurement aggregation service",
    "state procurement cell",
    "this portal is an aggregation service",
    "disclaimer",
    "all information displayed here is collected from source portals",
]

def basic_normalize(text):
    text = str(text).lower()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def mitigated_normalize(text):
    text = basic_normalize(text)

    # Remove known portal boilerplate from portal_profiles.md
    for phrase in BOILERPLATE:
        text = text.replace(phrase, " ")

    # Remove reference numbers
    text = re.sub(
        r"\b(?:ref(?:erence)?|tender|bid|notice|procurement)[\s:#-]*"
        r"[a-z]*\d+[a-z0-9/-]*\b",
        " ",
        text,
        flags=re.I
    )

    # Remove dates
    text = re.sub(
        r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b", " ", text
    )
    text = re.sub(
        r"\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b", " ", text
    )

    # Remove email / phone
    text = re.sub(r"\b[\w.+-]+@[\w.-]+\.\w+\b", " ", text)
    text = re.sub(r"\b\d{10}\b", " ", text)

    # Remove standalone numbers
    text = re.sub(r"\b\d+\b", " ", text)

    text = re.sub(r"\s+", " ", text)
    return text.strip()

def trigrams(text):
    tokens = text.split()
    if len(tokens) < 3:
        return set(tokens)
    return {
        " ".join(tokens[i:i+3])
        for i in range(len(tokens) - 2)
    }

# ---------------------------------------------------------
# LSH
# ---------------------------------------------------------
K = 128
BANDS = 32
ROWS = 4
P = 4294967311

rng = np.random.default_rng(42)
A = rng.integers(1, P - 1, size=K, dtype=np.int64)
B = rng.integers(0, P - 1, size=K, dtype=np.int64)

def hash_token(token):
    return int.from_bytes(
        hashlib.blake2b(
            token.encode("utf-8"),
            digest_size=8
        ).digest(),
        "little"
    ) % P

def signature(tokens):
    if not tokens:
        return np.full(K, P - 1, dtype=np.int64)

    hv = np.array([hash_token(t) for t in tokens], dtype=np.int64)

    sig = np.full(K, P - 1, dtype=np.int64)

    for i in range(K):
        values = (A[i] * hv + B[i]) % P
        sig[i] = values.min()

    return sig

def build_lsh(text_series):
    start = time.perf_counter()

    signatures = []

    for text in text_series:
        signatures.append(signature(trigrams(text)))

    signatures = np.array(signatures)

    buckets = {}

    for idx, sig in enumerate(signatures):
        for band in range(BANDS):
            start_i = band * ROWS
            end_i = start_i + ROWS

            raw = sig[start_i:end_i].tobytes()
            bucket = hashlib.sha1(raw).hexdigest()

            key = (band, bucket)

            if key not in buckets:
                buckets[key] = []

            buckets[key].append(idx)

    runtime = time.perf_counter() - start

    return signatures, buckets, runtime

def bucket_stats(buckets):
    sizes = np.array([len(v) for v in buckets.values()])

    return {
        "num_buckets": len(sizes),
        "mean": float(np.mean(sizes)),
        "median": float(np.median(sizes)),
        "p95": float(np.percentile(sizes, 95)),
        "p99": float(np.percentile(sizes, 99)),
        "max": int(np.max(sizes)),
    }

def candidate_count_for_pair(
    sig_a, sig_b
):
    for band in range(BANDS):
        start_i = band * ROWS
        end_i = start_i + ROWS

        if np.array_equal(
            sig_a[start_i:end_i],
            sig_b[start_i:end_i]
        ):
            return True
    return False

# ---------------------------------------------------------
# BASELINE
# ---------------------------------------------------------
print("\nBuilding BASELINE representation...")
start = time.perf_counter()

baseline_text = texts.map(basic_normalize)
baseline_signatures, baseline_buckets, baseline_runtime = build_lsh(
    baseline_text
)

baseline_total_time = time.perf_counter() - start
baseline_stats = bucket_stats(baseline_buckets)

print("\nBASELINE")
for k, v in baseline_stats.items():
    print(f"{k}: {v}")
print(f"Runtime: {baseline_total_time:.3f} sec")

# ---------------------------------------------------------
# MITIGATED
# ---------------------------------------------------------
print("\nBuilding MITIGATED representation...")
start = time.perf_counter()

mitigated_text = texts.map(mitigated_normalize)
mitigated_signatures, mitigated_buckets, mitigated_runtime = build_lsh(
    mitigated_text
)

mitigated_total_time = time.perf_counter() - start
mitigated_stats = bucket_stats(mitigated_buckets)

print("\nMITIGATED")
for k, v in mitigated_stats.items():
    print(f"{k}: {v}")
print(f"Runtime: {mitigated_total_time:.3f} sec")

# ---------------------------------------------------------
# LABELLED RETRIEVAL QUALITY
# ---------------------------------------------------------
id_to_idx = {
    notice_id: idx
    for idx, notice_id in enumerate(df["notice_id"])
}

def evaluate(signatures):
    survived = 0
    valid = 0

    for _, row in labels.iterrows():

        a = row["notice_id_a"]
        b = row["notice_id_b"]

        if a not in id_to_idx or b not in id_to_idx:
            continue

        ia = id_to_idx[a]
        ib = id_to_idx[b]

        survives = candidate_count_for_pair(
            signatures[ia],
            signatures[ib]
        )

        valid += 1

        if survives:
            survived += 1

    return survived / valid if valid else 0

baseline_recall = evaluate(baseline_signatures)
mitigated_recall = evaluate(mitigated_signatures)

print("\nLABELLED-PAIR RETRIEVAL QUALITY")
print(f"Baseline candidate survival:  {baseline_recall:.4f}")
print(f"Mitigated candidate survival: {mitigated_recall:.4f}")

# ---------------------------------------------------------
# SAVE TABLE
# ---------------------------------------------------------
comparison = pd.DataFrame([
    {
        "version": "baseline",
        **baseline_stats,
        "runtime_sec": baseline_total_time,
        "labelled_pair_survival": baseline_recall
    },
    {
        "version": "mitigated",
        **mitigated_stats,
        "runtime_sec": mitigated_total_time,
        "labelled_pair_survival": mitigated_recall
    }
])

comparison.to_csv(
    os.path.join(RESULTS_DIR, "section_e_before_after.csv"),
    index=False
)

print("\nSaved:")
print("results/section_e_before_after.csv")

# ---------------------------------------------------------
# PLOT BUCKET DISTRIBUTION
# ---------------------------------------------------------
baseline_sizes = np.array([
    len(v) for v in baseline_buckets.values()
])

mitigated_sizes = np.array([
    len(v) for v in mitigated_buckets.values()
])

plt.figure(figsize=(9, 5))

plt.hist(
    baseline_sizes,
    bins=50,
    alpha=0.6,
    label="Baseline"
)

plt.hist(
    mitigated_sizes,
    bins=50,
    alpha=0.6,
    label="Mitigated"
)

plt.xlabel("Bucket size")
plt.ylabel("Number of buckets")
plt.title("LSH Bucket Size Distribution Before vs After Mitigation")
plt.legend()
plt.tight_layout()

plot_path = os.path.join(
    RESULTS_DIR,
    "section_e_bucket_distribution.png"
)

plt.savefig(plot_path, dpi=150)
plt.close()

print("Saved:")
print("results/section_e_bucket_distribution.png")

print("\n" + "=" * 70)
print("SECTION E COMPLETE")
print("=" * 70)