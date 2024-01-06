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
                if node.is_leaf:
                    n_leaves += 1
                if not node.is_root:
                    assert is_zero(
                            (node.parent.height - node.height) - (
                             node.time - node.parent.time)
                            )
                state_history = node.leafward_state_history
                assert state_history[0][0] == node.rootward_state
                assert state_history[-1][0] == node.leafward_state
                duration = 0.0
                for state, length in state_history:
                    duration += length
                assert is_zero(node.branch_length - duration)
            assert n_leaves == max_extant_leaves
        mean_height = sum(root_heights) / n
        # Expected height is about 3.5
        assert is_zero(expected_height - mean_height, 0.05)

        mean_length = sum(tree_lengths) / n
        # Expected length is 49
        assert is_zero(expected_length - mean_length, 0.5)

    def test_basic_SDSD(self):
        rng = random.Random(1)

        sdsd_model = model.SDSDModel(
                q = [
                    [-1.0, 1.0],
                    [1.0, -1.0],
                ],
                birth_rates = [1.0, 2.0],
                death_rates = [0.5, 0.8],
                burst_rate = 1.0,
                burst_probs = [0.1, 0.5],
                burst_furcation_poisson_means = [1.0, 2.0],
                burst_furcation_poisson_shifts = [2, 2],
                only_bifurcate = False,
                )

        n = 100
        max_extant_leaves = 50
        for i in range(n):
            survived, root, burst_times = model.sim_SDSD_tree(
                    rng_seed = rng.random(),
                    sdsd_model = sdsd_model,
                    max_extant_leaves = max_extant_leaves,
                    max_extinct_leaves = None,
                    max_total_leaves = None,
                    max_time = None,
                    )
            n_leaves = 0
            for node in root:
                if node.is_leaf and (not node.is_extinct):
                    n_leaves += 1
                if not node.is_root:
                    assert is_zero(
                            (node.parent.height - node.height) - (
                             node.time - node.parent.time)
                            )
                state_history = node.leafward_state_history
                assert state_history[0][0] == node.rootward_state
                assert state_history[-1][0] == node.leafward_state
                duration = 0.0
                for state, length in state_history:
                    duration += length
                assert is_zero(node.branch_length - duration)
            if survived:
                assert n_leaves >= max_extant_leaves
            else:
                assert n_leaves == 0

    def test_rates_SDSD(self):
        rng = random.Random(1)

        r_trans = 1.5
        r_birth = 2.0
        r_death = 1.0
        r_burst = 1.2
        sdsd_model = model.SDSDModel(
                q = [
                    [-r_trans, r_trans],
                    [r_trans, -r_trans],
                ],
                birth_rates = [r_birth, r_birth],
                death_rates = [r_death, r_death],
                burst_rate = r_burst,
                burst_probs = [0.5, 0.5],
                burst_furcation_poisson_means = [1.0, 1.0],
                burst_furcation_poisson_shifts = [2, 2],
                only_bifurcate = False,
                )

        n = 200
        max_extant_leaves = None
        max_time = 2.0
        n_bursts = 0
        n_births_0 = 0
        n_births_1 = 0
        n_deaths_0 = 0
        n_deaths_1 = 0
        n_trans_01 = 0
        n_trans_10 = 0
        total_time = 0.0
        total_tree_length = 0.0
        for i in range(n):
            survived, root, burst_times = model.sim_SDSD_tree(
                    rng_seed = rng.random(),
                    sdsd_model = sdsd_model,
                    max_extant_leaves = max_extant_leaves,
                    max_extinct_leaves = None,
                    max_total_leaves = None,
                    max_time = max_time,
                    )
            # print(root.number_of_leaves)
            n_bursts += len(burst_times)
            assert root.seed_time == 0.0
            t = root.height + root.time
            if survived:
                assert is_zero(t - max_time)
            else:
                assert t < max_time
            total_time += (t)
            total_tree_length += (root.tree_length + root.time)
            for node in root:
                if node.is_extinct:
                    if node.leafward_state == 0:
                        n_deaths_0 += 1
                    elif node.leafward_state == 1:
                        n_deaths_1 += 1
                    else:
                        assert False == True
                elif (not node.is_leaf) and (not node.is_burst_node):
                    assert not node.is_extinct
                    assert len(node.children) == 2
                    if node.leafward_state == 0:
                        n_births_0 += 1
                    elif node.leafward_state == 1:
                        n_births_1 += 1
                    else:
                        assert False == True
                for trans in node.state_changes:
                    if trans == (0, 1):
                        n_trans_01 += 1
                    elif trans == (1, 0):
                        n_trans_10 += 1
                    else:
                        assert False == True
        n_trans = n_trans_01 + n_trans_10
        n_births = n_births_0 + n_births_1
        n_deaths = n_deaths_0 + n_deaths_1
        e_burst_rate = n_bursts / total_time
        e_birth_rate = n_births / total_tree_length
        e_death_rate = n_deaths / total_tree_length
        e_trans_rate = n_trans / total_tree_length
        eps = 0.1
        assert is_zero(
                (n_trans_10 / n_trans_01) - 1.0,
                eps
                )
        assert is_zero(
                (n_births_0 / n_births_1) - 1.0,
                eps
                )
        assert is_zero(
                (n_deaths_0 / n_deaths_1) - 1.0,
                eps
                )
        assert is_zero(
                e_trans_rate - r_trans,
                eps
                )
        assert is_zero(
                e_birth_rate - r_birth,
                eps
                )
        assert is_zero(
                e_death_rate - r_death,
                eps
                )
        assert is_zero(
                e_burst_rate - r_burst,
                eps
                )
