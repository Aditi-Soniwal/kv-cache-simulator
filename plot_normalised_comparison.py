
import matplotlib.pyplot as plt
import numpy as np

policies = ["LRU", "LFU", "Adaptive", "Static TTL"]

synthetic = [41.556667, 37.716667, 49.386667, 41.555]
full_prefix = [5.419965, 5.699411, 5.431958, 4.813934]
root_excluded = [1.306403, 1.596128, 1.316965, 0.674]

# Normalise each dataset independently.
def normalise(values):
    best = max(values)
    return [value / best * 100 for value in values]

synthetic_norm = normalise(synthetic)
full_norm = normalise(full_prefix)
root_norm = normalise(root_excluded)

x = np.arange(len(policies))
width = 0.25

plt.figure(figsize=(12, 7))

plt.bar(x - width, synthetic_norm, width, label="Synthetic")
plt.bar(x, full_norm, width, label="Mooncake Full Prefix")
plt.bar(x + width, root_norm, width, label="Mooncake Root Excluded")

plt.title(
    "Normalised Performance Comparison of KV-Cache Policies",
    fontsize=16,
    fontweight="bold"
)

plt.xlabel("Cache Retention Policy")
plt.ylabel("Normalised Hit Rate Index (Best = 100)")
plt.xticks(x, policies)
plt.ylim(0, 110)
plt.legend()
plt.grid(axis="y", linestyle="--", alpha=0.4)

plt.tight_layout()

plt.savefig(
    "results/normalised_synthetic_vs_mooncake.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()

print("Normalised comparison graph saved successfully!")
