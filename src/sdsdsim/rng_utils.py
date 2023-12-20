#! /usr/bin/env python

from sdsdsim import math_utils, GLOBAL_RNG


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
