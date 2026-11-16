
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

# Convert hit rates into percentages
synthetic["hit_rate_percent"] = synthetic["hit_rate"] * 100
real["prefix_hit_rate_percent"] = real["prefix_hit_rate"]

# Synthetic: average performance of each policy
synthetic_summary = (
    synthetic.groupby("policy")["hit_rate_percent"]
    .mean()
    .reset_index()
    .rename(columns={
        "policy": "Policy",
        "hit_rate_percent": "Synthetic_Average_Hit_Rate_Percent"
    })
)

# Real trace: separate Full Prefix and Root Excluded
real["Experiment"] = real["exclude_root_block"].map({
    False: "Full Prefix",
    True: "Root Excluded"
})

real_summary = (
    real.groupby(["policy", "Experiment"])["prefix_hit_rate_percent"]
    .mean()
    .reset_index()
    .rename(columns={
        "policy": "Policy",
        "prefix_hit_rate_percent": "Real_Average_Prefix_Hit_Rate_Percent"
    })
)

# Save detailed real-trace comparison
real_summary.to_csv(
    output_folder / "real_policy_summary.csv",
    index=False
)

# Save synthetic summary
synthetic_summary.to_csv(
    output_folder / "synthetic_policy_summary.csv",
    index=False
)

print("\nSYNTHETIC POLICY PERFORMANCE")
print(synthetic_summary.to_string(index=False))

print("\nREAL MOONCAKE POLICY PERFORMANCE")
print(real_summary.to_string(index=False))

print("\nComparison files saved in the results folder.")
