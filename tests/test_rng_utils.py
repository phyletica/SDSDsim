#! /usr/bin/env python

import os
import sys
import math
import random
import pytest

from sdsdsim import rng_utils
from sdsdsim.math_utils import is_zero 


class TestGetWeightedIndex:
    def test_uniform(self):
        rng = random.Random(1)
        weights = [3, 3, 3, 3]
        counts = [0 for i in range(len(weights))]
        n = 100000
        for rep in range(n):
            idx = rng_utils.get_weighted_index(weights, rng)
            counts[idx] += 1
        props = [c / n for c in counts]
        for p in props:
            assert is_zero(p - 1.0 / len(weights), 0.005)

    def test_nonuniform(self):
        rng = random.Random(1)
        weights = [5, 1, 3, 1]
        expected = [ w / sum(weights) for w in weights ]
        counts = [0 for i in range(len(weights))]
        n = 100000
        for rep in range(n):
            idx = rng_utils.get_weighted_index(weights, rng)
            counts[idx] += 1
        props = [c / n for c in counts]
        for i in range(len(weights)):
            assert is_zero(props[i] - expected[i], 0.005) 

    def test_zero(self):
        rng = random.Random(1)
        weights = [5, 0, 3, 2]
        expected = [ w / sum(weights) for w in weights ]
        counts = [0 for i in range(len(weights))]
        n = 100000
        for rep in range(n):
            idx = rng_utils.get_weighted_index(weights, rng)
            counts[idx] += 1
        props = [c / n for c in counts]
        for i in range(len(weights)):
            assert is_zero(props[i] - expected[i], 0.005) 
        assert props[1] == 0.0
