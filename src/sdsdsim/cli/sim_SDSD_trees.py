#! /usr/bin/env python

import os
import sys
import random
import argparse
import yaml

from sdsdsim import model
from sdsdsim import argparse_utils
from sdsdsim import __version__


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'config_path',
        metavar = 'PATH-TO-CONFIG-FILE',
        type = argparse_utils.arg_is_file,
        help = ('Path to SDSD model config file.'),
    )
    parser.add_argument(
        '-n', '--number-of-reps',
        action = 'store',
        default = 10,
        type = argparse_utils.arg_is_positive_int,
        help = ('Number of trees to simulate.'),
    )
    parser.add_argument(
        '-s', '--seed',
        action = 'store',
        type = argparse_utils.arg_is_positive_int,
        help = ('Seed for random number generator.'),
    )
    args = parser.parse_args()

    rng = random.Random()
    if not args.seed:
        args.seed = nephila.rng_utils.get_safe_seed(rng)
    rng.seed(args.seed)

    data = {
        'version' : __version__,
        'seed' : args.seed,
    }

    with open(args.config_path, "r") as stream:
        cfg = yaml.safe_load(stream)

    data['model'] = cfg['model']
    data['stopping_conditions'] = cfg['stopping_conditions']

    model = model.SDSDModel(**cfg['model'])
    print(cfg)
