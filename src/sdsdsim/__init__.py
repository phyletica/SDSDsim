#! /usr/bin/env python

import random
import logging

from nephila._version import __version__

logging.getLogger(__name__).addHandler(logging.NullHandler())

GLOBAL_RNG = random.Random()

