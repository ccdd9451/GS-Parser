#!/usr/bin/env python
# encoding: utf-8

import pickle
from pygraphviz import AGraph
from s_browser import Graph

with open('cache/ml_sum.sdb', 'rb') as f:
    l1 = pickle.load(f)

l = [x.all_cites() for x in l1]
G = Graph()
G.reversed_builder(l)
s = G.select(1)
d = s.to_tree()

A = AGraph(d)
A.draw('temp/twopi.jpg', format='jpg', prog='twopi')
