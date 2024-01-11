#! /usr/bin/env python

from sdsdsim import model

sdsd_model = model.SDSDModel(
        q = [
            [-3.0, 3.0],
            [3.0, -3.0],
        ],
        birth_rates = [1.0, 1.0],
        death_rates = [0.7, 0.7],
        burst_rate = 0.7,
        burst_probs = [0.1, 0.8],
        burst_furcation_poisson_means = [1.0, 2.0],
        burst_furcation_poisson_shifts = [2, 2],
        only_bifurcate = False,
)

seed = 12
n_leaves = 30
include_root_annotations = True

survived, root, burst_times = model.sim_SDSD_tree(rng_seed=seed, sdsd_model=sdsd_model, max_extant_leaves=n_leaves)

while not survived:
    seed += 1
    survived, root, burst_times = model.sim_SDSD_tree(rng_seed=seed, sdsd_model=sdsd_model, max_extant_leaves=n_leaves)

with open("tmp1.tre", 'w') as out:
    root.write_newick(out, include_root_annotations=include_root_annotations)
    out.write(";\n")

t = root.prune_extinct_leaves()

with open("tmp2.tre", 'w') as out:
    root.write_newick(out, include_root_annotations=include_root_annotations)
    out.write(";\n")
with open("tmp3.tre", 'w') as out:
    t.write_newick(out, include_root_annotations=include_root_annotations)
    out.write(";\n")
    

