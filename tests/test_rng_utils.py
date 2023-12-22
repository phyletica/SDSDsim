#! /usr/bin/env python

import os
import sys
import math
import random
import pytest

from sdsdsim import rng_utils
from sdsdsim.math_utils import is_zero 


class SampleSummarizer(object):
    count = 0
    def __init__(self, samples = None):
        self.__class__.count += 1
        self.name = self.__class__.__name__ + '-' + str(self.count)
        self._min = None
        self._max = None
        self._n = 0
        self._mean = 0.0
        self._sum_devs_2 = 0.0
        self._sum_devs_3 = 0.0
        self._sum_devs_4 = 0.0
        if samples:
            self.update_samples(samples)
    
    def add_sample(self, x):
        n = self._n + 1
        d = x - self._mean
        d_n = d / n
        d_n2 = d_n * d_n
        self._mean = self._mean + d_n
        first_term =  d * d_n * self._n
        self._sum_devs_4 += (first_term * d_n2 * ((n * n) - (3 * n) + 3)) + \
                (6 * d_n2 * self._sum_devs_2) - (4 * d_n * self._sum_devs_3)
        self._sum_devs_3 += (first_term * d_n * (n - 2)) - \
                (3 * d_n * self._sum_devs_2)
        self._sum_devs_2 += first_term
        self._n = n
        if not self._min:
            self._min = x
        elif x < self._min:
            self._min = x
        if not self._max:
            self._max = x
        elif x > self._max:
            self._max = x

    def update_samples(self, x_iter):
        for x in x_iter:
            self.add_sample(x)

    def _get_n(self):
        return self._n
    
    n = property(_get_n)

    def _get_min(self):
        return self._min

    def _get_max(self):
        return self._max

    minimum = property(_get_min)
    maximum = property(_get_max)
    
    def _get_mean(self):
        if self._n < 1:
            return None
        return self._mean
    
    def _get_variance(self):
        if self._n < 1:
            return None
        if self._n == 1:
            return float('inf')
        return (self._sum_devs_2 / (self._n - 1))

    def _get_std_dev(self):
        if self._n < 1:
            return None
        return math.sqrt(self._get_variance())

    def _get_pop_variance(self):
        if self._n < 1:
            return None
        return (self._sum_devs_2 / self._n)

    mean = property(_get_mean)
    variance = property(_get_variance)
    pop_variance = property(_get_pop_variance)
    std_deviation = property(_get_std_dev)

    def _get_skewness(self):
        return ((self._sum_devs_3 * math.sqrt(self._n)) / \
                (self._sum_devs_2 ** (float(3)/2)))
    def _get_kurtosis(self):
        return (((self._n * self._sum_devs_4) / (self._sum_devs_2 ** 2)) - 3)

    skewness = property(_get_skewness)
    kurtosis = property(_get_kurtosis)

class TestGetWeightedIndex:
    def test_uniform(self):
        rng = random.Random(1)
        weights = [3, 3, 3, 3]
        counts = [0 for i in range(len(weights))]
        n = 100000
        for rep in range(n):
            idx = rng_utils.get_weighted_index(weights, rng)
            counts[idx] += 1
        props = [c / n for c in counts]
        for p in props:
            assert is_zero(p - 1.0 / len(weights), 0.005)

    def test_nonuniform(self):
        rng = random.Random(1)
        weights = [5, 1, 3, 1]
        expected = [ w / sum(weights) for w in weights ]
        counts = [0 for i in range(len(weights))]
        n = 100000
        for rep in range(n):
            idx = rng_utils.get_weighted_index(weights, rng)
            counts[idx] += 1
        props = [c / n for c in counts]
        for i in range(len(weights)):
            assert is_zero(props[i] - expected[i], 0.005) 

    def test_zero(self):
        rng = random.Random(1)
        weights = [5, 0, 3, 2]
        expected = [ w / sum(weights) for w in weights ]
        counts = [0 for i in range(len(weights))]
        n = 100000
        for rep in range(n):
            idx = rng_utils.get_weighted_index(weights, rng)
            counts[idx] += 1
        props = [c / n for c in counts]
        for i in range(len(weights)):
            assert is_zero(props[i] - expected[i], 0.005) 
        assert props[1] == 0.0


class TestPoissonRV:
    def test_1(self):
        rng = random.Random(1)
        mean = 1.0
        n = 1000000
        ss = SampleSummarizer()
        for rep in range(n):
            n = rng_utils.poisson_rv(mean, rng)
            ss.add_sample(n)
        assert is_zero(mean - ss.mean, 0.001)
        assert is_zero(mean - ss.variance, 0.001)

    def test_01(self):
        rng = random.Random(1)
        mean = 0.1
        n = 1000000
        ss = SampleSummarizer()
        for rep in range(n):
            n = rng_utils.poisson_rv(mean, rng)
            ss.add_sample(n)
        assert is_zero(mean - ss.mean, 0.001)
        assert is_zero(mean - ss.variance, 0.001)

    def test_2(self):
        rng = random.Random(1)
        mean = 2.0
        n = 1000000
        ss = SampleSummarizer()
        for rep in range(n):
            n = rng_utils.poisson_rv(mean, rng)
            ss.add_sample(n)
        assert is_zero(mean - ss.mean, 0.001)
        assert is_zero(mean - ss.variance, 0.001)

    def test_underflow(self):
        rng_utils.LN_MIN_FLOAT = -1.1

        rng = random.Random(1)
        mean = 3.0
        n = 1000000
        ss = SampleSummarizer()
        for rep in range(n):
            n = rng_utils.poisson_rv(mean, rng)
            ss.add_sample(n)
        assert is_zero(mean - ss.mean, 0.001)
        assert is_zero(mean - ss.variance, 0.001)

        rng_utils.LN_MIN_FLOAT = math.log(rng_utils.MIN_FLOAT)
