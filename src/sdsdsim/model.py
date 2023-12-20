#! /usr/bin/env python

import random
import numpy as np

from sdsdsim import GLOBAL_RNG
from sdsdsim import ctmc
from sdsdsim import node


class SDSDModel(object):
    def __init__(
        self,
        q = [ [-1.0,    1.0],
              [1.0,     -1.0] ],
        birth_rates = [1.0, 1.0],
        death_rates = [0.5, 0.5],
        burst_rates = [1.0, 1.0],
    ):
        self.ctmc = ctmc.CTMC(q)
        n_states = len(self.q)
        if len(birth_rates) != n_states:
            raise ValueError(
                f"Provided {len(birth_rates)} birth rates for {n_states} "
                "states"
            )
        self.birth_rates = birth_rates
        if len(death_rates) != n_states:
            raise ValueError(
                f"Provided {len(death_rates)} death rates for {n_states} "
                "states"
            )
        self.death_rates = death_rates
        if len(burst_rates) != n_states:
            raise ValueError(
                f"Provided {len(burst_rates)} burst rates for {n_states} "
                "states"
            )
        self.burst_rates = burst_rates


def sim_SDSD_tree(
    rng_seed,
    sdsd_model,
    max_extant_tips = 50,
    max_extinct_tips = None,
    max_total_tips = None,
    max_time = None,
):
    rng = random.Random(rng_seed)
    root_state = self.ctmc.draw_random_state(rng)
