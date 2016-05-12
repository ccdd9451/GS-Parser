#!/usr/bin/env python
# encoding: utf-8

from unittest import TestCase
from browser import Browser
from scholar_queue import SQueue


import time
import asyncio

proxies = {'http': 'http://127.0.0.1:8087',
           'https': 'https://127.0.0.1:8087'}
class TestBrowser(TestCase):

    def test_init_2(self):
        print('debug begin')
        s = Browser(proxy=proxies, actiontime = 5)
        q = SQueue()
        s.add_queue(q)
        s.startcache()
        print('cache started')
        time.sleep(20)
        print("time's up")
        s.pausecache()
