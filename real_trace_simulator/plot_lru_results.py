
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Locate results folder
BASE_DIR = Path(__file__).parent
RESULTS_DIR = BASE_DIR / "results"

# Read LRU sensitivity results
csv_path = RESULTS_DIR / "lru_sensitivity_results.csv"
df = pd.read_csv(csv_path)

# Separate the two experiments
full = df[df["experiment"] == "full_prefix"].sort_values("capacity")
excluded = df[df["experiment"] == "root_excluded"].sort_values("capacity")

# ==========================================
# GRAPH 1: HIT RATE COMPARISON
# ==========================================

plt.figure(figsize=(10, 6))

plt.plot(
    full["capacity"],
    full["prefix_hit_rate"],
    marker="o",
    linewidth=2,
    label="Full Prefix"
)

plt.plot(
    excluded["capacity"],
    excluded["prefix_hit_rate"],
    marker="s",
    linewidth=2,
    label="Root Excluded"
)

# Add values above points
for _, row in full.iterrows():
    plt.annotate(
        f'{row["prefix_hit_rate"]:.2f}%',
        (row["capacity"], row["prefix_hit_rate"]),
        xytext=(0, 9),
        textcoords="offset points",
        ha="center"
    )

for _, row in excluded.iterrows():
    plt.annotate(
        f'{row["prefix_hit_rate"]:.2f}%',
        (row["capacity"], row["prefix_hit_rate"]),
        xytext=(0, -15),
        textcoords="offset points",
        ha="center"
    )

plt.title("LRU Hit Rate Across Cache Capacities on Mooncake Trace")
plt.xlabel("Cache Capacity (Blocks)")
plt.ylabel("Prefix Hit Rate (%)")
plt.xticks(full["capacity"])
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()

graph1_path = RESULTS_DIR / "lru_sensitivity_hit_rate.png"
plt.savefig(graph1_path, dpi=300, bbox_inches="tight")
plt.show()

# ==========================================
# GRAPH 2: DEEPER PREFIX HITS
# ==========================================

plt.figure(figsize=(10, 6))

plt.plot(
    full["capacity"],
    full["deeper_hits"],
    marker="o",
    linewidth=2,
    label="Full Prefix Experiment"
)

plt.plot(
    excluded["capacity"],
    excluded["deeper_hits"],
    marker="s",
    linewidth=2,
    label="Root Excluded Experiment"
)

plt.title("LRU Deeper Prefix Hits Across Cache Capacities")
plt.xlabel("Cache Capacity (Blocks)")
plt.ylabel("Deeper Prefix Hits")
plt.xticks(full["capacity"])
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()

graph2_path = RESULTS_DIR / "lru_deeper_prefix_hits.png"
plt.savefig(graph2_path, dpi=300, bbox_inches="tight")
plt.show()

print("\n========== GRAPHS GENERATED ==========")
print("Saved:", graph1_path)
print("Saved:", graph2_path)
