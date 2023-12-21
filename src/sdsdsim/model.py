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
        burst_probs = [0.1, 0.6],
        burst_furcation_poisson_rates = [1.0, 2.0],
        burst_furcation_poisson_shifts = [2, 2],
        only_bifurcate = False,
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
    clock = 0.0
    rng = random.Random(rng_seed)
    root_state = self.ctmc.draw_random_state(rng)
    root = node.Node(
        parent = None,
        label = "root",
        rootward_state = root_state,
    )
    extant_nodes = [root]
    extinct_nodes = []

    while True:
        final_extension = False
        if (
            (len(extinct_nodes) == max_extinct_tips)
            or (len(extant_nodes) == max_extant_tips)
            or (len(extant_nodes) + len(extinct_nodes) == max_total_tips)
        ):
            final_extension = True

        lineage_total_rates = []
        lineage_rates = []
        for node in extant_nodes:
            total_rate = 0.0
            current_state = node.tipward_state
            birth_rate = self.birth_rates[current_state]
            death_rate = self.death_rates[current_state]
            burst_rate = self.death_rates[current_state]
            transition_rate = self.ctmc.get_rate_from(current_state)
            lineage_total_rates.append(
                birth_rate + death_rate + burst_rate + transition_rate
            )
            lineage_rates.append(
                (birth_rate, death_rate, burst_rate, transition_rate)
            )
        lineage_wait_times = [rng.expovariate(r) for r in lineage_total_rates]
        wait_time = np.min(lineage_wait_times)
        if clock + wait_time > max_time:
            clock = max_time
            break
        clock += wait_time
        lineage_index = lineage_wait_times[np.argmin(lineage_wait_times)]
        lin_rates= lineage_rates[lineage_index]
        event_index = rng_utils.get_weighted_index(lin_rates, rng)

        if (event_index < 3) and final_extension:
            break
        
        if event_index == 0:
            node = extant_nodes[lineage_index]
            node.time = clock
            extant_nodes.remove(node)
            for i in range(2):
                child = node.Node(
                    parent = node,
                    rootward_state = node.tipward_state,
                )
                node.add_child(child)
                extant_nodes.append(child)

        elif event_index == 1:
            node = extant_nodes[lineage_index]
            node.time = clock
            extant_nodes.remove(node)
            extinct_nodes.append(node)

        elif event_index == 2:
            # burst rate must be equal across states
            # probability of diverging at burst can differ
            # cuould have:
            #   self.burst_probs = [ x, y, ... ]
            #   self.burst_descendant_func = bifurcate # always 2
            #   self.burst_descendant_func = shifted_poisson # poisson + 2
            # or
            #   self.burst_poisson_rates = [x, y, ...] and do poisson + 1 or
            #   truncated poisson

            # This should cover all necessary use cases
            # self.burst_probs = [] can set to all 1s to defer to the poissons
            # self.burst_furcation_rates = []
            # self.burst_furcation_shifts = [] set to 1s if burst probs are 1s otherwise 2s
            # self.strict_bifurcate = False

