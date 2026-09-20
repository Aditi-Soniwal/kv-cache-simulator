
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# Overall hit-rate results from all six workloads (%)
data = {
    "Workload": [
        "Sudden Shift",
        "Stable Reuse",
        "Gradual Shift",
        "Repeated Shifts",
        "Low Reuse",
        "High Cache Pressure"
    ],
    "LRU": [57.09, 57.65, 63.63, 60.65, 0.31, 10.01],
    "LFU": [40.77, 76.70, 49.52, 48.82, 0.39, 10.10],
    "Static TTL": [57.09, 57.65, 63.62, 60.65, 0.31, 10.01],
    "Adaptive": [72.74, 75.72, 69.00, 68.43, 0.42, 10.01]
}

df = pd.DataFrame(data)

# Plot settings
workloads = df["Workload"]
policies = ["LRU", "LFU", "Static TTL", "Adaptive"]

x = np.arange(len(workloads))
width = 0.2

plt.figure(figsize=(14, 7))

for i, policy in enumerate(policies):
    plt.bar(
        x + (i - 1.5) * width,
        df[policy],
        width,
        label=policy
    )

# Labels and title
plt.xlabel("Workload")
plt.ylabel("Overall Hit Rate (%)")
plt.title("Overall Hit Rate by Policy Across Six Synthetic Workloads")

plt.xticks(x, workloads, rotation=20, ha="right")
plt.ylim(0, 100)

plt.legend(title="Cache Policy")
plt.grid(axis="y", linestyle="--", alpha=0.3)

plt.tight_layout()

# Save figure
os.makedirs("results", exist_ok=True)

plt.savefig(
    "results/figure2_all_workloads.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()

print("Figure 2 generated successfully!")