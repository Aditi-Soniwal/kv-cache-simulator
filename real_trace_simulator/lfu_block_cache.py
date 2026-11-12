
from collections import defaultdict, OrderedDict


class LFUBlockCache:

    def __init__(self, capacity, exclude_root_block=False):

        if capacity <= 0:
            raise ValueError("Cache capacity must be positive.")

        self.capacity = capacity
        self.exclude_root_block = exclude_root_block

        # Stores each block's current frequency
        self.key_frequency = {}

        # Frequency -> ordered blocks.
        # Within the same frequency, oldest block is evicted first.
        self.frequency_buckets = defaultdict(OrderedDict)

        self.min_frequency = 0

        self.total_requests = 0
        self.total_blocks = 0
        self.prefix_hits = 0
        self.evictions = 0

        self.hits_by_position = {}
        self.root_blocks_excluded = 0

    def _update_frequency(self, block_id):

        old_frequency = self.key_frequency[block_id]

        # Remove block from its old frequency bucket
        del self.frequency_buckets[old_frequency][block_id]

        # If the minimum-frequency bucket becomes empty,
        # increase the minimum frequency
        if not self.frequency_buckets[old_frequency]:

            del self.frequency_buckets[old_frequency]

            if self.min_frequency == old_frequency:
                self.min_frequency += 1

        # Increase frequency
        new_frequency = old_frequency + 1

        self.key_frequency[block_id] = new_frequency

        # Add block to the end of its new frequency bucket
        self.frequency_buckets[new_frequency][block_id] = None

    def _evict(self):

        # Find the oldest block in the minimum-frequency bucket
        bucket = self.frequency_buckets[self.min_frequency]

        block_id, _ = bucket.popitem(last=False)

        del self.key_frequency[block_id]

        if not bucket:
            del self.frequency_buckets[self.min_frequency]

            if self.frequency_buckets:
                self.min_frequency = min(self.frequency_buckets.keys())
            else:
                self.min_frequency = 0

        self.evictions += 1

    def _insert(self, block_id):

        if len(self.key_frequency) >= self.capacity:
            self._evict()

        # Every newly inserted block starts with frequency 1
        self.key_frequency[block_id] = 1
        self.frequency_buckets[1][block_id] = None

        self.min_frequency = 1

    def access(self, request):

        self.total_requests += 1

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

        # Find the longest reusable prefix
        hit_length = 0

        for block_id in hashes:

            if block_id not in self.key_frequency:
                break

            hit_length += 1

            position = position_offset + hit_length - 1

            self.hits_by_position[position] = (
                self.hits_by_position.get(position, 0) + 1
            )

            # Only blocks in the reusable prefix
            # have their frequency increased
            self._update_frequency(block_id)

        self.prefix_hits += hit_length

        # Process blocks after the first prefix miss
        new_blocks = hashes[hit_length:]

        for block_id in new_blocks:

            # Do not refresh frequency for blocks that
            # are cached but are not part of the prefix hit
            if block_id in self.key_frequency:
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
            "policy": "LFU",
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
            "final_cache_size": len(self.key_frequency),
            "hits_by_position": self.hits_by_position.copy()
        }


if __name__ == "__main__":

    print("========== LFU CACHE UNIT TEST ==========")

    cache = LFUBlockCache(capacity=5)

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
