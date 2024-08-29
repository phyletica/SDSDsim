#! /bin/bash

set -e

ntrees=5

sim-SDSD-trees -n "$ntrees" -s 2014 sdsd-config.yml > sd-trees.yml
sim-SDSD-trees -n "$ntrees" -s 2019 bd-config.yml > bd-trees.yml

./plot_trees.R
pdfcrop "all-trees.pdf" "all-trees-cropped.pdf"
