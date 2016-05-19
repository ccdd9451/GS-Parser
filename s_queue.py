#!/usr/bin/env python
# encoding: utf-8

from bs4 import BeautifulSoup
import logging, re, pickle

RE_AMOUNT_BYTES = b'[Aa]bout ([0-9|,]+) results'

RE_AMOUNT = r'[Aa]bout ([0-9|,]+) results'
RE_ID = r'cites=([0-9]+)'
RE_CITED_NUM = r'Cited by ([0-9]+)'
RE_REFINFO = r'q=related:(.*?):scholar'


def Parsing(content):
    soup = BeautifulSoup(content, 'html.parser')
    amounttext = soup.find('div', id='gs_ab_md').text
    amount = int(re.search(RE_AMOUNT, amounttext).group(1).replace(',',''))
    results = soup.findAll('div', class_='gs_ri')
    r = []
    for result in results:
        try:
            fl = list(result.find('div', class_='gs_fl').findAll('a'))
            rd = {}
            rd['name'] = result.h3.a.text
            rd['link'] = result.h3.a['href']
            rd['id'] = int(re.search(RE_ID, fl[0]['href']).group(1))
            rd['cnum'] = int(re.search(RE_CITED_NUM, fl[0].text).group(1))
            rd['refurl'] = re.search(RE_REFINFO, fl[1]['href']).group(1)
            r.append(rd)
        except Exception as e:
            logging.debug('result cant parsed: {}\n\t {}'.format(result, e))
    return r, amount


class defaultlist(list):
    def __init__(self, *awrgs):
        self._fx = PageObj
        self.awrgs = awrgs
        self.results = []
        self.pagenum = None

    def _fill(self, index):
        pagenum = len(self)
        while pagenum <= index:
            self.append(self._fx(pagenum, *self.awrgs))
            pagenum = len(self)

    def __setitem__(self, index, value):
        self._fill(index)
        list.__setitem__(self, index, value)

    def __getitem__(self, index):
        self._fill(index)
        return list.__getitem__(self, index)


class CommObj(object):
    '''
        _para, _if_cached, _qtype, _qkey
        _source, results, numsum
    '''

    def __init__(self, querytype, querykey, para=None):
        self._para = para or {}
        self._if_cached = False
        self._source = None
        self._results = list()
        self.numsum = None
        if querytype in ('q', 'cite'):
            self._qtype = querytype
            self._qkey = querykey
        else:
            raise ValueError('Invalid query type: %s' % querytype)

    def __getstate__(self):
        d = {'_qtype': self._qtype,
             '_qkey': self._qkey,
             '_para': self._para}
        return d

    def __setstate__(self, d):
        CommObj.__init__(self, d['_qtype'], d['_qkey'], para=d['_para'])

    @property
    def cached(self):
        return self._if_cached

    @property
    def source(self):
        if self.cached:
            return self._source
        logging.warning('Not Cached!')
        return None

    @source.setter
    def source(self, source):
        if not self.checkvali(source):
            logging.warning('Not a vaild GS page: {}'
                            .format(source.split(b'<body>')[1][:100]))
            return
        self._source = source
        self._if_cached = True

    @property
    def params(self):
        pdict = {self._qtype: self._qkey}
        pdict.update(self._para)
        return pdict

    def checkvali(self, source):
        self._results, self.numsum = Parsing(source)
        return self._results



class PageObj(CommObj):
    '''
        _para, _if_cached, _qtype, _qkey
        _source, results, numsum, pagenum
    '''
    def __init__(self, pagenum, *awrgs, **kawrgs):
        self.pagenum = pagenum
        super(PageObj, self).__init__(*awrgs, **kawrgs)
        self._para['start'] = pagenum * 20

    def __getstate__(self):
        if not self.cached:
            return self.pagenum, None, super(PageObj, self).__getstate__()
        else:
            return self.pagenum, self._source, super(PageObj, self).__getstate__()

    def __setstate__(self, state):
        pagenum, source, d = state
        super(PageObj, self).__setstate__(d)
        self.pagenum = pagenum
        self.source = source
        self._para['start'] = self.pagenum * 20

    @property
    def results(self):
        return self._results


class SearchObj(CommObj):
    '''
        _para, _if_cached, _qtype, _qkey
        _source, _pages
    '''

    def __init__(self, *awrgs, **kawrgs):
        super(SearchObj, self).__init__(*awrgs, **kawrgs)
        self._pages = defaultlist(*awrgs, **kawrgs)

    def __getstate__(self):
        return self._pages, super(SearchObj, self).__getstate__()

    def __setstate__(self, state):
        self._pages, d = state
        super(SearchObj, self).__setstate__(d)

    def vizd(self):
        return {self._qkey: [str(x['id']) for x in self.results]}

    @property
    def source(self):
        return self._pages[0].source

    @source.setter
    def source(self, source):
        self._pages[0].source = source

    @property
    def cached(self):
        return self._pages[0]._if_cached

    def pages(self, *pagenumiter, update=True):
        for num in pagenumiter:
            if update or not self._pages[num].cached:
                yield self._pages[num]

    def close(self):
        with open('cache/{}.sdb'.format(self._qkey), 'wb') as f:
            pickle.dump(self, f)

    @staticmethod
    def open(key):
        with open('cache/{}.sdb'.format(key), 'rb') as f:
            return pickle.load(f)

    @staticmethod
    def search_with_key(key):
        nsearch = SearchObj('q', key)
        return nsearch

    @staticmethod
    def cited_by_id(idnum):
        idnum = str(int(idnum))  # To make sure it's an figure id
        nsearch = SearchObj('cite', idnum)
        return nsearch

    @property
    def results(self):
        return sum((page.results for page in self._pages), [])


# depercated
# class SQueue(object):
#    '''
#    SQueue is the main controller of Scholar program. SQueue makes it possible that
#    users continue ask datas while driver is working in background. This feather
#    provided a way to use it in a scriptify way.
#    '''
#
#    def __init__(self):
#        '''
#        _comm_queue used to store the list of uncomplete queries, every item in it is a
#        SearchObj or a PageObj which drivers get them before working.
#        '''
#
#        self._search_queue=[]
#        self._page_queue=[]
#
#    def objcheck(func):
#        def warps(self, obj):
#            if isinstance(obj, SearchObj):
#                return func(self, obj, self._search_queue)
#            elif isinstance(obj, PageObj):
#                return func(self, obj, self._page_queue)
#        return warps
#
#    @objcheck
#    def add_queue(self, obj, queue):
#        queue.append(obj)
#
#    @objcheck
#    def add_queue_at_top(self, obj, queue):
#        queue.insert(0, obj)
#
#    def pop_queue(self):
#        logging.debug('A obj is asked poping from queue')
#        if self._search_queue:
#            return self._search_queue.pop(0)
#        elif self._page_queue:
#            return self._page_queue.pop(0)
#        else:
#            logging.info('Stack is empty!')
#            return None
#
#
