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

## Controlling state-dependent rates of shared and multifurcating divergences

The model parameter `burst_rate` controls the rate at which ``burst events''
occur. There is only one `burst_rate` that is shared across all states.
When a burst event occurs, each extant lineage at that time has the opportunity
to diverge into 2 or more descendant lineages.

There are two ways to control how "burstiness" of lineages of each character
state.

### Controlling state-dependent burst rates with `burst_probs`

Here's an example `model` configuration with two character states, let's call
them A and B, where we will use the `burst_probs` settings to make lineages in
State B much more likely to diverge at burst events:

    model:
      q : [ [ -1.0,  1.0 ],
            [  1.0, -1.0 ] ]
      birth_rates : [1.0, 1.0]
      death_rates : [0.5, 0.5]
      burst_rate : 0.5
      burst_probs : [0.1, 0.7]
      burst_furcation_poisson_means : [1.0, 1.0]
      burst_furcation_poisson_shifts : [2, 2]
      only_bifurcate : False

States A and B have the same birth and death rates and burst Poisson
distribution settings.
The only difference is that lineages in State A and B have a 0.1 and 0.7
probability of diverging at each burst event, respectively.

**IF** a lineage does diverge at a burst event, the two
`burst_furcation_poisson` settings control how it will diverge.
With the settings

    burst_furcation_poisson_means : [1.0, 1.0]
    burst_furcation_poisson_shifts : [2, 2]

the number of descendent lineages created by a lineage that diverges at a burst
event (in either State A or B) is determined by a Poisson distribution with
mean of 1 and right-shifted so that the minimum number is 2 (so in this case,
the actual mean will be 3).
Shifting the Poisson distribution to have a minimum of 2 (rather than 0)
ensures that every divergence leads to at least a bifurcation (but trifurcation
on average).

### Controlling state-dependent burst rates with Poisson settings 

Here's an alternative config, where we make lineages in State B more "bursty"
using the Poisson distribution settings, rather than the `burst_prob` settings.

    model:
      q : [ [ -1.0,  1.0 ],
            [  1.0, -1.0 ] ]
      birth_rates : [1.0, 1.0]
      death_rates : [0.5, 0.5]
      burst_rate : 0.5
      burst_probs : [1.0, 1.0]
      burst_furcation_poisson_means : [0.1, 2.0]
      burst_furcation_poisson_shifts : [1, 1]
      only_bifurcate : False

You can see that lineages in State A and B will always "do something" at
a burst event (i.e., `burst_prob = [1.0, 1.0]`), but the minimum number
of descendant lineages they leave behind is now 1
(i.e., `burst_furcation_poisson_shifts : [1, 1]`).
So, the propensity of lineages in State A and B to actually diverge (at least
bifurcate) at burst events is entirely controlled
by the mean of the Poisson distribution on the number of descendent lineages
that are produced when a lineage hits a burst event.
Lineages in State A will most often leave only 1 descendent lineage (i.e., do
nothing) when crossing a burst event; a Poisson distribution with a mean of 0.1
and shifted to the right by 1, so the actual mean number of lineages will be
1.1.
Lineages in State A will, on average, trifurcate when crossing a burst event; a
Poisson distribution with a mean of 2 and shifted to the right by 1 (an
realized mean of 3).

**NOTE:** If the `only_bifurcate` option is set to `True`, all burst
divergences will be strictly bifurcating, and so the Poisson settings are
ignored. When `only_bifurcate = True`, `burst_probs` is the **only** way to
allow lineages with different character states to vary in their burstiness.

### Controlling state-dependent burst rates with a mix of settings

The examples above show that the `burst_probs` and Poisson settings offer two
ways of modeling differing "burstiness" among character states.
However, they are not mutually exclusive and can be mixed.
Here's an example where `burst_probs` makes lineages in character state B
7-times more likely to diverge at burst events, and when a burst divergence
occurs, lineages in State B will, on average, trifurcate (Poisson distribution
with a mean of 3), whereas lineages in State A most often bifurcate (Poisson
with a mean of 2.1):

    model:
      q : [ [ -1.0,  1.0 ],
            [  1.0, -1.0 ] ]
      birth_rates : [1.0, 1.0]
      death_rates : [0.5, 0.5]
      burst_rate : 0.5
      burst_probs : [0.1, 0.7]
      burst_furcation_poisson_means : [0.1, 1.0]
      burst_furcation_poisson_shifts : [2, 2]
      only_bifurcate : False
