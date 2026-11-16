# KV-Cache Retention Policy Simulator

A research project exploring how different KV-cache retention policies perform when request patterns change in LLM serving.

## About the Project

KV-cache helps Large Language Models avoid repeating computations by storing previously generated attention information. But cache memory is limited, so the system needs to decide which entries to keep and which ones to remove.

This project compares four cache replacement and retention policies to understand how they behave under different request patterns, especially when those patterns change over time.

The main focus is on one question:

**How do different KV-cache retention policies perform when request-reuse patterns suddenly change?**

## Policies Compared

| Policy | What it does |
|---|---|
| LRU | Removes the least recently used entry. |
| LFU | Removes the least frequently used entry. |
| Static TTL | Removes entries after a fixed time period. |
| Adaptive | Uses recent access frequency to make retention decisions. |

The Adaptive policy is implemented using a sliding window of recent requests.

## Experiments

I tested the policies in two different settings.

### 1. Synthetic Workloads

The simulator uses six workloads, each representing a different request pattern.

- Sudden Shift
- Stable Reuse
- Gradual Shift
- Repeated Shifts
- Low Reuse
- High Cache Pressure

**Setup:**
- 10,000 requests per workload
- 200 possible keys
- Cache capacity of 20 entries
- Four retention policies

### 2. Mooncake Conversation Trace

I also tested the policies using a Mooncake conversation trace instead of relying only on generated workloads.

- 12,031 requests/conversations
- 288,500 blocks in Full Prefix
- 276,469 blocks in Root Excluded
- Cache capacities: 256, 512, 1,024, 2,048 and 4,096 blocks
- Static TTL: 100 request intervals
- Adaptive window: 100 requests

Two versions of the experiment were performed:

- **Full Prefix:** Uses the complete prefix block sequence.
- **Root Excluded:** Excludes the root block when its hash ID is zero.

## Results

### Synthetic Experiments

Average hit rate across all six workloads:

| Policy | Average Hit Rate |
|---|---:|
| LRU | 41.56% |
| LFU | 37.72% |
| Static TTL | 41.56% |
| Adaptive | 49.39% |

Adaptive performed best on average in the synthetic experiments. LFU performed particularly well when request patterns remained stable.

### Mooncake Experiments

Average hit rate across the five tested cache capacities:

| Policy | Full Prefix | Root Excluded |
|---|---:|---:|
| LRU | 5.42% | 1.31% |
| LFU | 5.70% | 1.60% |
| Static TTL | 4.81% | 0.67% |
| Adaptive | 5.43% | 1.32% |

LFU achieved the highest average hit rate in both Mooncake experiments. Adaptive and LRU showed very similar results.

These results also show that a policy performing well on synthetic workloads may not necessarily perform best on a real trace.

## Metrics Used

The experiments track:

- Cache hit rate
- Pre-change and post-change hit rates
- Hit-rate drop after workload changes
- Recovery time
- Eviction count
- TTL expirations

## Visualisations

The `results` folders contain the generated CSV files and graphs used to compare the policies.

Some of the included comparisons are:
- Synthetic workload comparison
- Mooncake Full Prefix comparison
- Mooncake Root Excluded comparison
- Capacity-wise comparison
- Normalised comparison across experiments

## Project Structure

```text
kv-cache-simulator/
│
├── real_trace_simulator/
│   └── results/
│
├── results/
│
├── capacity_wise_comparison.py
├── compare_synthetic_real.py
├── plot_normalised_comparison.py
├── plot_synthetic_real_comparison.py
├── plot_synthetic_vs_mooncake.py
│
├── .gitignore
└── README.md
```

## Running the Analysis

Clone the repository:

```bash
git clone https://github.com/Aditi-Soniwal/kv-cache-simulator.git
cd kv-cache-simulator
```

Install the required libraries:

```bash
pip install pandas numpy matplotlib
```

Run the analysis scripts:

```bash
python compare_synthetic_real.py
python capacity_wise_comparison.py
python plot_synthetic_real_comparison.py
python plot_synthetic_vs_mooncake.py
python plot_normalised_comparison.py
```

The scripts generate comparison tables and graphs inside the `results` folder.

*Note: The original Mooncake trace is not included in this repository. Running the real-trace experiments requires access to the source dataset.*

## What I Found

The experiments showed that:
- Adaptive performed best on average across the synthetic workloads.
- LFU performed best on average in the Mooncake experiments.
- LRU and Adaptive had very similar results on the real trace.
- Cache capacity and request-reuse patterns both affected policy performance.

The results are based on the workloads and configurations tested in this project. More traces and experiments would be needed to determine how these policies perform in other LLM serving environments.

## Future Work

Some things worth exploring next:
- Testing more real-world LLM traces.
- Trying different cache capacities and TTL values.
- Exploring semantic KV-cache reuse.
- Studying cache behaviour in multi-tenant LLM serving.

**Author:** Aditi Soniwal  
