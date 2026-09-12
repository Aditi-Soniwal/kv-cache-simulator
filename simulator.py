import os
import pandas as pd
import matplotlib.pyplot as plt

from workload import generate_shift_trace
from policies import LRUCache, LFUCache, StaticTTLCache, AdaptiveCache
from metrics import summarize

RESULTS = "results"
os.makedirs(RESULTS, exist_ok=True)

# --------------------------------------------------
# EXPERIMENT SETTINGS
# --------------------------------------------------

SCENARIOS = {
    "Small Shift": {
        "capacity": 20,
        "num_keys": 200,
        "seed": 42
    },

    "Medium Shift": {
        "capacity": 30,
        "num_keys": 200,
        "seed": 43
    },

    "High Pressure": {
        "capacity": 10,
        "num_keys": 200,
        "seed": 44
    }
}

BEFORE = 5000
AFTER = 5000
CHANGE = BEFORE


# --------------------------------------------------
# RUN EXPERIMENTS
# --------------------------------------------------

all_results = []

for scenario_name, settings in SCENARIOS.items():

    print("\n======================================")
    print("SCENARIO:", scenario_name)
    print("======================================")

    capacity = settings["capacity"]
    num_keys = settings["num_keys"]
    seed = settings["seed"]

    trace = generate_shift_trace(
        BEFORE,
        AFTER,
        num_keys=num_keys,
        seed=seed
    )

    policies = {
        "LRU": LRUCache(capacity),
        "LFU": LFUCache(capacity),
        "Static-TTL": StaticTTLCache(capacity, 100),
        "Adaptive": AdaptiveCache(capacity, 100)
    }

    for policy_name, cache in policies.items():

        history = []

        for t, key in enumerate(trace):

            hit = cache.access(key, t)

            history.append(1 if hit else 0)

        result = summarize(
            history,
            cache.evictions,
            capacity,
            CHANGE
        )

        result["scenario"] = scenario_name
        result["policy"] = policy_name

        all_results.append(result)

        print(
            policy_name,
            "Hit Rate:",
            round(result["hit_rate"] * 100, 2),
            "%"
        )


# --------------------------------------------------
# SAVE ALL RESULTS
# --------------------------------------------------

df = pd.DataFrame(all_results)

df.to_csv(
    f"{RESULTS}/multi_scenario_results.csv",
    index=False
)

print("\n======================================")
print("FINAL RESULTS")
print("======================================\n")

print(
    df[
        [
            "scenario",
            "policy",
            "hit_rate",
            "pre_change_hit_rate",
            "post_change_hit_rate",
            "hit_rate_drop",
            "recovery_time_requests",
            "evictions"
        ]
    ].to_string(index=False)
)


# --------------------------------------------------
# GRAPH 1: HIT RATE BY SCENARIO
# --------------------------------------------------

pivot = df.pivot(
    index="scenario",
    columns="policy",
    values="hit_rate"
)

pivot.plot(
    kind="bar",
    figsize=(10, 6)
)

plt.ylabel("Hit Rate")
plt.xlabel("Workload Scenario")
plt.title("KV-Cache Hit Rate Across Workload Scenarios")
plt.xticks(rotation=0)
plt.legend(title="Policy")
plt.tight_layout()

plt.savefig(
    f"{RESULTS}/multi_scenario_hit_rate.png",
    dpi=160
)

plt.close()


# --------------------------------------------------
# GRAPH 2: HIT-RATE DROP
# --------------------------------------------------

pivot_drop = df.pivot(
    index="scenario",
    columns="policy",
    values="hit_rate_drop"
)

pivot_drop.plot(
    kind="bar",
    figsize=(10, 6)
)

plt.ylabel("Hit-Rate Drop")
plt.xlabel("Workload Scenario")
plt.title("Performance Degradation After Reuse-Pattern Change")
plt.xticks(rotation=0)
plt.legend(title="Policy")
plt.tight_layout()

plt.savefig(
    f"{RESULTS}/hit_rate_drop.png",
    dpi=160
)

plt.close()


print("\nGraphs and CSV saved inside the 'results' folder.")