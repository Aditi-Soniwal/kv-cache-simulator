
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import numpy as np

# Input files
synthetic_file = Path("results/all_workload_results.csv")
real_file = Path(
    "real_trace_simulator/results/all_policies_combined_results.csv"
)

# Output folder
output_folder = Path("results")
output_folder.mkdir(exist_ok=True)

# Load data
synthetic = pd.read_csv(synthetic_file)
real = pd.read_csv(real_file)

synthetic.columns = synthetic.columns.str.strip()
real.columns = real.columns.str.strip()

# Policy and workload order
policies = ["LRU", "LFU", "Static-TTL", "Adaptive"]

workloads = [
    "Sudden Shift",
    "Stable Reuse",
    "Gradual Shift",
    "Repeated Shifts",
    "Low Reuse",
    "High Cache Pressure"
]

# Convert synthetic hit rate to percentage
synthetic["hit_rate_percent"] = synthetic["hit_rate"] * 100

# Mooncake prefix hit rate is already a percentage
real["hit_rate_percent"] = real["prefix_hit_rate"]

# -------------------------------------------------
# GRAPH 1: Synthetic workload comparison
# -------------------------------------------------

synthetic_pivot = synthetic.pivot_table(
    index="workload",
    columns="policy",
    values="hit_rate_percent",
    aggfunc="mean"
)

synthetic_pivot = synthetic_pivot.reindex(
    index=workloads,
    columns=policies
)

ax = synthetic_pivot.plot(
    kind="bar",
    figsize=(12, 6),
    width=0.8
)

ax.set_title(
    "Synthetic Workload Performance: KV-Cache Policies",
    fontsize=14,
    fontweight="bold"
)
ax.set_xlabel("Workload")
ax.set_ylabel("Hit Rate (%)")
ax.set_ylim(bottom=0)
ax.grid(axis="y", linestyle="--", alpha=0.4)
ax.legend(title="Policy")
plt.xticks(rotation=25, ha="right")
plt.tight_layout()

plt.savefig(
    output_folder / "synthetic_workload_comparison.png",
    dpi=300,
    bbox_inches="tight"
)
plt.close()

# -------------------------------------------------
# GRAPH 2: Mooncake Full Prefix capacity comparison
# -------------------------------------------------

full_prefix = real[real["exclude_root_block"] == False]

full_pivot = full_prefix.pivot_table(
    index="capacity",
    columns="policy",
    values="hit_rate_percent",
    aggfunc="mean"
)

full_pivot = full_pivot.reindex(columns=policies)

ax = full_pivot.plot(
    kind="line",
    marker="o",
    linewidth=2,
    figsize=(10, 6)
)

ax.set_title(
    "Mooncake Full Prefix: Hit Rate vs Cache Capacity",
    fontsize=14,
    fontweight="bold"
)
ax.set_xlabel("Cache Capacity (Blocks)")
ax.set_ylabel("Prefix Hit Rate (%)")
ax.set_xticks(full_pivot.index)
ax.grid(True, linestyle="--", alpha=0.4)
ax.legend(title="Policy")
plt.tight_layout()

plt.savefig(
    output_folder / "mooncake_full_prefix_comparison.png",
    dpi=300,
    bbox_inches="tight"
)
plt.close()

# -------------------------------------------------
# GRAPH 3: Mooncake Root Excluded capacity comparison
# -------------------------------------------------

root_excluded = real[real["exclude_root_block"] == True]

root_pivot = root_excluded.pivot_table(
    index="capacity",
    columns="policy",
    values="hit_rate_percent",
    aggfunc="mean"
)

root_pivot = root_pivot.reindex(columns=policies)

ax = root_pivot.plot(
    kind="line",
    marker="o",
    linewidth=2,
    figsize=(10, 6)
)

ax.set_title(
    "Mooncake Root Excluded: Hit Rate vs Cache Capacity",
    fontsize=14,
    fontweight="bold"
)
ax.set_xlabel("Cache Capacity (Blocks)")
ax.set_ylabel("Prefix Hit Rate (%)")
ax.set_xticks(root_pivot.index)
ax.grid(True, linestyle="--", alpha=0.4)
ax.legend(title="Policy")
plt.tight_layout()

plt.savefig(
    output_folder / "mooncake_root_excluded_comparison.png",
    dpi=300,
    bbox_inches="tight"
)
plt.close()

print("\nTHREE RESEARCH GRAPHS GENERATED SUCCESSFULLY!")

print("\nSaved files:")
print("1. synthetic_workload_comparison.png")
print("2. mooncake_full_prefix_comparison.png")
print("3. mooncake_root_excluded_comparison.png")

print("\nAll graphs are saved in the results folder.")
