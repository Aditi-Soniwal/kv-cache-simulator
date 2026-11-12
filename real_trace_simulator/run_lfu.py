
import pandas as pd
from pathlib import Path

from load_trace import load_mooncake_trace
from lfu_block_cache import LFUBlockCache


# Load the same Mooncake trace used for LRU
requests = load_mooncake_trace()

# Same capacities as the LRU experiment
capacities = [256, 512, 1024, 2048, 4096]

# Same two experiment modes
experiment_modes = [
    {
        "name": "full_prefix",
        "exclude_root": False
    },
    {
        "name": "root_excluded",
        "exclude_root": True
    }
]

summary_results = []
position_results = []

for mode in experiment_modes:

    mode_name = mode["name"]
    exclude_root = mode["exclude_root"]

    print("\n")
    print("#" * 60)
    print("EXPERIMENT:", mode_name.upper())
    print("#" * 60)

    for capacity in capacities:

        print("\n" + "=" * 50)
        print(
            f"Running LFU | Capacity: {capacity} | "
            f"Mode: {mode_name}"
        )
        print("=" * 50)

        cache = LFUBlockCache(
            capacity=capacity,
            exclude_root_block=exclude_root
        )

        # Process the same requests in the same order
        for request in requests:
            cache.access(request)

        result = cache.get_results()

        # Save summary without nested dictionary
        summary_row = {
            key: value
            for key, value in result.items()
            if key != "hits_by_position"
        }

        summary_row["experiment"] = mode_name
        summary_results.append(summary_row)

        print("Requests:", result["requests"])
        print("Total blocks:", result["total_blocks"])
        print("Prefix hits:", result["prefix_hits"])

        print(
            "Prefix hit rate:",
            round(result["prefix_hit_rate"], 4),
            "%"
        )

        print("Root hits:", result["root_hits"])
        print("Deeper prefix hits:", result["deeper_hits"])
        print("Evictions:", result["evictions"])
        print("Final cache size:", result["final_cache_size"])

        print("\nHits by original prefix position:")

        for position, count in sorted(
            result["hits_by_position"].items()
        ):
            print(f"Position {position}: {count}")

            position_results.append({
                "experiment": mode_name,
                "policy": "LFU",
                "capacity": capacity,
                "prefix_position": position,
                "hits": count
            })


# Convert to DataFrames
summary_df = pd.DataFrame(summary_results)
position_df = pd.DataFrame(position_results)

# Save results in the existing results folder
output_dir = Path(__file__).parent / "results"
output_dir.mkdir(exist_ok=True)

summary_path = output_dir / "lfu_sensitivity_results.csv"
position_path = output_dir / "lfu_sensitivity_by_position.csv"

summary_df.to_csv(summary_path, index=False)
position_df.to_csv(position_path, index=False)


# Display final comparison
print("\n")
print("#" * 65)
print("FINAL LFU SENSITIVITY COMPARISON")
print("#" * 65)

columns = [
    "experiment",
    "capacity",
    "total_blocks",
    "prefix_hits",
    "prefix_hit_rate",
    "root_hits",
    "deeper_hits",
    "evictions"
]

print(summary_df[columns].to_string(index=False))

print("\nFiles saved successfully:")
print(summary_path)
print(position_path)

print("\nBoth LFU sensitivity experiments completed.")
