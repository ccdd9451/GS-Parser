#!/usr/bin/env python
# encoding: utf-8

import pickle
from s_browser import Graph

with open('cache/ml_sum.sdb', 'rb') as f:
    l = pickle.load(f)

l = [x.vizd2() for x in l]
G = Graph()
G.reversed_builder(l)
