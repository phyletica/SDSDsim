#! /usr/bin/env python

import os
import sys
import math
import random
import pytest

from sdsdsim import ctmc


class TestGetSteadyStateProbs:
    def test_simple(self):
        rng = random.Random(1)
        q = [
            [-5.0, 1.5, 2.0, 1.5],
            [-3.0, 1.0, 1.5, 0.5],
            [-6.0, 1.5, 2.0, 2.5],
            [-1.0, 0.5, 0.2, 0.3],
        ]

        m = ctmc.CTMC(q)

        sim_state_probs = m.sim_steady_state_probs(max_time = 1000000.0)
        calc_state_probs = m.get_steady_state_probs()

        assert len(sim_state_probs) == len(q)
        assert len(calc_state_probs) == len(q)

        for i in range(len(q)):
            assert math.isclose(sim_state_probs[i], calc_state_probs[i])
