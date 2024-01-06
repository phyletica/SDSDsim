#! /usr/bin/env python

import os
import sys
import math
import random
import pytest

from sdsdsim import node
from sdsdsim.math_utils import is_zero 


class TestHeight:
    def test_height(self):
        t_l1 = 10.0
        t_l2 = 9.0
        t_l3 = 7.0
        t_l4 = 5.0
        t_l5 = 4.0
        l1 = node.Node(time = t_l1)
        l2 = node.Node(time = t_l2)
        l3 = node.Node(time = t_l3)
        l4 = node.Node(time = t_l4)
        l5 = node.Node(time = t_l5)

        t_i1 = 8.0
        t_i2 = 6.0
        t_i3 = 3.0
        t_r = 1.0

        i1 = node.Node(time = t_i1)
        i2 = node.Node(time = t_i2)
        i3 = node.Node(time = t_i3)

        i1.add_child(l1)
        i1.add_child(l2)
        i2.add_child(i1)
        i2.add_child(l3)
        i3.add_child(l4)
        i3.add_child(l5)

        root = node.Node(time = t_r)
        root.seed_time = 0.0
        root.add_child(i2)
        root.add_child(i3)

        assert root.height == 9.0

        assert l1.height == 0.0
        assert l2.height == 1.0
        assert l3.height == 3.0
        assert l4.height == 5.0
        assert l5.height == 6.0

        assert i1.height == 2.0
        assert i2.height == 4.0
        assert i3.height == 7.0

        assert root.number_of_leaves == 5
