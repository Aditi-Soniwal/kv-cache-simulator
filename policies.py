from collections import OrderedDict, defaultdict, deque

class LRUCache:
    def __init__(self, capacity):
        self.capacity, self.cache, self.evictions = capacity, OrderedDict(), 0
    def access(self, key, t):
        hit = key in self.cache
        if hit:
            self.cache.move_to_end(key)
            self.cache[key]["last"] = t
            self.cache[key]["freq"] += 1
        else:
            if len(self.cache) >= self.capacity:
                self.cache.popitem(last=False); self.evictions += 1
            self.cache[key] = {"last": t, "freq": 1}
        return hit

class LFUCache:
    def __init__(self, capacity):
        self.capacity, self.cache, self.evictions = capacity, {}, 0
    def access(self, key, t):
        if key in self.cache:
            self.cache[key]["freq"] += 1; self.cache[key]["last"] = t
            return True
        if len(self.cache) >= self.capacity:
            victim = min(self.cache, key=lambda k:(self.cache[k]["freq"], self.cache[k]["last"]))
            del self.cache[victim]; self.evictions += 1
        self.cache[key] = {"freq":1, "last":t}
        return False

class StaticTTLCache:
    def __init__(self, capacity, ttl=100):
        self.capacity, self.ttl, self.cache, self.evictions = capacity, ttl, {}, 0
    def access(self, key, t):
        for k in list(self.cache):
            if t - self.cache[k]["last"] > self.ttl:
                del self.cache[k]
        if key in self.cache:
            self.cache[key]["last"] = t
            return True
        if len(self.cache) >= self.capacity:
            victim = min(self.cache, key=lambda k:self.cache[k]["last"])
            del self.cache[victim]; self.evictions += 1
        self.cache[key] = {"last":t}
        return False

class AdaptiveCache:
    def __init__(self, capacity, window=100):
        self.capacity, self.window = capacity, window
        self.cache, self.recent, self.evictions = {}, deque(maxlen=window), 0
    def access(self, key, t):
        self.recent.append(key)
        counts = defaultdict(int)
        for x in self.recent: counts[x] += 1
        if key in self.cache:
            self.cache[key]["last"] = t; self.cache[key]["recent_freq"] = counts[key]
            return True
        if len(self.cache) >= self.capacity:
            victim = min(self.cache, key=lambda k:(self.cache[k]["recent_freq"], self.cache[k]["last"]))
            del self.cache[victim]; self.evictions += 1
        self.cache[key] = {"last":t, "recent_freq":counts[key]}
        return False
