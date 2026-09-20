
import pandas as pd
import matplotlib.pyplot as plt
import os

# Hit-rate results (%) for all six workloads
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

# Calculate average hit rate for each policy
policies = ["LRU", "LFU", "Static TTL", "Adaptive"]
average_hit_rates = df[policies].mean()

# Create a bar chart with only four bars
plt.figure(figsize=(9, 6))

bars = plt.bar(
    policies,
    average_hit_rates,
    width=0.6
)

# Display values above the bars
for bar in bars:
    height = bar.get_height()
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        height + 0.5,
        f"{height:.2f}%",
        ha="center",
        fontsize=11
    )

plt.title("Overall Hit Rate by Policy Across Six Synthetic Workloads")
plt.xlabel("Cache Policy")
plt.ylabel("Average Hit Rate (%)")
plt.ylim(0, 60)

plt.tight_layout()

# Save the graph
os.makedirs("results", exist_ok=True)
plt.savefig(
    "results/figure2_policy_wise_hit_rate.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()

print("\nAverage Hit Rate by Policy:")
print(average_hit_rates.round(2))