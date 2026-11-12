
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# ==========================================
# 1. PATHS AND SETTINGS
# ==========================================

BASE_DIR = Path(__file__).parent
RESULTS_DIR = BASE_DIR / "results"

INPUT_FILE = RESULTS_DIR / "all_policies_combined_results.csv"

OUTPUT_DIR = RESULTS_DIR
OUTPUT_DIR.mkdir(exist_ok=True)

POLICIES = ["LRU", "LFU", "Static TTL", "Adaptive"]

# ==========================================
# 2. LOAD AND VALIDATE DATA
# ==========================================

df = pd.read_csv(INPUT_FILE)

required_columns = [
    "experiment",
    "policy",
    "capacity",
    "prefix_hit_rate",
    "prefix_hits"
]

missing = [
    col for col in required_columns
    if col not in df.columns
]

if missing:
    raise ValueError(f"Missing columns: {missing}")

df["capacity"] = pd.to_numeric(df["capacity"])
df["prefix_hit_rate"] = pd.to_numeric(
    df["prefix_hit_rate"]
)

df["prefix_hits"] = pd.to_numeric(df["prefix_hits"])

df = df.sort_values(
    ["experiment", "capacity", "policy"]
)

print("\nDATA VALIDATION")
print("=" * 65)

print("Total rows:", len(df))
print("Policies:", sorted(df["policy"].unique()))
print("Capacities:", sorted(df["capacity"].unique()))
print("Experiment modes:", sorted(df["experiment"].unique()))

# ==========================================
# 3. IMPROVEMENT OVER LRU
# ==========================================

improvement_rows = []

for mode in df["experiment"].unique():

    mode_df = df[df["experiment"] == mode]

    for capacity in sorted(mode_df["capacity"].unique()):

        capacity_df = mode_df[
            mode_df["capacity"] == capacity
        ]

        lru_row = capacity_df[
            capacity_df["policy"] == "LRU"
        ]

        if lru_row.empty:
            continue

        lru_rate = lru_row.iloc[0]["prefix_hit_rate"]

        for _, row in capacity_df.iterrows():

            difference = (
                row["prefix_hit_rate"] - lru_rate
            )

            relative_improvement = (
                difference / lru_rate * 100
                if lru_rate != 0 else 0
            )

            improvement_rows.append({
                "experiment": mode,
                "capacity": capacity,
                "policy": row["policy"],
                "hit_rate": row["prefix_hit_rate"],
                "lru_hit_rate": lru_rate,
                "difference_percentage_points": difference,
                "relative_improvement_percent":
                    relative_improvement
            })

improvement_df = pd.DataFrame(improvement_rows)

improvement_df.to_csv(
    OUTPUT_DIR / "policy_improvement_over_lru.csv",
    index=False
)

print("\nPOLICY IMPROVEMENT OVER LRU")
print("=" * 65)

print(
    improvement_df[
        improvement_df["policy"] != "LRU"
    ].round(4).to_string(index=False)
)

# ==========================================
# 4. BEST POLICY AT EACH CAPACITY
# ==========================================

best_rows = []

for mode in df["experiment"].unique():

    mode_df = df[df["experiment"] == mode]

    for capacity in sorted(mode_df["capacity"].unique()):

        capacity_df = mode_df[
            mode_df["capacity"] == capacity
        ]

        best = capacity_df.loc[
            capacity_df["prefix_hit_rate"].idxmax()
        ]

        best_rows.append({
            "experiment": mode,
            "capacity": capacity,
            "best_policy": best["policy"],
            "best_hit_rate": best["prefix_hit_rate"]
        })

best_df = pd.DataFrame(best_rows)

best_df.to_csv(
    OUTPUT_DIR / "final_best_policy_results.csv",
    index=False
)

print("\nBEST POLICY BY CAPACITY")
print("=" * 65)
print(best_df.round(4).to_string(index=False))

# ==========================================
# 5. CHANGE IN HIT RATE WITH CAPACITY
# ==========================================

capacity_rows = []

for mode in df["experiment"].unique():

    mode_df = df[df["experiment"] == mode]

    for policy in POLICIES:

        policy_df = mode_df[
            mode_df["policy"] == policy
        ].sort_values("capacity")

        if policy_df.empty:
            continue

        first = policy_df.iloc[0]
        last = policy_df.iloc[-1]

        capacity_rows.append({
            "experiment": mode,
            "policy": policy,
            "initial_capacity": first["capacity"],
            "initial_hit_rate": first["prefix_hit_rate"],
            "final_capacity": last["capacity"],
            "final_hit_rate": last["prefix_hit_rate"],
            "hit_rate_change_percentage_points":
                last["prefix_hit_rate"]
                - first["prefix_hit_rate"]
        })

capacity_df = pd.DataFrame(capacity_rows)

capacity_df.to_csv(
    OUTPUT_DIR / "capacity_scaling_analysis.csv",
    index=False
)

print("\nCAPACITY SCALING ANALYSIS")
print("=" * 65)
print(capacity_df.round(4).to_string(index=False))

# ==========================================
# 6. ROOT HIT SHARE ANALYSIS
# ==========================================

if "root_hits" in df.columns:

    root_df = df.copy()

    root_df["root_hit_share_percent"] = (
        root_df["root_hits"]
        / root_df["prefix_hits"].replace(0, pd.NA)
        * 100
    )

    root_df[
        [
            "experiment",
            "policy",
            "capacity",
            "root_hits",
            "prefix_hits",
            "root_hit_share_percent"
        ]
    ].to_csv(
        OUTPUT_DIR / "root_hit_share_analysis.csv",
        index=False
    )

    print("\nROOT HIT SHARE")
    print("=" * 65)

    print(
        root_df[
            root_df["experiment"] == "full_prefix"
        ][
            [
                "policy",
                "capacity",
                "root_hits",
                "prefix_hits",
                "root_hit_share_percent"
            ]
        ].round(4).to_string(index=False)
    )

else:
    print("\nRoot-hit analysis skipped: root_hits column missing.")

# ==========================================
# 7. STATIC TTL REMOVAL ANALYSIS
# ==========================================

ttl_file = OUTPUT_DIR / "static_ttl_sensitivity_results.csv"

if ttl_file.exists():

    ttl_df = pd.read_csv(ttl_file)

    ttl_df["total_removals"] = (
        ttl_df["expirations"] + ttl_df["evictions"]
    )

    ttl_df["expiration_share_percent"] = (
        ttl_df["expirations"]
        / ttl_df["total_removals"].replace(0, pd.NA)
        * 100
    )

    ttl_df["capacity_eviction_share_percent"] = (
        ttl_df["evictions"]
        / ttl_df["total_removals"].replace(0, pd.NA)
        * 100
    )

    ttl_df.to_csv(
        OUTPUT_DIR / "static_ttl_removal_analysis.csv",
        index=False
    )

    print("\nSTATIC TTL REMOVAL ANALYSIS")
    print("=" * 65)

    print(
        ttl_df[
            [
                "experiment",
                "capacity",
                "expirations",
                "evictions",
                "final_cache_size",
                "expiration_share_percent",
                "capacity_eviction_share_percent"
            ]
        ].round(2).to_string(index=False)
    )

# ==========================================
# 8. FINAL COMPARISON GRAPHS
# ==========================================

capacities = sorted(df["capacity"].unique())

fig, axes = plt.subplots(1, 2, figsize=(16, 6))

modes = [
    ("full_prefix", "Full Prefix"),
    ("root_excluded", "Root Excluded")
]

for ax, (mode, title) in zip(axes, modes):

    mode_df = df[df["experiment"] == mode]

    for policy in POLICIES:

        policy_df = mode_df[
            mode_df["policy"] == policy
        ].sort_values("capacity")

        if policy_df.empty:
            continue

        ax.plot(
            policy_df["capacity"],
            policy_df["prefix_hit_rate"],
            marker="o",
            linewidth=2,
            label=policy
        )

    ax.set_title(title)
    ax.set_xlabel("Cache Capacity (Blocks)")
    ax.set_ylabel("Prefix Hit Rate (%)")
    ax.set_xticks(capacities)
    ax.grid(True, alpha=0.3)
    ax.legend()

fig.suptitle(
    "Final Cache Policy Performance on Mooncake Trace",
    fontsize=16
)

plt.tight_layout()

plt.savefig(
    OUTPUT_DIR / "final_research_comparison.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()

print("\n==========================================")
print("FINAL RESEARCH ANALYSIS COMPLETED")
print("==========================================")

print("\nGenerated files:")

for filename in [
    "policy_improvement_over_lru.csv",
    "final_best_policy_results.csv",
    "capacity_scaling_analysis.csv",
    "root_hit_share_analysis.csv",
    "static_ttl_removal_analysis.csv",
    "final_research_comparison.png"
]:

    path = OUTPUT_DIR / filename

    if path.exists():
        print("Saved:", path.name)
