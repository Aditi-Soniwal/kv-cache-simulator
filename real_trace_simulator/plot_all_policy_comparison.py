
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

BASE_DIR = Path(__file__).parent
RESULTS_DIR = BASE_DIR / "results"

# CSV files for all four policies
files = {
    "LRU": "lru_sensitivity_results.csv",
    "LFU": "lfu_sensitivity_results.csv",
    "Static TTL": "static_ttl_sensitivity_results.csv",
    "Adaptive": "adaptive_sensitivity_results.csv"
}

data = {}

for policy, filename in files.items():
    path = RESULTS_DIR / filename

    if not path.exists():
        raise FileNotFoundError(f"Missing file: {path}")

    df = pd.read_csv(path)

    required = {"experiment", "capacity", "prefix_hit_rate"}
    if not required.issubset(df.columns):
        raise ValueError(
            f"{filename} must contain: {required}"
        )

    data[policy] = df

capacities = [256, 512, 1024, 2048, 4096]

# Create two comparison panels
fig, axes = plt.subplots(1, 2, figsize=(16, 6))

modes = [
    ("full_prefix", "Full Prefix"),
    ("root_excluded", "Root Excluded")
]

for ax, (mode, title) in zip(axes, modes):

    for policy, df in data.items():

        subset = df[df["experiment"] == mode].sort_values(
            "capacity"
        )

        ax.plot(
            subset["capacity"],
            subset["prefix_hit_rate"],
            marker="o",
            linewidth=2,
            markersize=6,
            label=policy
        )

    ax.set_title(title)
    ax.set_xlabel("Cache Capacity (Blocks)")
    ax.set_ylabel("Prefix Hit Rate (%)")
    ax.set_xticks(capacities)
    ax.grid(True, alpha=0.3)
    ax.legend()

fig.suptitle(
    "Comparison of Cache Policies on Mooncake Trace",
    fontsize=16
)

plt.tight_layout()

output_path = RESULTS_DIR / "all_policy_comparison.png"

plt.savefig(
    output_path,
    dpi=300,
    bbox_inches="tight"
)

plt.show()

print("\nCombined comparison graph saved:")
print(output_path)
