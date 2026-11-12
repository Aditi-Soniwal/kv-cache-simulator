
import pandas as pd
from collections import Counter

path = (
    "datasets/mooncake/conversations/"
    "train-00000-of-00001.parquet"
)

df = pd.read_parquet(path)

# Count each non-zero hash ID
counts = Counter()

for hashes in df["hash_ids"]:
    counts.update(int(h) for h in hashes if h != 0)

# Analyse prefix overlap between consecutive requests
prefix_lengths = []

for i in range(1, len(df)):
    previous = [int(h) for h in df.iloc[i-1]["hash_ids"]]
    current = [int(h) for h in df.iloc[i]["hash_ids"]]

    shared = 0

    for a, b in zip(previous, current):
        if a == b:
            shared += 1
        else:
            break

    prefix_lengths.append(shared)

print("========== PREFIX REUSE ANALYSIS ==========")

print("Requests:", len(df))
print("Repeated non-zero hash IDs:",
      sum(1 for c in counts.values() if c > 1))

print("\nConsecutive request comparisons:",
      len(prefix_lengths))

print("Comparisons with shared prefix:",
      sum(1 for x in prefix_lengths if x > 0))

print("Average shared prefix blocks:",
      round(sum(prefix_lengths) / len(prefix_lengths), 3))

print("Maximum shared prefix blocks:",
      max(prefix_lengths))

print("\nFirst 20 shared-prefix lengths:")
print(prefix_lengths[:20])

print("\nMost frequent non-zero hashes:")
print(counts.most_common(10))

print("\n========== GLOBAL PREFIX REUSE ==========")

# Count how many requests contain each hash
request_frequency = Counter()

for hashes in df["hash_ids"]:
    request_frequency.update(set(int(h) for h in hashes))

# Reuse across requests
print("Total distinct prefix hashes:",
      len(request_frequency))

print("Hashes used by multiple requests:",
      sum(1 for count in request_frequency.values()
          if count > 1))

print("\nTop 15 hashes by request frequency:")
print(request_frequency.most_common(15))

# Distribution of request reuse
reuse_distribution = Counter(request_frequency.values())

print("\nReuse frequency distribution:")
for frequency, number_of_hashes in sorted(
    reuse_distribution.items()
):
    print(f"Used in {frequency} requests: {number_of_hashes} hashes")
