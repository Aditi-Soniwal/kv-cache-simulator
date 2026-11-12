
from collections import OrderedDict


class LRUBlockCache:

    def __init__(self, capacity, exclude_root_block=False):

        if capacity <= 0:
            raise ValueError("Cache capacity must be positive.")

        self.capacity = capacity
        self.exclude_root_block = exclude_root_block

        self.cache = OrderedDict()

        self.total_requests = 0
        self.total_blocks = 0
        self.prefix_hits = 0
        self.evictions = 0

        self.hits_by_position = {}
        self.root_blocks_excluded = 0

    def access(self, request):

        self.total_requests += 1

        hashes = request["hash_ids"]

        # Optional sensitivity experiment:
        # exclude the first block only when its ID is 0.
        if (
            self.exclude_root_block
            and hashes
            and hashes[0] == 0
        ):
            hashes = hashes[1:]
            self.root_blocks_excluded += 1

            # Original position of the first remaining block
            position_offset = 1

        else:
            position_offset = 0

        self.total_blocks += len(hashes)

        # Find the longest reusable prefix
        hit_length = 0

        for block_id in hashes:

            if block_id not in self.cache:
                break

            hit_length += 1

            # Record hit using original prefix position
            position = position_offset + hit_length - 1

            self.hits_by_position[position] = (
                self.hits_by_position.get(position, 0) + 1
            )

            # Only actual prefix hits refresh recency
            self.cache.move_to_end(block_id)

        self.prefix_hits += hit_length

        # Process blocks after the first missing prefix block
        new_blocks = hashes[hit_length:]

        for block_id in new_blocks:

            # If already cached but not part of the reusable
            # prefix, do not refresh its recency.
            if block_id in self.cache:
                continue

            # Evict least recently used block if full
            while len(self.cache) >= self.capacity:

                self.cache.popitem(last=False)
                self.evictions += 1

            # Insert newly computed block
            self.cache[block_id] = None

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
            "policy": "LRU",
            "capacity": self.capacity,
            "exclude_root_block": self.exclude_root_block,
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

    print("========== LRU CACHE UNIT TEST ==========")

    cache = LRUBlockCache(capacity=5)

    test_requests = [
        {"hash_ids": [1, 2, 3]},
        {"hash_ids": [1, 2, 4]},
        {"hash_ids": [1, 2, 5]},
        {"hash_ids": [6, 7, 8]}
    ]

    for request in test_requests:
        cache.access(request)

    result = cache.get_results()

    for key, value in result.items():
        print(f"{key}: {value}")
