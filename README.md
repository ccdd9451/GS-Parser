# GS-Parser

A practicing project of google scholar parser.

## Code and Examples

### Parsing a keyword:

    >>> proxies = None
    >>> driver = Browser(proxy=proxies)
    >>> emp = Search.search_with_key('some example')
    >>> driver.req_item(emp)
    >>> driver.req_item(emp.pages(*range(0, 5)))
    >>> emp.close()

When close() was called, crawled data would be stored at 'temp/{keyword}.sdb' file. You can rescue those data with import and use SearchObj.open(keyword) function, which provides a off-line support for analysis.

### Parsing a cites:

Unavailable now, Google CAPTCHA is always activated. Finding reasons.

    >>> proxies = None
    >>> driver = Browser(proxy=proxies)
    >>> emp = Search.cited_by_id(17725825958939227007)
    >>> driver.req_item(emp)
    >>> driver.req_item(emp.pages(*range(0, 5)))
    >>> emp.close()

### Drawing relationship

A Graph object is provided, which require SearchObjs input and draw a jpg file with given name. The Graph's draw function is supported by pygraphviz module.
    
    >>> l
    [<SearchObj object at 0xXXXXXXXXX>, <SearchObj object at 0xXXXXXXXXX>, <SearchObj object at 0xXXXXXXXXX>, <SearchObj object at 0xXXXXXXXXX>]
    >>> from s_browser import Graph
    >>> G = Graph(filename='all')
    >>> G.builder(l)
    >>> G.draw()
    
    >>> G1 = G.select(1)
    >>> G1.draw()


