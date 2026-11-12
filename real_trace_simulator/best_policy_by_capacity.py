
import pandas as pd
from pathlib import Path

# Load consolidated results
BASE_DIR = Path(__file__).parent
RESULTS_DIR = BASE_DIR / "results"

input_file = RESULTS_DIR / "all_policies_combined_results.csv"

df = pd.read_csv(input_file)

# Find the best policy for every capacity and experiment
best_results = []

for experiment in ["full_prefix", "root_excluded"]:

    experiment_df = df[
        df["experiment"] == experiment
    ]

    for capacity in sorted(experiment_df["capacity"].unique()):

        capacity_df = experiment_df[
            experiment_df["capacity"] == capacity
        ]

        best = capacity_df.loc[
            capacity_df["prefix_hit_rate"].idxmax()
        ]

        best_results.append({
            "experiment": experiment,
            "capacity": capacity,
            "best_policy": best["policy"],
            "best_hit_rate": round(
                best["prefix_hit_rate"], 4
            )
        })

# Create final table
best_df = pd.DataFrame(best_results)

# Save CSV
output_file = RESULTS_DIR / "best_policy_by_capacity.csv"

best_df.to_csv(output_file, index=False)

print("\nBEST POLICY BY CACHE CAPACITY")
print("=" * 60)

print(best_df.to_string(index=False))

print("\nFile saved successfully:")
print(output_file)
