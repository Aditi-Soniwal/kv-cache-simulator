import os
import pandas as pd
import matplotlib.pyplot as plt
from workload import generate_shift_trace
from policies import LRUCache, LFUCache, StaticTTLCache, AdaptiveCache
from metrics import summarize

RESULTS="results"; os.makedirs(RESULTS, exist_ok=True)
CAPACITY = 20
BEFORE = 5000
AFTER = 5000
CHANGE = BEFORE

trace = generate_shift_trace(
    BEFORE,
    AFTER,
    num_keys=200,
    seed=42
)

policies={"LRU":LRUCache(CAPACITY),"LFU":LFUCache(CAPACITY),
          "Static-TTL":StaticTTLCache(CAPACITY,100),
          "Adaptive":AdaptiveCache(CAPACITY,100)}

rows=[]; histories={}
for name, cache in policies.items():
    h=[]
    for t,key in enumerate(trace):
        h.append(1 if cache.access(key,t) else 0)
    histories[name]=h
    row=summarize(h,cache.evictions,CAPACITY,CHANGE); row["policy"]=name
    rows.append(row)

df=pd.DataFrame(rows)
df.to_csv(f"{RESULTS}/policy_comparison.csv",index=False)

plt.figure(figsize=(10,5))
for name,h in histories.items():
    plt.plot(pd.Series(h).rolling(100).mean(),label=name)
plt.axvline(CHANGE,linestyle="--",label="Pattern change")
plt.xlabel("Request number"); plt.ylabel("Rolling hit rate")
plt.title("KV-Cache Hit Rate Under Sudden Reuse-Pattern Change")
plt.legend(); plt.tight_layout()
plt.savefig(f"{RESULTS}/hit_rate_over_time.png",dpi=160); plt.close()

plt.figure(figsize=(8,5))
df.set_index("policy")["hit_rate"].plot(kind="bar")
plt.ylabel("Overall hit rate"); plt.title("Overall Hit Rate by Policy")
plt.tight_layout(); plt.savefig(f"{RESULTS}/overall_hit_rate.png",dpi=160); plt.close()

print(df[["policy","hit_rate","pre_change_hit_rate","post_change_hit_rate","hit_rate_drop","recovery_time_requests","evictions"]].to_string(index=False))
