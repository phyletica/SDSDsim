# SDSDsim (State-dependent shared diversification simulations)

Simulate trees under a state-dependent birth-death process generalized to allow
shared and multifurcating divergences.

## Dev setup

Use conda (or faster mamba) to create dev environment:

    cd SDSDsim 
    mamba env create --name SDSD-dev --file envs/environment.yml
    mamba env update --name SDSD-dev --file envs/SDSD-dev-extras.yml --prune

To be able to plot character-mapped trees, also add R and Phytools dependencies:

    mamba env update --name SDSD-dev --file envs/SDSD-R-plotting-extras.yml --prune

Next, install SDSDsim into the conda environment in "editable" mode.
This allows you to edit the SDSDsim source code and test your changes on the
fly without having to reinstall SDSDsim.

    conda activate SDSD-dev
    pip install --editable .

Running the test suite:

    cd SDSDsim
    conda activate SDSD-dev
    pytest
