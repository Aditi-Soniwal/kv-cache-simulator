
import random


def generate_phase(length, num_keys, hot_keys, hot_probability, seed):
    """
    Generate requests with frequently reused hot keys
    and less frequently reused cold keys.
    """

    rng = random.Random(seed)

    hot = [f"P{i}" for i in range(hot_keys)]
    cold = [f"P{i}" for i in range(hot_keys, num_keys)]

    trace = []

    for _ in range(length):
        if rng.random() < hot_probability:
            key = rng.choice(hot)
        else:
            key = rng.choice(cold)

        trace.append(key)

    return trace


# 1. Existing workload: Sudden shift
def generate_shift_trace(
    before_length=5000,
    after_length=5000,
    num_keys=200,
    seed=42
):
    before = generate_phase(
        length=before_length,
        num_keys=num_keys,
        hot_keys=20,
        hot_probability=0.80,
        seed=seed
    )

    rng = random.Random(seed + 1)

    hot = [f"P{i}" for i in range(100, 120)]
    cold = [
        f"P{i}"
        for i in range(num_keys)
        if i not in range(100, 120)
    ]

    after = []

    for _ in range(after_length):
        if rng.random() < 0.80:
            after.append(rng.choice(hot))
        else:
            after.append(rng.choice(cold))

    return before + after


# 2. Stable reuse
def generate_stable_trace(
    length=10000,
    num_keys=200,
    seed=42
):
    """
    The same group of popular keys remains popular
    throughout the workload.
    """

    return generate_phase(
        length=length,
        num_keys=num_keys,
        hot_keys=20,
        hot_probability=0.80,
        seed=seed
    )


# 3. Gradual shift
def generate_gradual_shift_trace(
    length=10000,
    num_keys=200,
    seed=42
):
    """
    Popularity gradually moves from P0-P19
    to P100-P119.
    """

    rng = random.Random(seed)

    old_hot = list(range(0, 20))
    new_hot = list(range(100, 120))

    trace = []

    for t in range(length):

        # Gradually increase the probability of
        # selecting the new popular group.
        alpha = t / max(1, length - 1)

        if rng.random() < alpha:
            key = rng.choice(new_hot)
        else:
            key = rng.choice(old_hot)

        trace.append(f"P{key}")

    return trace


# 4. Repeated shifts
def generate_repeated_shift_trace(
    length=10000,
    num_keys=200,
    segment_length=2000,
    seed=42
):
    """
    Popularity alternates between two groups
    after every segment.
    """

    rng = random.Random(seed)

    group_a = list(range(0, 20))
    group_b = list(range(100, 120))

    trace = []

    for t in range(length):

        segment = t // segment_length

        if segment % 2 == 0:
            hot = group_a
        else:
            hot = group_b

        # 80% hot requests, 20% other requests
        if rng.random() < 0.80:
            key = rng.choice(hot)
        else:
            key = rng.randrange(num_keys)

        trace.append(f"P{key}")

    return trace


# 5. Low reuse
def generate_low_reuse_trace(
    length=10000,
    num_keys=5000,
    seed=42
):
    """
    Requests are selected from a large key pool,
    so individual keys are less likely to repeat.
    """

    rng = random.Random(seed)

    return [
        f"K{rng.randrange(num_keys)}"
        for _ in range(length)
    ]


# 6. High cache pressure
def generate_high_cache_pressure_trace(
    length=10000,
    num_keys=200,
    seed=42
):
    """
    Requests are spread uniformly across many keys.
    With a small cache, many keys compete for space.
    """

    rng = random.Random(seed)

    return [
        f"P{rng.randrange(num_keys)}"
        for _ in range(length)
    ]