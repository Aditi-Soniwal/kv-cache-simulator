# KV-Cache Retention Robustness Simulator

Research prototype for:
Evaluating the Robustness of KV-Cache Retention Policies Under Sudden Changes in Request-Reuse Patterns.

The simulator generates a controlled request trace, introduces a sudden reuse-pattern shift, simulates LRU, LFU, Static-TTL and a simple Adaptive baseline, and measures cache performance and recovery time.

Install:
pip install -r requirements.txt

Run:
python simulator.py

Important: this is a cache-behavior simulator, not a full LLM server. The adaptive policy is a baseline, not a claimed novel algorithm.
