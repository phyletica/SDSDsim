#! /usr/bin/env python

import os
import sys
import math
import random
import pytest

from sdsdsim import model
from sdsdsim.math_utils import is_zero 


def expected_yule_tree_height(ntips, birth_rate):
    height = 0
    for i in range(2, ntips + 1):
        height += float(1) / (i * birth_rate)
    return height

def expected_yule_tree_length(ntips, birth_rate):
    return float(ntips - 1) / birth_rate

class TestSimSDSDTree:
    def test_yule(self):
        rng = random.Random(1)

        sdsd_model = model.SDSDModel(
                q = [
                    [-1.0, 1.0],
                    [1.0, -1.0],
                ],
                birth_rates = [1.0, 1.0],
                death_rates = [0.0, 0.0],
                burst_rate = 0.0,
                burst_probs = [0.0, 0.0],
                only_bifurcate = True,
                )

        n = 1000
        max_extant_leaves = 50
        expected_height = expected_yule_tree_height(max_extant_leaves, 1.0)
        expected_length = expected_yule_tree_length(max_extant_leaves, 1.0)
        root_heights = []
        tree_lengths = []
        for i in range(n):
            survived, root, burst_times = model.sim_SDSD_tree(
                    rng_seed = rng.random(),
                    sdsd_model = sdsd_model,
                    max_extant_leaves = max_extant_leaves,
                    max_extinct_leaves = None,
                    max_total_leaves = None,
                    max_time = None,
                    )
            assert survived
            assert len(burst_times) == 0
            root_heights.append(root.height)
            tree_lengths.append(root.tree_length)
            n_leaves = 0
            for node in root:
                assert node.is_burst_node == False
                assert node.is_extinct == False
                if node.is_leaf():
                    n_leaves += 1
        mean_height = sum(root_heights) / n
        # Expected height is about 3.5
        assert is_zero(expected_height - mean_height, 0.05)

        mean_length = sum(tree_lengths) / n
        # Expected length is 49
        assert is_zero(expected_length - mean_length, 0.5)
