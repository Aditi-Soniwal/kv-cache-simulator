
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# --------------------------------------------------
# PATHS
# --------------------------------------------------

BASE_DIR = Path(__file__).parent
RESULTS_DIR = BASE_DIR / "results"
RESULTS_DIR.mkdir(exist_ok=True)

FILES = {
    "LRU": "lru_sensitivity_results.csv",
    "LFU": "lfu_sensitivity_results.csv",
    "Static TTL": "static_ttl_sensitivity_results.csv",
    "Adaptive": "adaptive_sensitivity_results.csv"
}

POLICY_DATA = []

# --------------------------------------------------
# LOAD RESULTS FROM ALL FOUR POLICIES
# --------------------------------------------------

for policy, filename in FILES.items():

    file_path = RESULTS_DIR / filename

    if not file_path.exists():
        raise FileNotFoundError(
            f"Missing result file: {file_path}"
        )

    df = pd.read_csv(file_path)

    # Standardise policy names
    df["policy"] = policy

    # Identify experiment mode
    if "experiment" in df.columns:

        df["experiment"] = df["experiment"].astype(str)

    elif "exclude_root_block" in df.columns:

        df["experiment"] = df[
            "exclude_root_block"
        ].apply(
            lambda x: (
                "root_excluded"
                if str(x).strip().lower() in
                ["true", "1", "yes"]
                else "full_prefix"
            )
        )

    else:
        raise ValueError(
            f"Cannot identify experiment mode in {filename}"
        )

    POLICY_DATA.append(df)

# Combine all policies
combined = pd.concat(
    POLICY_DATA,
    ignore_index=True
)

# Standardise data types
combined["capacity"] = pd.to_numeric(
    combined["capacity"]
)

combined["prefix_hit_rate"] = pd.to_numeric(
    combined["prefix_hit_rate"]
)

# Sort results
combined = combined.sort_values(
    ["experiment", "capacity", "policy"]
)

# --------------------------------------------------
# SAVE CONSOLIDATED CSV
# --------------------------------------------------

combined_path = (
    RESULTS_DIR / "all_policies_combined_results.csv"
)

combined.to_csv(
    combined_path,
    index=False
)

print("\nCONSOLIDATED RESULTS")
print("=" * 75)

display_columns = [
    "experiment",
    "policy",
    "capacity",
    "prefix_hit_rate",
    "evictions"
]

print(
    combined[display_columns].to_string(
        index=False
    )
)

# --------------------------------------------------
# CREATE COMPARISON GRAPHS
# --------------------------------------------------

capacities = sorted(
    combined["capacity"].unique()
)

policies = [
    "LRU",
    "LFU",
    "Static TTL",
    "Adaptive"
]

experiment_modes = [
    ("full_prefix", "Full Prefix"),
    ("root_excluded", "Root Excluded")
]

fig, axes = plt.subplots(
    1,
    2,
    figsize=(16, 6)
)

for ax, (mode, title) in zip(
    axes,
    experiment_modes
):

    mode_data = combined[
        combined["experiment"] == mode
    ]

    for policy in policies:

        policy_data = mode_data[
            mode_data["policy"] == policy
        ].sort_values("capacity")

        if policy_data.empty:
            continue

        ax.plot(
            policy_data["capacity"],
            policy_data["prefix_hit_rate"],
            marker="o",
            linewidth=2,
            markersize=7,
            label=policy
        )

    ax.set_title(title, fontsize=14)
    ax.set_xlabel("Cache Capacity (Blocks)")
    ax.set_ylabel("Prefix Hit Rate (%)")
    ax.set_xticks(capacities)
    ax.grid(True, alpha=0.3)
    ax.legend()

fig.suptitle(
    "Comparison of Cache Policies on Mooncake Trace",
    fontsize=17
)

plt.tight_layout()

graph_path = (
    RESULTS_DIR / "all_policies_comparison.png"
)

plt.savefig(
    graph_path,
    dpi=300,
    bbox_inches="tight"
)

plt.show()

# --------------------------------------------------
# FIND BEST POLICY AT EACH CAPACITY
# --------------------------------------------------

best_rows = []

for mode in combined["experiment"].unique():

    mode_data = combined[
        combined["experiment"] == mode
    ]

    for capacity in capacities:

        capacity_data = mode_data[
            mode_data["capacity"] == capacity
        ]

        if capacity_data.empty:
            continue

        best = capacity_data.loc[
            capacity_data["prefix_hit_rate"].idxmax()
        ]

        best_rows.append({
            "experiment": mode,
            "capacity": capacity,
            "best_policy": best["policy"],
            "best_hit_rate": best["prefix_hit_rate"]
        })

best_df = pd.DataFrame(best_rows)

best_path = (
    RESULTS_DIR / "best_policy_by_capacity.csv"
)

best_df.to_csv(
    best_path,
    index=False
)

print("\nBEST POLICY AT EACH CAPACITY")
print("=" * 75)

print(
    best_df.to_string(index=False)
)

# --------------------------------------------------
# FINAL FILE LOCATIONS
# --------------------------------------------------

print("\nALL FILES SAVED SUCCESSFULLY")
print("=" * 75)

print("Combined CSV:", combined_path)
print("Comparison Graph:", graph_path)
print("Best Policy CSV:", best_path)
