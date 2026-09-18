import os
import re
import time
import hashlib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")
NOTICE_DIR = os.path.join(DATA, "notices")
RESULTS = os.path.join(BASE, "results")
os.makedirs(RESULTS, exist_ok=True)

# ============================================================
# 1. LOAD DATA
# ============================================================

print("========== Q2 DATA LOADING ==========")

notice_files = sorted(
    os.path.join(NOTICE_DIR, f)
    for f in os.listdir(NOTICE_DIR)
    if f.lower().endswith(".csv")
)

df = pd.concat(
    [pd.read_csv(f) for f in notice_files],
    ignore_index=True
)

labels = pd.read_csv(
    os.path.join(DATA, "labelled_pairs.csv")
)

print("Notice files:", len(notice_files))
print("Notices:", len(df))
print("Labelled pairs:", len(labels))

print("\nLabel distribution:")
print(labels["label"].value_counts())

# ============================================================
# 2. NORMALIZATION
# ============================================================

print("\n========== NORMALIZATION ==========")

def normalize(text):
    text = str(text).lower()

    # Remove known portal boilerplate
    boilerplate = [
        "national procurement aggregation service",
        "state procurement cell -- consolidated tender bulletin",
        "government of india",
        "government of india -- procurement portal"
    ]

    for phrase in boilerplate:
        text = text.replace(phrase, " ")

    # Reference numbers
    text = re.sub(
        r'\b(?:npas-\d{4}-\d+|spc/\d{4}-\d{2}/\d+|pwd/\d{4}/\d+|'
        r'ref-\d{4}-\d+|mc/\d{4}/w/\d+|tn-\d+/\d{4})\b',
        ' ',
        text
    )

    # Dates
    text = re.sub(
        r'\b\d{1,4}[-/.]\d{1,2}[-/.]\d{1,4}\b',
        ' ',
        text
    )

    # Money values
    text = re.sub(
        r'\b(?:rs|inr)\.?\s*[\d,./ -]+(?:cr|crore|lakh)?\b',
        ' ',
        text
    )

    # Email / phone
    text = re.sub(r'\S+@\S+', ' ', text)
    text = re.sub(r'\b\d{8,}\b', ' ', text)

    # Other standalone numbers
    text = re.sub(r'\b\d+(?:\.\d+)?\b', ' ', text)

    # Punctuation / whitespace
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()

    return text


df["clean_text"] = (
    df["title"].fillna("") + " " +
    df["body"].fillna("")
).map(normalize)

notice_map = df.set_index("notice_id")

print("Normalization complete.")

# ============================================================
# 3. WORD N-GRAMS
# ============================================================

def make_ngrams(text, n):
    words = text.split()

    if len(words) < n:
        return set(words)

    return {
        " ".join(words[i:i+n])
        for i in range(len(words)-n+1)
    }


def jaccard(a, b):
    union = a | b

    if not union:
        return 0.0

    return len(a & b) / len(union)


# ============================================================
# 4. SECTION A
# COMPARE UNIGRAMS VS TRIGRAMS
# ============================================================

print("\n========== SECTION A ==========")

def get_similarity(row, n):
    a = notice_map.loc[row["notice_id_a"], "clean_text"]
    b = notice_map.loc[row["notice_id_b"], "clean_text"]

    return jaccard(
        make_ngrams(a, n),
        make_ngrams(b, n)
    )


labels["unigram_similarity"] = labels.apply(
    lambda r: get_similarity(r, 1),
    axis=1
)

labels["trigram_similarity"] = labels.apply(
    lambda r: get_similarity(r, 3),
    axis=1
)

print("\nMean similarity by label:")
print(
    labels.groupby("label")[
        ["unigram_similarity", "trigram_similarity"]
    ].mean()
)

same = labels[labels["label"] == "same"]

different = labels[labels["label"] == "different"]

print("\nExample SAME pair:")
print(
    same[
        [
            "notice_id_a",
            "notice_id_b",
            "unigram_similarity",
            "trigram_similarity"
        ]
    ].head(1).to_string(index=False)
)

print("\nExample DIFFERENT pair:")
print(
    different[
        [
            "notice_id_a",
            "notice_id_b",
            "unigram_similarity",
            "trigram_similarity"
        ]
    ].head(1).to_string(index=False)
)

print("""
ADOPTED CHOICE:
Word 3-grams.

Signal:
substantive tender wording, scope, eligibility and work description.

Noise:
portal boilerplate, reference numbers, dates, monetary formatting,
emails, phone numbers and standalone identifiers.

Similarity:
Jaccard similarity = intersection / union.
""")

# ============================================================
# 5. SECTION B
# 128-VALUE MINHASH
# ============================================================

print("\n========== SECTION B ==========")

K = 128

# Fixed before implementation.
print("MinHash size:", K)

# Stable 64-bit hash for each token.
def token_hash(token):
    return int.from_bytes(
        hashlib.blake2b(
            token.encode("utf-8"),
            digest_size=8
        ).digest(),
        "little"
    )


# Generate deterministic universal-hash parameters.
rng = np.random.default_rng(42)

A = rng.integers(
    1,
    np.iinfo(np.uint64).max,
    size=K,
    dtype=np.uint64
)

B = rng.integers(
    0,
    np.iinfo(np.uint64).max,
    size=K,
    dtype=np.uint64
)

P = np.uint64(18446744073709551557)


def minhash(tokens):
    if not tokens:
        return np.zeros(K, dtype=np.uint64)

    values = np.array(
        [token_hash(t) for t in tokens],
        dtype=np.uint64
    )

    sig = np.full(
        K,
        np.uint64(18446744073709551615)
    )

    for value in values:
        hashed = (A * value + B) % P
        sig = np.minimum(sig, hashed)

    return sig


# Only labelled notices are required for error measurement.
needed_ids = set(labels["notice_id_a"]) | set(labels["notice_id_b"])

signature_cache = {}

start = time.perf_counter()

for nid in needed_ids:
    tokens = make_ngrams(
        notice_map.loc[nid, "clean_text"],
        3
    )

    signature_cache[nid] = minhash(tokens)

print(
    "Signature creation time:",
    round(time.perf_counter() - start, 3),
    "seconds"
)

errors = []

for _, row in labels.iterrows():

    sig_a = signature_cache[row["notice_id_a"]]
    sig_b = signature_cache[row["notice_id_b"]]

    estimate = np.mean(sig_a == sig_b)

    exact = row["trigram_similarity"]

    errors.append(abs(estimate - exact))

errors = np.array(errors)

print("Mean absolute error:", round(float(errors.mean()), 6))
print(
    "95th percentile error:",
    round(float(np.quantile(errors, 0.95)), 6)
)
print("Maximum error:", round(float(errors.max()), 6))

print("""
APPLICATION REQUIREMENT:
Mean absolute estimation error <= 0.05
and 95th percentile error <= 0.10.

ADOPTED:
128 MinHash values.

The realised error above is measured against the trusted labelled
pairs rather than assumed from a tutorial.
""")

# ============================================================
# 6. FULL-CORPUS MINHASH
# ============================================================

print("\n========== FULL CORPUS SIGNATURES ==========")

all_signatures = {}

start = time.perf_counter()

for i, row in df.iterrows():

    tokens = make_ngrams(
        row["clean_text"],
        3
    )

    all_signatures[row["notice_id"]] = minhash(tokens)

    if (i + 1) % 1000 == 0:
        print("Processed:", i + 1)

full_time = time.perf_counter() - start

print(
    "Full signature construction time:",
    round(full_time, 3),
    "seconds"
)

# ============================================================
# 7. SECTION C
# LSH CANDIDATE RETRIEVAL
# ============================================================

print("\n========== SECTION C ==========")

BANDS = 32
ROWS = 4

print("Bands:", BANDS)
print("Rows per band:", ROWS)

buckets = {}

for nid, sig in all_signatures.items():

    for band in range(BANDS):

        start_pos = band * ROWS
        end_pos = start_pos + ROWS

        band_values = sig[start_pos:end_pos]

        key = hashlib.sha1(
            band_values.tobytes()
        ).hexdigest()

        bucket_id = (band, key)

        if bucket_id not in buckets:
            buckets[bucket_id] = []

        buckets[bucket_id].append(nid)


def get_candidates(nid):

    sig = all_signatures[nid]

    result = set()

    for band in range(BANDS):

        start_pos = band * ROWS
        end_pos = start_pos + ROWS

        key = hashlib.sha1(
            sig[start_pos:end_pos].tobytes()
        ).hexdigest()

        result.update(
            buckets.get((band, key), [])
        )

    result.discard(nid)

    return result


candidate_counts = []
found = 0

for _, row in labels.iterrows():

    candidates = get_candidates(row["notice_id_a"])

    candidate_counts.append(len(candidates))

    if row["notice_id_b"] in candidates:
        found += 1

candidate_recall = found / len(labels)

print("Candidate recall:", round(candidate_recall, 6))
print(
    "Average candidate count:",
    round(float(np.mean(candidate_counts)), 2)
)
print(
    "Median candidate count:",
    int(np.median(candidate_counts))
)
print(
    "Maximum candidate count:",
    int(np.max(candidate_counts))
)

# ============================================================
# 8. RETRIEVAL CURVE
# ============================================================

thresholds = np.arange(
    0.1,
    1.0,
    0.1
)

recall_curve = []

for threshold in thresholds:

    eligible = 0
    retrieved = 0

    for _, row in labels.iterrows():

        sim = row["trigram_similarity"]

        if sim >= threshold:

            eligible += 1

            candidates = get_candidates(
                row["notice_id_a"]
            )

            if row["notice_id_b"] in candidates:
                retrieved += 1

    if eligible:
        recall_curve.append(
            retrieved / eligible
        )
    else:
        recall_curve.append(0)

plt.figure(figsize=(8, 5))

plt.plot(
    thresholds,
    recall_curve,
    marker="o"
)

plt.xlabel("True Jaccard similarity")
plt.ylabel("Candidate survival probability")
plt.title("LSH Candidate Retrieval Curve")
plt.grid(True)

curve_file = os.path.join(
    RESULTS,
    "candidate_recall_curve.png"
)

plt.savefig(
    curve_file,
    dpi=150,
    bbox_inches="tight"
)

plt.close()

print("Curve saved:", curve_file)

# ============================================================
# 9. BUCKET DISTRIBUTION / SECTION E
# ============================================================

print("\n========== SECTION E ==========")

bucket_sizes = np.array(
    [len(v) for v in buckets.values()]
)

print("Number of buckets:", len(bucket_sizes))
print("Mean bucket size:", round(float(bucket_sizes.mean()), 2))
print("Median bucket size:", int(np.median(bucket_sizes)))
print("P95 bucket size:", round(float(np.quantile(bucket_sizes, .95)), 2))
print("P99 bucket size:", round(float(np.quantile(bucket_sizes, .99)), 2))
print("Maximum bucket size:", int(bucket_sizes.max()))

largest = sorted(
    [
        (band, key, len(ids))
        for (band, key), ids in buckets.items()
    ],
    key=lambda x: x[2],
    reverse=True
)[:10]

print("\nTop 10 buckets:")

for item in largest:
    print(item)

# ============================================================
# 10. SAVE RESULTS FOR DATABASE
# ============================================================

print("\n========== SAVING RESULTS ==========")

df[
    [
        "notice_id",
        "portal_id",
        "published_at",
        "title",
        "body",
        "estimated_value",
        "closing_date"
    ]
].to_csv(
    os.path.join(
        RESULTS,
        "notices_load.csv"
    ),
    index=False
)

bucket_rows = []

for (band, key), ids in buckets.items():

    for nid in ids:

        bucket_rows.append(
            {
                "band": band,
                "bucket": key,
                "notice_id": nid
            }
        )

pd.DataFrame(bucket_rows).to_csv(
    os.path.join(
        RESULTS,
        "lsh_buckets_load.csv"
    ),
    index=False
)

print("Saved notices_load.csv")
print("Saved lsh_buckets_load.csv")

print("\n========== Q2 A-C-E COMPLETE ==========")