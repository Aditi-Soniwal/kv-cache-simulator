
import pandas as pd
from pathlib import Path

# Input files
synthetic_file = Path("results/all_workload_results.csv")
real_file = Path(
    "real_trace_simulator/results/all_policies_combined_results.csv"
)

# Output folder
output_folder = Path("results")
output_folder.mkdir(exist_ok=True)

# Load datasets
synthetic = pd.read_csv(synthetic_file)
real = pd.read_csv(real_file)

# Clean column names
synthetic.columns = synthetic.columns.str.strip()
real.columns = real.columns.str.strip()

# Convert synthetic hit rate from fraction to percentage
synthetic["Hit_Rate_Percent"] = synthetic["hit_rate"] * 100

# Mooncake prefix_hit_rate is already expressed as a percentage
real["Hit_Rate_Percent"] = real["prefix_hit_rate"]

# Synthetic capacity-wise analysis
synthetic_summary = (
    synthetic.groupby(
        ["capacity", "workload", "policy"]
    )["Hit_Rate_Percent"]
    .mean()
    .reset_index()
)

synthetic_summary["Dataset"] = "Synthetic"
synthetic_summary["Capacity_Unit"] = "Cache Entries"
synthetic_summary = synthetic_summary.rename(columns={
    "capacity": "Capacity",
    "workload": "Condition",
    "policy": "Policy"
})

# Real Mooncake capacity-wise analysis
real["Experiment"] = real["exclude_root_block"].map({
    False: "Full Prefix",
    True: "Root Excluded"
})

real_summary = (
    real.groupby(
        ["capacity", "Experiment", "policy"]
    )["Hit_Rate_Percent"]
    .mean()
    .reset_index()
)

real_summary["Dataset"] = "Mooncake"
real_summary["Capacity_Unit"] = "Blocks"
real_summary = real_summary.rename(columns={
    "capacity": "Capacity",
    "Experiment": "Condition",
    "policy": "Policy"
})

# Save separate summaries
synthetic_summary.to_csv(
    output_folder / "synthetic_capacity_comparison.csv",
    index=False
)

real_summary.to_csv(
    output_folder / "mooncake_capacity_comparison.csv",
    index=False
)

# Save combined descriptive comparison
combined = pd.concat(
    [synthetic_summary, real_summary],
    ignore_index=True
)

combined = combined[
    [
        "Dataset",
        "Capacity_Unit",
        "Capacity",
        "Condition",
        "Policy",
        "Hit_Rate_Percent"
    ]
]

combined.to_csv(
    output_folder / "capacity_wise_comparison.csv",
    index=False
)

print("\nSYNTHETIC CAPACITY-WISE RESULTS")
print(synthetic_summary.to_string(index=False))

print("\nMOONCAKE CAPACITY-WISE RESULTS")
print(real_summary.to_string(index=False))

print("\nAll comparison files saved successfully!")
