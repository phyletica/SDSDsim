#! /usr/bin/env python

import os
import sys
import pytest

from sdsdsim import math_utils


class TestIsZero:
    def test_true(self):
        assert math_utils.is_zero(1.0, 1.0)
        assert math_utils.is_zero(-1.0, 1.0)
        assert math_utils.is_zero(1e-11, 1e-11)
        assert math_utils.is_zero(-1e-11, 1e-11)
        assert math_utils.is_zero(1e-11, 1e-10)
        assert math_utils.is_zero(-1e-11, 1e-10)

    def test_false(self):
        assert not math_utils.is_zero(1.000000000000001, 1.0)
        assert not math_utils.is_zero(-1.000000000000001, 1.0)
        assert not math_utils.is_zero(1.1e-11, 1e-11)
        assert not math_utils.is_zero(-1.1e-11, 1e-11)
        assert not math_utils.is_zero(1e-9, 1e-10)
        assert not math_utils.is_zero(-1e-9, 1e-10)
