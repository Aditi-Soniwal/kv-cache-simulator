def recovery_time(history, change_point, threshold=.80, window=100):
    for i in range(change_point + window, len(history)+1):
        if sum(history[i-window:i])/window >= threshold:
            return i-change_point
    return None

def summarize(history, evictions, capacity, change_point):
    n=len(history); hits=sum(history)
    pre=history[:change_point]; post=history[change_point:]
    pre_rate=sum(pre)/len(pre); post_rate=sum(post)/len(post)
    return {
        "requests":n, "hit_rate":hits/n, "miss_rate":1-hits/n,
        "pre_change_hit_rate":pre_rate, "post_change_hit_rate":post_rate,
        "hit_rate_drop":max(0,pre_rate-post_rate),
        "recovery_time_requests":recovery_time(history,change_point),
        "evictions":evictions, "eviction_rate":evictions/n,
        "capacity":capacity
    }
