#!/usr/bin/env python
# encoding: utf-8

from s_queue import SearchObj
from pygraphviz import AGraph
from numpy import array

str = input('keys here, separate by comma:\n')
s = set()
d = dict()
for s in str.split(','):
    try:
        l = SearchObj.open(s.strip())
        r = l.vizd()
        d.update(r)

    except Exception:
        pass


A = AGraph(d)
A.layout('circo')
A.draw('temp/a.jpg',format='jpg')
