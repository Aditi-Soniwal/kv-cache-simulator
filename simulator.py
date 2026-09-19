import os
import pandas as pd
import matplotlib.pyplot as plt
from metrics import summarize;

from policies import LRUCache, LFUCache, StaticTTLCache, AdaptiveCache

from workload import (
    generate_shift_trace,
    generate_stable_trace,
    generate_gradual_shift_trace,
    generate_repeated_shift_trace,
    generate_low_reuse_trace,
    generate_high_cache_pressure_trace
)

RESULTS = "results"
os.makedirs(RESULTS, exist_ok=True)


# --------------------------------------------------
# EXPERIMENT SETTINGS
# --------------------------------------------------

CAPACITY = 20
NUM_KEYS = 200
TOTAL_REQUESTS = 10000
BEFORE = 5000
AFTER = 5000
CHANGE = BEFORE

RESULTS = "results"
os.makedirs(RESULTS, exist_ok=True)


# --------------------------------------------------
# DEFINE WORKLOADS
# --------------------------------------------------

WORKLOADS = {
    "Sudden Shift": lambda: generate_shift_trace(
        BEFORE, AFTER, num_keys=NUM_KEYS, seed=42
    ),

    "Stable Reuse": lambda: generate_stable_trace(
        length=TOTAL_REQUESTS, num_keys=NUM_KEYS, seed=42
    ),

    "Gradual Shift": lambda: generate_gradual_shift_trace(
        length=TOTAL_REQUESTS, num_keys=NUM_KEYS, seed=42
    ),

    "Repeated Shifts": lambda: generate_repeated_shift_trace(
        length=TOTAL_REQUESTS, num_keys=NUM_KEYS, seed=42
    ),

    "Low Reuse": lambda: generate_low_reuse_trace(
        length=TOTAL_REQUESTS, num_keys=5000, seed=42
    ),

    "High Cache Pressure": lambda: generate_high_cache_pressure_trace(
        length=TOTAL_REQUESTS, num_keys=NUM_KEYS, seed=42
    )
}


# Actual transition points for workloads with designed changes.
# For other workloads, use None.
CHANGE_POINTS = {
    "Sudden Shift": 5000,
    "Stable Reuse": None,
    "Gradual Shift": 3000,
    "Repeated Shifts": 2000,
    "Low Reuse": None,
    "High Cache Pressure": None
}


# --------------------------------------------------
# RUN EXPERIMENTS
# --------------------------------------------------

all_results = []

for workload_name, generator in WORKLOADS.items():

    print("\n======================================")
    print("WORKLOAD:", workload_name)
    print("======================================")

    trace = generator()
    change_point = CHANGE_POINTS[workload_name]

    policies = {
        "LRU": LRUCache(CAPACITY),
        "LFU": LFUCache(CAPACITY),
        "Static-TTL": StaticTTLCache(CAPACITY, 100),
        "Adaptive": AdaptiveCache(CAPACITY, 100)
    }

    for policy_name, cache in policies.items():

        history = []

        for t, key in enumerate(trace):
            hit = cache.access(key, t)
            history.append(1 if hit else 0)

        # For workloads without a designed transition,
        # use midpoint only for reporting pre/post metrics.
        metric_change = (
            change_point
            if change_point is not None
            else len(history) // 2
        )

        result = summarize(
            history,
            cache.evictions,
            CAPACITY,
            metric_change
        )

        result["workload"] = workload_name
        result["policy"] = policy_name
        result["designed_change_point"] = change_point

        if change_point is None:
            result["change_note"] = (
                "No designed transition; midpoint is a reporting split only"
            )
        else:
            result["change_note"] = "Designed workload transition"

        all_results.append(result)

        print(
            policy_name,
            "| Hit Rate:",
            round(result["hit_rate"] * 100, 2),
            "%"
        )


# --------------------------------------------------
# SAVE RESULTS
# --------------------------------------------------

df = pd.DataFrame(all_results)

df.to_csv(
    f"{RESULTS}/all_workload_results.csv",
    index=False
)

print("\n======================================")
print("FINAL RESULTS")
print("======================================\n")

print(
    df[
        [
            "workload",
            "policy",
            "hit_rate",
            "pre_change_hit_rate",
            "post_change_hit_rate",
            "hit_rate_drop",
            "recovery_time_requests",
            "evictions",
            "change_note"
        ]
    ].to_string(index=False)
)


# --------------------------------------------------
# GRAPH 1: OVERALL HIT RATE
# --------------------------------------------------

pivot = df.pivot(
    index="workload",
    columns="policy",
    values="hit_rate"
)

pivot.plot(
    kind="bar",
    figsize=(12, 6)
)

plt.ylabel("Overall Hit Rate")
plt.xlabel("Workload")
plt.title("KV-Cache Hit Rate Across Workloads")
plt.xticks(rotation=25, ha="right")
plt.legend(title="Policy")
plt.tight_layout()

plt.savefig(
    f"{RESULTS}/all_workload_hit_rate.png",
    dpi=160
)

plt.close()


# --------------------------------------------------
# GRAPH 2: HIT-RATE DROP
# Only meaningful for designed transitions
# --------------------------------------------------

shift_df = df[
    df["designed_change_point"].notna()
]

pivot_drop = shift_df.pivot(
    index="workload",
    columns="policy",
    values="hit_rate_drop"
)

pivot_drop.plot(
    kind="bar",
    figsize=(10, 6)
)

plt.ylabel("Hit-Rate Drop")
plt.xlabel("Workload")
plt.title("Hit-Rate Drop for Workloads with Designed Changes")
plt.xticks(rotation=20, ha="right")
plt.legend(title="Policy")
plt.tight_layout()

plt.savefig(
    f"{RESULTS}/shift_workload_hit_rate_drop.png",
    dpi=160
)

plt.close()


print("\nCSV and graphs saved inside the results folder.")