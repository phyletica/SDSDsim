#! /usr/bin/env python

def is_zero(x, tolerance = 1e-09):
    return abs(x) <= abs(tolerance)
