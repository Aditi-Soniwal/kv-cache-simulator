import random


def generate_phase(length, num_keys, hot_keys, hot_probability, seed):
    """
    Generates a workload with a mixture of:
    - frequently reused 'hot' keys
    - less frequently reused 'cold' keys
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


def generate_shift_trace(
    before_length=5000,
    after_length=5000,
    num_keys=200,
    seed=42
):

    # -----------------------------
    # PHASE 1
    # -----------------------------
    # P0-P19 are highly popular

    before = generate_phase(
        length=before_length,
        num_keys=num_keys,
        hot_keys=20,
        hot_probability=0.80,
        seed=seed
    )

    # -----------------------------
    # PHASE 2
    # -----------------------------
    # Suddenly a DIFFERENT group
    # becomes popular.
    #
    # P100-P119 are now hot.

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