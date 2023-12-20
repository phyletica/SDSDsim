#! /usr/bin/env python

import os
import sys
import math
import random
import pytest

from sdsdsim import ctmc
from sdsdsim.math_utils import is_zero 


class TestGetSteadyStateProbs:
    def test_balanced_2(self):
        rng = random.Random(1)
        q = [
            [-1.0, 1.0],
            [1.0, -1.0],
        ]

        m = ctmc.CTMC(q)
        expected = [0.5, 0.5]
        sim_state_probs = m.sim_steady_state_probs(max_time = 10000.0, rng = rng)
        calc_state_probs = m.get_steady_state_probs()

        assert len(sim_state_probs) == len(q)
        assert len(calc_state_probs) == len(q)

        for i in range(len(q)):
            assert is_zero(sim_state_probs[i] - expected[i], 0.01)
            assert is_zero(calc_state_probs[i] - expected[i], 0.0000001)

    def test_imbalanced_2(self):
        rng = random.Random(1)
        q = [
            [-1.0, 1.0],
            [2.0, -2.0],
        ]

        m = ctmc.CTMC(q)
        expected = [2/3.0, 1/3.0]
        sim_state_probs = m.sim_steady_state_probs(max_time = 10000.0, rng = rng)
        calc_state_probs = m.get_steady_state_probs()

        assert len(sim_state_probs) == len(q)
        assert len(calc_state_probs) == len(q)

        for i in range(len(q)):
            assert is_zero(sim_state_probs[i] - expected[i], 0.01)
            assert is_zero(calc_state_probs[i] - expected[i], 0.0000001)

    def test_four_states(self):
        rng = random.Random(1)
        q = [
            [-5.0, 1.5, 2.0, 1.5],
            [1.0, -3.0, 1.5, 0.5],
            [1.5, 2.0, -6.0, 2.5],
            [0.5, 0.2, 0.3, -1.0],
        ]

        m = ctmc.CTMC(q)

        sim_state_probs = m.sim_steady_state_probs(max_time = 100000.0, rng = rng)
        calc_state_probs = m.get_steady_state_probs()

        assert len(sim_state_probs) == len(q)
        assert len(calc_state_probs) == len(q)

        for i in range(len(q)):
            assert is_zero(sim_state_probs[i] - calc_state_probs[i], 0.005)
