#!/usr/bin/env python
# encoding: utf-8

from browser import Browser
from scholar_queue import SQueue
from s_parser import Parsing


proxies = {'http': 'http://127.0.0.1:8087',
           'https': 'https://127.0.0.1:8087'}

driver = Browser(proxy=proxies)
queue = SQueue()

pdx = queue.search_key('some example')
driver.req_item(pdx)

pdx_parsed = Parsing(pdx)


#cited = queue.cited_by_id('12345678')

#a = input()
#queue.wait(pdx).get_cached(pdx)
#queue.wait(cited).get_cached(cited)
#
#get_page = []
#get_page.expand(pdx.get_pages(req_pagenum=range(5)))
#get_page.expand(cited.get_pages(req_pagenum=range(5)))
#
#queue.add_dpage(get_page)
#queue.wait_all_cached().flush()
#
#pdx.export_as_htmls()
#cited.export_as_htmls()
#
#
