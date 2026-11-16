
import matplotlib.pyplot as plt
import numpy as np

policies = ["LRU", "LFU", "Adaptive", "Static TTL"]

synthetic = [41.556667, 37.716667, 49.386667, 41.555]
full_prefix = [5.419965, 5.699411, 5.431958, 4.813934]
root_excluded = [1.306403, 1.596128, 1.316965, 0.674000]

x = np.arange(len(policies))
width = 0.25

plt.figure(figsize=(12, 7))

plt.bar(x - width, synthetic, width,
        label="Synthetic Workloads")

plt.bar(x, full_prefix, width,
        label="Mooncake Full Prefix")

plt.bar(x + width, root_excluded, width,
        label="Mooncake Root Excluded")

plt.title(
    "Synthetic vs Real-Trace Performance of KV-Cache Policies",
    fontsize=16,
    fontweight="bold"
)

plt.xlabel("Cache Retention Policy", fontsize=12)
plt.ylabel("Average Hit Rate (%)", fontsize=12)

plt.xticks(x, policies)
plt.legend()
plt.grid(axis="y", linestyle="--", alpha=0.4)

plt.tight_layout()

plt.savefig(
    "results/synthetic_vs_mooncake_comparison.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()
