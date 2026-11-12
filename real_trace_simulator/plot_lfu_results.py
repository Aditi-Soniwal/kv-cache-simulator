
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

BASE_DIR = Path(__file__).parent
RESULTS_DIR = BASE_DIR / "results"

csv_path = RESULTS_DIR / "lfu_sensitivity_results.csv"
df = pd.read_csv(csv_path)

full = df[df["experiment"] == "full_prefix"].sort_values("capacity")
excluded = df[df["experiment"] == "root_excluded"].sort_values("capacity")

# GRAPH 1: LFU HIT RATE
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

plt.title("LFU Hit Rate Across Cache Capacities on Mooncake Trace")
plt.xlabel("Cache Capacity (Blocks)")
plt.ylabel("Prefix Hit Rate (%)")
plt.xticks(full["capacity"])
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()

plt.savefig(
    RESULTS_DIR / "lfu_sensitivity_hit_rate.png",
    dpi=300,
    bbox_inches="tight"
)
plt.show()


# GRAPH 2: LFU DEEPER PREFIX HITS
plt.figure(figsize=(10, 6))

plt.plot(
    full["capacity"],
    full["deeper_hits"],
    marker="o",
    linewidth=2,
    label="Full Prefix"
)

plt.plot(
    excluded["capacity"],
    excluded["deeper_hits"],
    marker="s",
    linewidth=2,
    label="Root Excluded"
)

plt.title("LFU Deeper Prefix Hits Across Cache Capacities")
plt.xlabel("Cache Capacity (Blocks)")
plt.ylabel("Deeper Prefix Hits")
plt.xticks(full["capacity"])
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()

plt.savefig(
    RESULTS_DIR / "lfu_deeper_prefix_hits.png",
    dpi=300,
    bbox_inches="tight"
)
plt.show()

print("\nLFU graphs generated successfully!")
print("Saved: lfu_sensitivity_hit_rate.png")
print("Saved: lfu_deeper_prefix_hits.png")
