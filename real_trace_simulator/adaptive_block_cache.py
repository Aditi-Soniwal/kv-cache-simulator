
from collections import OrderedDict, Counter, deque


class AdaptiveBlockCache:

    def __init__(
        self,
        capacity,
        exclude_root_block=False,
        window_size=100
    ):

        if capacity <= 0:
            raise ValueError("Cache capacity must be positive.")

        if window_size <= 0:
            raise ValueError("Window size must be positive.")

        self.capacity = capacity
        self.exclude_root_block = exclude_root_block
        self.window_size = window_size

        # Cached blocks
        self.cache = OrderedDict()

        # Recent request history
        self.recent_requests = deque()
        self.recent_frequency = Counter()

        # Statistics
        self.total_requests = 0
        self.total_blocks = 0
        self.prefix_hits = 0
        self.evictions = 0

        self.hits_by_position = {}
        self.root_blocks_excluded = 0

        # Tracks last access for tie-breaking
        self.access_clock = 0
        self.last_access = {}

    def update_recent_window(self, hashes):

        # Add current request to sliding window
        request_blocks = list(hashes)

        self.recent_requests.append(request_blocks)

        for block_id in request_blocks:
            self.recent_frequency[block_id] += 1

        # Remove oldest request when window is full
        if len(self.recent_requests) > self.window_size:

            expired_request = self.recent_requests.popleft()

            for block_id in expired_request:

                self.recent_frequency[block_id] -= 1

                if self.recent_frequency[block_id] <= 0:
                    del self.recent_frequency[block_id]

    def evict_block(self):

        if not self.cache:
            return

        # Lowest recent frequency is evicted first.
        # If scores tie, evict the least recently accessed block.
        victim = min(
            self.cache.keys(),
            key=lambda block_id: (
                self.recent_frequency.get(block_id, 0),
                self.last_access.get(block_id, 0)
            )
        )

        del self.cache[victim]
        del self.last_access[victim]

        self.evictions += 1

    def access(self, request):

        self.total_requests += 1

        hashes = list(request["hash_ids"])

        # Optional root-block exclusion experiment
        if (
            self.exclude_root_block
            and hashes
            and hashes[0] == 0
        ):

            hashes = hashes[1:]
            self.root_blocks_excluded += 1
            position_offset = 1

        else:
            position_offset = 0

        self.total_blocks += len(hashes)

        # Update recent usage information
        self.update_recent_window(hashes)

        # Find longest reusable prefix
        hit_length = 0

        for block_id in hashes:

            if block_id not in self.cache:
                break

            hit_length += 1

            position = position_offset + hit_length - 1

            self.hits_by_position[position] = (
                self.hits_by_position.get(position, 0) + 1
            )

            # Refresh last-access information
            self.access_clock += 1
            self.last_access[block_id] = self.access_clock

            self.cache.move_to_end(block_id)

        self.prefix_hits += hit_length

        # Process blocks after the first missing prefix block
        new_blocks = hashes[hit_length:]

        for block_id in new_blocks:

            # Do not refresh blocks outside the reusable prefix
            if block_id in self.cache:
                continue

            # Evict until there is available space
            while len(self.cache) >= self.capacity:
                self.evict_block()

            # Insert newly computed block
            self.cache[block_id] = None

            self.access_clock += 1
            self.last_access[block_id] = self.access_clock

    def get_results(self):

        hit_rate = (
            self.prefix_hits / self.total_blocks * 100
            if self.total_blocks else 0
        )

        root_hits = self.hits_by_position.get(0, 0)

        deeper_hits = sum(
            count
            for position, count in self.hits_by_position.items()
            if position > 0
        )

        return {
            "policy": "Adaptive",
            "capacity": self.capacity,
            "exclude_root_block": self.exclude_root_block,
            "window_size": self.window_size,
            "requests": self.total_requests,
            "total_blocks": self.total_blocks,
            "prefix_hits": self.prefix_hits,
            "prefix_hit_rate": hit_rate,
            "root_hits": root_hits,
            "deeper_hits": deeper_hits,
            "root_blocks_excluded": self.root_blocks_excluded,
            "evictions": self.evictions,
            "final_cache_size": len(self.cache),
            "hits_by_position": self.hits_by_position.copy()
        }


if __name__ == "__main__":

    print("========== ADAPTIVE BLOCK CACHE UNIT TEST ==========")

    cache = AdaptiveBlockCache(
        capacity=5,
        window_size=100
    )

    test_requests = [
        {"hash_ids": [1, 2, 3]},
        {"hash_ids": [1, 2, 4]},
        {"hash_ids": [1, 2, 5]},
        {"hash_ids": [6, 7, 8]},
        {"hash_ids": [1, 2, 3]}
    ]

    for request in test_requests:
        cache.access(request)

    result = cache.get_results()

    for key, value in result.items():
        print(f"{key}: {value}")
