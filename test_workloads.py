
from workload import (
    generate_shift_trace,
    generate_stable_trace,
    generate_gradual_shift_trace,
    generate_repeated_shift_trace,
    generate_low_reuse_trace,
    generate_high_cache_pressure_trace
)

workloads = {
    "Sudden shift": generate_shift_trace(),
    "Stable reuse": generate_stable_trace(),
    "Gradual shift": generate_gradual_shift_trace(),
    "Repeated shifts": generate_repeated_shift_trace(),
    "Low reuse": generate_low_reuse_trace(length=10000),
    "High cache pressure": generate_high_cache_pressure_trace(length=10000)
}

for name, trace in workloads.items():
    print(
        name,
        "| Requests:", len(trace),
        "| Unique keys:", len(set(trace)),
        "| First 5:", trace[:5]
    )