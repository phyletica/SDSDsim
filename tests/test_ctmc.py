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

class TestGetRateFrom:
    def test_four_states(self):
        rng = random.Random(1)
        q = [
            [-5.0, 1.5, 2.0, 1.5],
            [1.0, -3.0, 1.5, 0.5],
            [1.5, 2.0, -6.0, 2.5],
            [0.5, 0.2, 0.3, -1.0],
        ]
        m = ctmc.CTMC(q)

        expected_rates = [5.0, 3.0, 6.0, 1.0]

        for i in range(len(expected_rates)):
            assert is_zero(expected_rates[i] - m.get_rate_from(i))

class TestDrawRandomState:
    def test_four_states(self):
        rng = random.Random(1)
        q = [
            [-5.0, 1.5, 2.0, 1.5],
            [1.0, -3.0, 1.5, 0.5],
            [1.5, 2.0, -6.0, 2.5],
            [0.5, 0.2, 0.3, -1.0],
        ]
        m = ctmc.CTMC(q)
        
        probs = m.get_steady_state_probs()
        state_counts = [0 for _ in range(len(probs))]
        n = 100000
        for i in range(n):
            state = m.draw_random_state(rng)
            state_counts[state] += 1
        assert sum(state_counts) == n
        sim_probs = [c / n for c in state_counts]
        for i in range(len(probs)):
            assert is_zero(probs[i] - sim_probs[i], 0.005)

class TestDrawTransition:
    def test_four_states(self):
        rng = random.Random(1)
        q = [
            [-5.0, 1.5, 2.0, 1.5],
            [1.0, -3.0, 1.5, 0.5],
            [1.5, 2.0, -6.0, 2.5],
            [0.5, 0.2, 0.3, -1.0],
        ]
        m = ctmc.CTMC(q)

        expected_probs = []
        state_counts = []
        for i, row in enumerate(q):
            total_rate = 0.0
            for j, rate in enumerate(row):
                if i == j:
                    continue
                total_rate += rate
            probs = []
            counts = []
            for j, rate in enumerate(row):
                counts.append(0)
                if i == j:
                    probs.append(0.0)
                    continue
                probs.append(rate / total_rate)
            expected_probs.append(probs)
            state_counts.append(counts)
        
        n = 100000
        for state in range(len(q)):
            for rep in range(n):
                new_state = m.draw_transition(state, rng)
                state_counts[state][new_state] += 1
            for j in range(len(q)):
                state_counts[state][j] = state_counts[state][j] / float(n)

        for i, row in enumerate(expected_probs):
            for j, exp_prob in enumerate(row):
                if i == j:
                    assert is_zero(state_counts[i][j])
                    continue
                assert is_zero(exp_prob - state_counts[i][j], 0.005)

