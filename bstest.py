#!/usr/bin/env python
# encoding: utf-8

from scholar_queue import SearchObj
from s_parser import Parsing

pdx = SearchObj('q', 'aaa')
with open(r'temp/example.html', 'rb') as f:
    pdx.source = f.read()

p = Parsing(pdx)


