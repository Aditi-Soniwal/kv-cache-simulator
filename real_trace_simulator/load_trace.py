
import pandas as pd
from pathlib import Path
import math

# Locate the project and dataset
PROJECT_DIR = Path(__file__).resolve().parent.parent

DATASET_PATH = (
    PROJECT_DIR
    / "datasets"
    / "mooncake"
    / "conversations"
    / "train-00000-of-00001.parquet"
)

BLOCK_SIZE = 512


def load_mooncake_trace():

    print("Loading Mooncake conversation trace...")

    df = pd.read_parquet(DATASET_PATH)

    required_columns = [
        "timestamp",
        "input_length",
        "output_length",
        "hash_ids"
    ]

    # Validate columns
    missing = set(required_columns) - set(df.columns)

    if missing:
        raise ValueError(f"Missing columns: {missing}")

    # Preserve original order for requests with equal timestamps
    df = df.sort_values(
        "timestamp",
        kind="stable"
    ).reset_index(drop=True)

    requests = []

    for index, row in df.iterrows():

        hashes = [int(h) for h in row["hash_ids"]]

        expected_blocks = math.ceil(
            int(row["input_length"]) / BLOCK_SIZE
        )

        if len(hashes) != expected_blocks:
            raise ValueError(
                f"Block count mismatch at request {index}"
            )

        requests.append({
            "request_id": index,
            "timestamp": int(row["timestamp"]),
            "input_length": int(row["input_length"]),
            "output_length": int(row["output_length"]),
            "hash_ids": hashes
        })

    print("\n========== TRACE LOADED ==========")
    print("Total requests:", len(requests))
    print("Block size:", BLOCK_SIZE, "tokens")
    print("First timestamp:", requests[0]["timestamp"])
    print("Last timestamp:", requests[-1]["timestamp"])

    print(
        "Total prefix blocks:",
        sum(len(r["hash_ids"]) for r in requests)
    )

    return requests


if __name__ == "__main__":
    requests = load_mooncake_trace()

    print("\nFirst request:")
    print(requests[0])

    print("\nSecond request:")
    print(requests[1])
