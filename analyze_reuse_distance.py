
import pandas as pd
from collections import defaultdict
import numpy as np

path = (
    "datasets/mooncake/conversations/"
    "train-00000-of-00001.parquet"
)

df = pd.read_parquet(path)

last_seen = {}
reuse_distances = []

for request_index, hashes in enumerate(df["hash_ids"]):

    for raw_hash in hashes:

        h = int(raw_hash)

        # Exclude common hash 0 for this diagnostic
        if h == 0:
            continue

        if h in last_seen:
            distance = request_index - last_seen[h]
            reuse_distances.append(distance)

        last_seen[h] = request_index

print("\n========== REUSE DISTANCE ANALYSIS ==========")

if reuse_distances:

    distances = np.array(reuse_distances)

    print("Total reuse events:", len(distances))
    print("Minimum distance:", distances.min())
    print("Maximum distance:", distances.max())
    print("Average distance:", round(distances.mean(), 2))
    print("Median distance:", np.median(distances))

    print("\nPercentiles:")
    for p in [25, 50, 75, 90, 95, 99]:
        print(f"{p}th percentile:",
              np.percentile(distances, p))

    print("\nReuse distance groups:")

    bins = [0, 10, 50, 100, 500, 1000, 5000, float("inf")]

    labels = [
        "1-10 requests",
        "11-50 requests",
        "51-100 requests",
        "101-500 requests",
        "501-1000 requests",
        "1001-5000 requests",
        "More than 5000 requests"
    ]

    for i, label in enumerate(labels):
        count = np.sum(
            (distances > bins[i]) &
            (distances <= bins[i + 1])
        )
        print(label, ":", count)

else:
    print("No reuse events found.")
