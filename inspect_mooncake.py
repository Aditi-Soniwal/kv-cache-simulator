
import pandas as pd

file_path = (
    "datasets/mooncake/conversations/"
    "train-00000-of-00001.parquet"
)

print("Loading Mooncake dataset...")

df = pd.read_parquet(file_path)

print("\n========== DATASET INFORMATION ==========")

print("Total rows:", len(df))
print("Total columns:", len(df.columns))

print("\nColumn names:")
print(df.columns.tolist())

print("\nColumn data types:")
print(df.dtypes)

print("\nFirst 5 records:")
print(df.head().to_string())

print("\n========== FIRST RECORD ==========")
print(df.iloc[0].to_dict())

print("\n========== DETAILED DATASET ANALYSIS ==========")

print("\nDataset shape:", df.shape)

print("\nTimestamp statistics:")
print(df["timestamp"].describe())

print("\nUnique timestamps:", df["timestamp"].nunique())

print("\nFirst 20 timestamps:")
print(df["timestamp"].head(20).tolist())

print("\nMissing values:")
print(df.isnull().sum())

print("\nHash IDs information:")
print("First request block count:", len(df.iloc[0]["hash_ids"]))
print("Second request block count:", len(df.iloc[1]["hash_ids"]))

# Count how many hash IDs are shared
from collections import Counter

all_hashes = []

for hashes in df["hash_ids"]:
    all_hashes.extend(hashes)

hash_counts = Counter(all_hashes)

shared_hashes = {
    key: count
    for key, count in hash_counts.items()
    if count > 1
}

print("\nTotal hash occurrences:", len(all_hashes))
print("Unique hash IDs:", len(hash_counts))
print("Repeated hash IDs:", len(shared_hashes))

print("\nMost reused hash IDs:")
print(hash_counts.most_common(10))

import math

print("\n========== CACHE REUSE VALIDATION ==========")

import numpy as np

zero_count = sum(
    np.count_nonzero(hashes == 0)
    for hashes in df["hash_ids"]
)

print("Hash ID 0 occurrences:", zero_count)
print("Total requests:", len(df))

# Check request ordering
print("\nTimestamps sorted:",
      df["timestamp"].is_monotonic_increasing)

print("Minimum timestamp:", df["timestamp"].min())
print("Maximum timestamp:", df["timestamp"].max())

# Validate number of prefix blocks
mismatches = []

for index, row in df.iterrows():
    expected = math.ceil(row["input_length"] / 512)
    actual = len(row["hash_ids"])

    if expected != actual:
        mismatches.append((index, expected, actual))

print("\nBlock count mismatches:", len(mismatches))
print("First mismatches:", mismatches[:10])

# Examine repeated hashes excluding zero
from collections import Counter

counts = Counter(
    h
    for hashes in df["hash_ids"]
    for h in hashes
    if h != 0
)

print("\nUnique non-zero hash IDs:", len(counts))
print("Repeated non-zero hash IDs:",
      sum(1 for count in counts.values() if count > 1))

print("\nMost reused non-zero hashes:")
print(counts.most_common(10))
