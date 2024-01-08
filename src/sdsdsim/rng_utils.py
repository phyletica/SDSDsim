#! /usr/bin/env python

import sys
import math

from sdsdsim import math_utils, GLOBAL_RNG

MIN_FLOAT = sys.float_info.min
MAX_FLOAT = sys.float_info.max
LN_MIN_FLOAT = math.log(MIN_FLOAT)
LN_MAX_FLOAT = math.log(MAX_FLOAT)

def get_weighted_index(weights, rng = None):
    total_weight = sum(weights)
    return get_prob_index([w / total_weight for w in weights], rng)

def get_prob_index(probs, rng = None):
    assert math_utils.is_zero(1.0 - sum(probs))
    if not rng:
        rng = GLOBAL_RNG
    u = rng.random()
    for i, p in enumerate(probs):
        u -= p
        if u < 0.0:
            return i
    assert math_utils.is_zero(u), print(u)
    return i

def poisson_rv(mean, rng = None):
    assert mean > 0.0
    if not rng:
        rng = GLOBAL_RNG
    neg_mean = -mean
    n_divs = 1
    if neg_mean < LN_MIN_FLOAT:
        n_divs = 1
        while neg_mean < LN_MIN_FLOAT:
            n_divs += 1
            neg_mean = -mean / n_divs
        n = 0
        for i in range(n_divs):
            n += poisson_rv(-neg_mean, rng)
        return n
    L = math.exp(neg_mean)
    p = 1.0
    k = 0.0
    while p >= L:
        k = k + 1.0
        u = rng.random()
        p = p * u
    n = k - 1.0
    if n > sys.maxsize:
        raise Exception("Poisson draw was larger than maxsize")
    return int(n)

def get_safe_seed(rng):
    """
    Get a random seed (int) between 0 and 2^31, which is safe to write and read
    across systems and is safe for seeding numpy (which must be between 0 and
    2^32-1).

    Parameters
    ----------
    rng : `random.Random` object
        An instance of a `random.Random` object

    Returns
    -------
    int
        A random integer from the range 1 to 2^31-1 (inclusive)
    """
    return rng.randint(1, (2**31)-1)
