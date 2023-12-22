#! /usr/bin/env python

import random
import numpy as np

from sdsdsim import GLOBAL_RNG, rng_utils
from sdsdsim.ctmc import CTMC
from sdsdsim.node import Node


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
        self.ctmc = CTMC(q)
        n_states = self.ctmc.n_states
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
):
    clock = 0.0
    rng = random.Random(rng_seed)
    root_state = sdsd_model.ctmc.draw_random_state(rng)
    root = Node(
        label = "root",
        rootward_state = root_state,
    )
    root.seed_time = clock
    extant_nodes = [root]
    extinct_nodes = []
    burst_times = []
    survived = True

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
            birth_rate = sdsd_model.birth_rates[current_state]
            death_rate = sdsd_model.death_rates[current_state]
            transition_rate = sdsd_model.ctmc.get_rate_from(current_state)
            lineage_total_rates.append(
                birth_rate + death_rate + transition_rate
            )
            lineage_rates.append(
                (birth_rate, death_rate, transition_rate)
            )
        lineage_total_rates.append(sdsd_model.burst_rate)
        lineage_total_rates = np.array(lineage_total_rates)
        positive_rate_indices = np.where(lineage_total_rates > 0.0)[0]
        positive_rates = lineage_total_rates[positive_rate_indices]
        lineage_wait_times = [rng.expovariate(r) for r in positive_rates]
        wait_time = np.min(lineage_wait_times)
        if (max_time is not None) and (clock + wait_time > max_time):
            clock = max_time
            break
        clock += wait_time
        lineage_index = positive_rate_indices[np.argmin(lineage_wait_times)]
        if lineage_index == len(lineage_total_rates) - 1:
            # This is a burst event
            if final_extension:
                # We have the desired number of leaves and have extended the
                # tree to the next diversification event
                break
            burst_times.append(clock)
            for node in extant_nodes:
                current_state = node.leafward_state
                burst_p = sdsd_model.burst_probs[current_state]
                u = rng.random()
                if u > burst_p:
                    # This lineage does not diverge at this burst, so skip to
                    # the next
                    continue
                n_children = 2
                if not sdsd_model.only_bifurcate:
                    burst_mean = sdsd_model.burst_furcation_poisson_means[current_state]
                    burst_shift = sdsd_model.burst_furcation_poisson_shifts[current_state]
                    pois_rv = rng_utils.poisson_rv(
                            mean = burst_mean,
                            rng = rng)
                    n_children = pois_rv + burst_shift
                assert n_children > 0
                if n_children > 1:
                    node.time = clock
                    node.is_burst_node = True
                    extant_nodes.remove(node)
                    for i in range(n_children):
                        child = Node(
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
                    child = Node(
                        rootward_state = node.leafward_state,
                    )
                    node.add_child(child)
                    extant_nodes.append(child)

            elif event_index == 1:
                # lineage-specific death event
                node = extant_nodes[lineage_index]
                node.time = clock
                node.is_extinct = True
                extant_nodes.remove(node)
                extinct_nodes.append(node)
                if len(extant_nodes) == 0:
                    survived = False
                    break

            elif event_index == 2:
                # lineage-specific state transition
                node = extant_nodes[lineage_index]
                current_state = node.leafward_state
                new_state = sdsd_model.ctmc.draw_transition(current_state)
                node.transition_state(new_state, clock)

            else:
                raise ValueError(f"Unexpected event index: {event_index}")
    # Populate node and state change heights
    for node in root:
        if node.time is None:
            assert node.is_leaf()
            assert not node.is_extinct
            node.time = clock
            node.height = 0.0
        else:
            node.height = clock - node.time
        assert not node.state_change_heights
        for state_change_t in node.state_change_times:
            node.state_change_heights.append(clock - state_change_t)
    return survived, root, burst_times
