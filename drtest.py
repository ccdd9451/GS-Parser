# !/usr/bin/env python
#  encoding: utf-8

from s_browser import Browser, Search


proxies = {'http': 'http://127.0.0.1:8087',
           'https': 'https://127.0.0.1:8087'}

driver = Browser(proxy=proxies)

pdx = Search.cited_by_id(17725825958939227007)
driver.req_item(pdx)
driver.req_item(pdx.pages(*range(0, 5)))

pdx.close()




# cited = queue.cited_by_id('12345678')

# a = input()
# queue.wait(pdx).get_cached(pdx)
# queue.wait(cited).get_cached(cited)
#
# get_page = []
# get_page.expand(pdx.get_pages(req_pagenum=range(5)))
# get_page.expand(cited.get_pages(req_pagenum=range(5)))
#
# queue.add_dpage(get_page)
# queue.wait_all_cached().flush()
#
# pdx.export_as_htmls()
# cited.export_as_htmls()
#
#
