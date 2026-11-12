
from collections import OrderedDict


class StaticTTLBlockCache:

    def __init__(
        self,
        capacity,
        ttl_requests=100,
        exclude_root_block=False
    ):

        if capacity <= 0:
            raise ValueError("Cache capacity must be positive.")

        if ttl_requests <= 0:
            raise ValueError("TTL must be positive.")

        self.capacity = capacity
        self.ttl_requests = ttl_requests
        self.exclude_root_block = exclude_root_block

        # OrderedDict stores:
        # block_id -> request index of last reusable-prefix access
        # Oldest access is at the beginning.
        self.cache = OrderedDict()

        self.request_index = -1

        self.total_requests = 0
        self.total_blocks = 0
        self.prefix_hits = 0
        self.evictions = 0
        self.expirations = 0

        self.hits_by_position = {}
        self.root_blocks_excluded = 0

    def _expire_old_blocks(self):

        # Because cache order follows last access,
        # expired blocks appear at the beginning.
        while self.cache:

            oldest_block = next(iter(self.cache))
            last_access = self.cache[oldest_block]

            idle_requests = self.request_index - last_access

            if idle_requests > self.ttl_requests:

                self.cache.popitem(last=False)
                self.expirations += 1

            else:
                break

    def _insert(self, block_id):

        # Expire old entries before applying capacity eviction
        self._expire_old_blocks()

        # If still full, use LRU fallback
        if len(self.cache) >= self.capacity:

            self.cache.popitem(last=False)
            self.evictions += 1

        # Newly inserted block starts its TTL now
        self.cache[block_id] = self.request_index

    def access(self, request):

        self.request_index += 1
        self.total_requests += 1

        # Remove expired blocks before processing this request
        self._expire_old_blocks()

        hashes = request["hash_ids"]

        # Optional root-excluded sensitivity experiment
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

            # Refresh TTL only for a reusable-prefix hit
            self.cache[block_id] = self.request_index

            # Move refreshed block to newest position
            self.cache.move_to_end(block_id)

        self.prefix_hits += hit_length

        # Process blocks after the first prefix miss
        new_blocks = hashes[hit_length:]

        for block_id in new_blocks:

            # A cached block beyond the first prefix miss
            # is not counted as a hit and is not refreshed.
            if block_id in self.cache:
                continue

            self._insert(block_id)

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
            "policy": "Static TTL",
            "capacity": self.capacity,
            "ttl_requests": self.ttl_requests,
            "exclude_root_block": self.exclude_root_block,
            "requests": self.total_requests,
            "total_blocks": self.total_blocks,
            "prefix_hits": self.prefix_hits,
            "prefix_hit_rate": hit_rate,
            "root_hits": root_hits,
            "deeper_hits": deeper_hits,
            "root_blocks_excluded": self.root_blocks_excluded,
            "expirations": self.expirations,
            "evictions": self.evictions,
            "final_cache_size": len(self.cache),
            "hits_by_position": self.hits_by_position.copy()
        }


if __name__ == "__main__":

    print("========== STATIC TTL UNIT TEST ==========")

    cache = StaticTTLBlockCache(
        capacity=5,
        ttl_requests=2
    )

    test_requests = [
        {"hash_ids": [1, 2, 3]},
        {"hash_ids": [1, 2, 4]},
        {"hash_ids": [1, 2, 5]},
        {"hash_ids": [6, 7, 8]},
        {"hash_ids": [9, 10, 11]}
    ]

    for request in test_requests:
        cache.access(request)

    result = cache.get_results()

    for key, value in result.items():
        print(f"{key}: {value}")
