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
        burst_rate = 0.5,
        burst_probs = [0.1, 0.6],
        burst_furcation_poisson_means = [1.0, 2.0],
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
        if len(burst_furcation_poisson_means) != n_states:
            raise ValueError(
                f"Provided {len(burst_furcation_poisson_means)} burst "
                f"furcation poisson rates for {n_states} states"
            )
        self.burst_furcation_poisson_means = burst_furcation_poisson_means
        if len(burst_furcation_poisson_shifts) != n_states:
            raise ValueError(
                f"Provided {len(burst_furcation_poisson_shifts)} burst "
                f"furcation poisson shifts for {n_states} states"
            )
        self.burst_furcation_poisson_shifts = burst_furcation_poisson_shifts
        self.burst_rate = burst_rate
        self.only_bifurcate = only_bifurcate


def sim_SDSD_tree(
    rng_seed,
    sdsd_model,
    max_extant_leaves = 50,
    max_extinct_leaves = None,
    max_total_leaves = None,
    max_time = None,
    time_zero_at_root = False,
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
    burst_times = []

    while True:
        final_extension = False
        if ((max_extant_leaves is not None)
                and (len(extant_nodes) == max_extant_leaves)):
            final_extension = True
        elif ((max_extinct_leaves is not None)
                and (len(extinct_nodes) == max_extinct_leaves)):
            final_extension = True
        elif ((max_total_leaves is not None)
                and (len(extant_nodes) + len(extinct_nodes) == max_total_leaves)):
            final_extension = True
        lineage_total_rates = []
        lineage_rates = []
        for node in extant_nodes:
            total_rate = 0.0
            current_state = node.leafward_state
            birth_rate = self.birth_rates[current_state]
            death_rate = self.death_rates[current_state]
            transition_rate = self.ctmc.get_rate_from(current_state)
            lineage_total_rates.append(
                birth_rate + death_rate + transition_rate
            )
            lineage_rates.append(
                (birth_rate, death_rate, transition_rate)
            )
        lineage_total_rates.append(self.burst_rate)
        lineage_wait_times = [rng.expovariate(r) for r in lineage_total_rates]
        wait_time = np.min(lineage_wait_times)
        if clock + wait_time > max_time:
            clock = max_time
            break
        clock += wait_time
        lineage_index = lineage_wait_times[np.argmin(lineage_wait_times)]
        if lineage_index == len(lineage_wait_times) - 1:
            # This is a burst event
            if final_extension:
                # We have the desired number of leaves and have extended the
                # tree to the next diversification event
                break
            burst_times.append(clock)
            for node in extant_nodes:
                current_state = node.leafward_state
                burst_p = self.burst_probs[current_state]
                u = rng.random()
                if u > burst_p:
                    # This lineage does not diverge at this burst, so skip to
                    # the next
                    continue
                n_children = 2
                if not self.only_bifurcate:
                    burst_mean = self.burst_furcation_poisson_means[current_state]
                    burst_shift = self.burst_furcation_poisson_shifts[current_state]
                    pois_rv = rng_utils.poisson_rv(
                            mean = burst_mean,
                            rng = rng)
                    n_children = pois_rv + burst_shift
                assert n_children > 0
                if n_children > 1:
                    node.time = clock
                    extant_nodes.remove(node)
                    for i in range(n_children):
                        child = node.Node(
                            parent = node,
                            rootward_state = node.leafward_state,
                        )
                        node.add_child(child)
                        extant_nodes.append(child)
        else:
            # This is a lineage-specific event
            lin_rates= lineage_rates[lineage_index]
            event_index = rng_utils.get_weighted_index(lin_rates, rng)

            if (event_index < 2) and final_extension:
                # We have the desired number of leaves and have extended the
                # tree to the next birth/death event
                break
            
            if event_index == 0:
                # lineage-specific birth event
                node = extant_nodes[lineage_index]
                node.time = clock
                extant_nodes.remove(node)
                for i in range(2):
                    child = node.Node(
                        parent = node,
                        rootward_state = node.leafward_state,
                    )
                    node.add_child(child)
                    extant_nodes.append(child)

            elif event_index == 1:
                # lineage-specific death event
                node = extant_nodes[lineage_index]
                node.time = clock
                extant_nodes.remove(node)
                extinct_nodes.append(node)

            elif event_index == 2:
                # lineage-specific state transition
                node = extant_nodes[lineage_index]
                current_state = node.leafward_state
                new_state = sdsd_model.ctmc.draw_transition(current_state)
                node.transition_state(new_state, clock)

            else:
                raise ValueError(f"Unexpected event index: {event_index}")
    if not time_zero_at_root:
        # recurse through tree and reverse time
        # and
        # reverse time in burst_times
        pass
    return root, burst_times
