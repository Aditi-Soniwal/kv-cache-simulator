
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Locate results folder
BASE_DIR = Path(__file__).parent
RESULTS_DIR = BASE_DIR / "results"

# Load Adaptive experiment results
csv_path = RESULTS_DIR / "adaptive_sensitivity_results.csv"
df = pd.read_csv(csv_path)

# Separate experiment modes
full_prefix = df[
    df["experiment"] == "full_prefix"
].sort_values("capacity")

root_excluded = df[
    df["experiment"] == "root_excluded"
].sort_values("capacity")

# Create graph
plt.figure(figsize=(12, 7))

plt.plot(
    full_prefix["capacity"],
    full_prefix["prefix_hit_rate"],
    marker="o",
    linewidth=2.5,
    markersize=8,
    label="Full Prefix"
)

plt.plot(
    root_excluded["capacity"],
    root_excluded["prefix_hit_rate"],
    marker="s",
    linewidth=2.5,
    markersize=8,
    label="Root Excluded"
)

# Add percentage labels
for _, row in full_prefix.iterrows():
    plt.annotate(
        f'{row["prefix_hit_rate"]:.2f}%',
        (row["capacity"], row["prefix_hit_rate"]),
        xytext=(0, 10),
        textcoords="offset points",
        ha="center"
    )

for _, row in root_excluded.iterrows():
    plt.annotate(
        f'{row["prefix_hit_rate"]:.2f}%',
        (row["capacity"], row["prefix_hit_rate"]),
        xytext=(0, -18),
        textcoords="offset points",
        ha="center"
    )

# Graph formatting
plt.title(
    "Adaptive Hit Rate Across Cache Capacities on Mooncake Trace"
)
plt.xlabel("Cache Capacity (Blocks)")
plt.ylabel("Prefix Hit Rate (%)")

plt.xticks([256, 512, 1024, 2048, 4096])
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()

# Save graph
output_path = (
    RESULTS_DIR / "adaptive_sensitivity_hit_rate.png"
)

plt.savefig(
    output_path,
    dpi=300,
    bbox_inches="tight"
)

plt.show()

print("\nAdaptive graph saved successfully:")
print(output_path)
