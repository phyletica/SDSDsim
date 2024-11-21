#! /bin/bash

set -e

ntrees=5

sdsd_seed=2014
bd_seed=2019

sim-SDSD-trees -n "$ntrees" -s "$sdsd_seed" sdsd-config.yml > sd-trees.yml
sim-SDSD-trees -n "$ntrees" -s "$bd_seed" bd-config.yml > bd-trees.yml

./plot_trees.R
pdfcrop "all-trees.pdf" "all-trees-cropped.pdf"
