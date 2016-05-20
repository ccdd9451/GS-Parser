#!/usr/bin/env python
# encoding: utf-8


import pickle

with open('df.db', 'rb') as f:
    l = pickle.load(f)
count = l.count()
lt = l.T
lt['count']=count
a = lt[lt['count']>1]
d = dict()
for i in a.columns:
    b = a[(a[i] == True)][i]
    d.update({b.name: {x: None for x in b.index}})
