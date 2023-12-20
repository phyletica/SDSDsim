#! /usr/bin/env python

import os
import sys
import math
import random
import pytest

from sdsdsim import rng_utils


class TestGetWeightedIndex:
    def test_uniform(self):
        rng = random.Random(1)
        weights = [3, 3, 3, 3]
        counts = [0 for i in range(len(weights))]
        n = 1000000
        for rep in n:
            idx = rng_utils.get_weighted_index(weights, rng)
            counts[idx] += 1
        props = [c / n for c in counts]
        for p in props:
            assert math.isclose(p, 1.0 / len(weights))

    def test_nonuniform(self):
        rng = random.Random(1)
        weights = [5, 1, 3, 1]
        expected = [ w / sum(weights) for w in weights ]
        counts = [0 for i in range(len(weights))]
        n = 1000000
        for rep in n:
            idx = rng_utils.get_weighted_index(weights, rng)
            counts[idx] += 1
        props = [c / n for c in counts]
        for i in range(len(weights)):
            assert math.isclose(props[i], expected[i]) 

    def test_zero(self):
        rng = random.Random(1)
        weights = [5, 0, 3, 2]
        expected = [ w / sum(weights) for w in weights ]
        counts = [0 for i in range(len(weights))]
        n = 1000000
        for rep in n:
            idx = rng_utils.get_weighted_index(weights, rng)
            counts[idx] += 1
        props = [c / n for c in counts]
        for i in range(len(weights)):
            assert math.isclose(props[i], expected[i]) 
