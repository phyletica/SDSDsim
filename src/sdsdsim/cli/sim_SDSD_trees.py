#! /usr/bin/env python

import os
import sys
import random
import argparse
import yaml

import sdsdsim


def vet_model_config(model_config):
    required_model_keys = [
        'q',
        'birth_rates',
        'death_rates',
        'burst_rate',
        'burst_probs',
        'burst_furcation_poisson_means',
        'burst_furcation_poisson_shifts',
        'only_bifurcate',
    ]
    for k in model_config.keys():
        if k not in required_model_keys:
            sys.stderr.write(f"ERROR: Unexpected model field: '{k}'\n")
            sys.exit(1)
    for k in required_model_keys:
        if k not in model_config:
            sys.stderr.write(f"ERROR: Model field '{k}' is missing\n")
            sys.exit(1)

def parse_stopping_conditions(d):
    defaults = {
        'max_extant_leaves' : None,
        'max_extinct_leaves' : None,
        'max_total_leaves' : None,
        'max_time' : None,
    }
    all_null = True
    for key, val in d.items():
        if key not in defaults:
            sys.stderr.write(f"ERROR: Unexpected stopping condition: '{key}'\n")
            sys.exit(1)
        if val is not None:
            all_null = False
            if val <= 0:
                sys.stderr.write(
                    f"ERROR: Stopping condition {key} should be positive or "
                    f"null (found {val})\n"
                )
                sys.exit(1)
        defaults[key] = val
    if all_null:
        sys.stderr.write("ERROR: No stopping conditions provided\n")
        sys.exit(1)
    return defaults

def parse_settings(settings_config):
    settings = {}
    settings['keep_extinct_trees'] = settings_config.get(
        'keep_extinct_trees', False)
    settings['prune_extinct_leaves'] = settings_config.get(
        'prune_extinct_leaves', False)
    settings['max_leaves_strict'] = settings_config.get(
        'max_leaves_strict', False)
    stopping_conditions = settings_config.get('stopping_conditions', {})
    settings['stopping_conditions'] = parse_stopping_conditions(
        stopping_conditions)
    for k in settings_config.keys():
        if k not in settings:
            sys.stderr.write(f"ERROR: Unrecognized settings field '{k}'\n")
    return settings

def parse_config(path):
    with open(path, "r") as stream:
        cfg = yaml.safe_load(stream)
    vet_model_config(cfg['model'])
    settings = parse_settings(cfg['settings'])
    cfg['settings'] = settings
    return cfg

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'config_path',
        metavar = 'PATH-TO-CONFIG-FILE',
        type = sdsdsim.argparse_utils.arg_is_file,
        help = ('Path to SDSD model config file.'),
    )
    parser.add_argument(
        '-n', '--number-of-samples',
        action = 'store',
        default = 10,
        type = sdsdsim.argparse_utils.arg_is_positive_int,
        help = ('Number of trees to sample.'),
    )
    parser.add_argument(
        '-s', '--seed',
        action = 'store',
        type = sdsdsim.argparse_utils.arg_is_positive_int,
        help = ('Seed for random number generator.'),
    )
    args = parser.parse_args()

    rng = random.Random()
    if not args.seed:
        args.seed = sdsdsim.rng_utils.get_safe_seed(rng)
    rng.seed(args.seed)

    data = {
        'SDSDsim_version' : sdsdsim.__version__,
        'seed' : args.seed,
    }

    cfg = parse_config(args.config_path)

    prune_extinct_leaves = cfg['settings']['prune_extinct_leaves']
    keep_extinct_trees = cfg['settings']['keep_extinct_trees']
    max_leaves_strict = cfg['settings']['max_leaves_strict']

    data['model'] = cfg['model']
    data['settings'] = cfg['settings']

    model = sdsdsim.model.SDSDModel(**cfg['model'])

    samples = []
    
    while len(samples) < args.number_of_samples:
        survived, tree, burst_times = sdsdsim.model.sim_SDSD_tree(
            rng_seed = rng.random(),
            sdsd_model = model,
            **cfg['settings']['stopping_conditions']
        )
        if (not survived) and (not keep_extinct_trees):
            continue
        if max_leaves_strict:
            mx = cfg['settings']['stopping_conditions']['max_total_leaves']
            if (mx and (tree.number_of_leaves > mx)):
                sys.stderr.write(
                    f"max_total_leaves is {mx} and final shared event resulted "
                    f"in {tree.number_of_leaves} leaves...\n"
                    f"\tDiscarding this simulation!\n"
                )
                continue
            mx = cfg['settings']['stopping_conditions']['max_extant_leaves']
            if (mx and (tree.number_of_extant_leaves > mx)):
                sys.stderr.write(
                    f"max_extant_leaves is {mx} and final shared event resulted "
                    f"in {tree.number_of_extant_leaves} leaves...\n"
                    f"\tDiscarding this simulation!\n"
                )
                continue
            mx = cfg['settings']['stopping_conditions']['max_extinct_leaves']
            if (mx and (tree.number_of_extinct_leaves > mx)):
                # This should never happen, but putting logic in place in case
                # we ever decide to allow shared extinction events
                sys.stderr.write(
                    f"max_extinct_leaves is {mx} and final shared event resulted "
                    f"in {tree.number_of_extinct_leaves} leaves...\n"
                    f"\tDiscarding this simulation!\n"
                )
                continue
        if prune_extinct_leaves:
            tree = tree.prune_extinct_leaves()
        samples.append(
            {
                'tree': tree.as_newick_string(),
                'burst_times': [float(t) for t in burst_times],
            }
        )

    data['trees'] = samples
    yaml.dump(data, stream = sys.stdout, default_flow_style = False)
