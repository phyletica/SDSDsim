#! /usr/bin/env python

import numpy as np

from sdsdsim import GLOBAL_RNG
from sdsdsim import math_utils
from sdsdsim import rng_utils


class CTMC(object):
    """
    The methods for getting the steady-state probabilities borrow heavily from
    this very nice blog post by Vince Knight:
        https://vknight.org/blog/posts/continuous-time-markov-chains
    """
    def __init__(
        self,
        q = np.array([[-1.0,   1.0],
                      [ 1.0,  -1.0]]),
    ):
        q = np.array(q)
        self.vet_q_matrix(q)
        self.q = q

    @classmethod
    def vet_q_matrix(cls, q):
        n_states = len(q)
        for i, row in enumerate(q):
            if len(row) != n_states:
                raise ValueError(
                    f"Row {i} has {len(row)} states; expecting {n_states}")
            diag_rate = row[i]
            if diag_rate >= 0.0:
                raise ValueError(f"Diagonal rate in row {i} is not negative")
            transition_rate = 0.0
            for j, rate in enumerate(row):
                if i == j:
                    continue
                if rate < 0.0:
                    raise ValueError(f"Off-diagonal rate [{i}][{j}] is negative")
                transition_rate += rate
            if transition_rate < 0.0:
                raise ValueError(f"Row {i} off-diagonal rates do not sum to be positive")
            row_sum = transition_rate + diag_rate
            if not math_utils.is_zero(row_sum):
                raise ValueError(f"Row {i} does not sum to zero")

    def _get_n_states(self):
        return len(self.q)

    n_states = property(_get_n_states)

    def get_rate_from(self, state):
        row = self.q[state]
        rate = 0.0
        for r in row:
            if r > 0.0:
                rate += r
        return rate

    def draw_transition(self, state, rng = None):
        if not rng:
            rng = GLOBAL_RNG
        row = self.q[state]
        potential_states = np.where(row > 0.0)[0]
        rates = row[potential_states]
        state_index = rng_utils.get_weighted_index(rates, rng)
        new_state = potential_states[state_index]
        return new_state

    def are_steady_state_probs(self, state_probs):
        return np.allclose((state_probs @ self.q), 0.0)

    def get_steady_state_probs(self):
        m = np.vstack((self.q.transpose()[:-1], np.ones(self.n_states)))
        b = np.vstack((np.zeros((self.n_states - 1, 1)), [1]))
        state_probs = np.linalg.solve(m, b).transpose()[0]
        return state_probs
    
    def draw_random_state(self, rng = None):
        if not rng:
            rng = GLOBAL_RNG
        steady_state_probs = self.get_steady_state_probs()
        state = rng_utils.get_prob_index(steady_state_probs, rng)
        return state

    def sim_steady_state_probs(
        self,
        max_time = 10000.0,
        warmup_time = 500.0,
        rng = None,
    ):
        if warmup_time >= max_time:
            raise ValueError("max_time must be > warmup_time")
        if not rng:
            rng = GLOBAL_RNG
        state = 0
        clock = 0.0
        time_in_state = {x : 0.0 for x in range(self.n_states) }

        while clock < max_time:
            row = self.q[state]
            potential_states = np.where(row > 0.0)[0]
            rates = row[potential_states]
            samples = [rng.expovariate(r) for r in rates]
            time = np.min(samples)
            clock += time
            if clock > warmup_time:
                time_in_state[state] += time
            state = potential_states[np.argmin(samples)]
        
        total_time = sum(time_in_state.values())
        prop_in_state = [
            time_in_state[i] / total_time for i in range(self.n_states)
        ]
        return np.array(prop_in_state)
