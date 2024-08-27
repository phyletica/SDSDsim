#! /bin/bash

set -e

ntrees=5

sim-SDSD-trees -n "$ntrees" -s 1 sdsd-config.yml > sd-trees.yml
sim-SDSD-trees -n "$ntrees" -s 2 bd-config.yml > bd-trees.yml
