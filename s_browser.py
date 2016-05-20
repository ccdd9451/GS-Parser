# !/usr/bin/env python
# encoding: utf-8

import logging
import time
import random
import os
import re
import pickle
from bs4 import BeautifulSoup
from collections import Iterable, defaultdict

import requests
from http.cookiejar import LWPCookieJar


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s')
PYTHONASYNCIODEBUG = True
ENABLE_BACKGROUND_WORK = False

MAX_RETRIES = 1
WAIT_AFTER_INCONNECTED = False
RESET_COOKIES = False
CACHE_HTML_FILES = True

ENV_HEADER = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'en-us,en;q=0.5',
    'Connection': 'keep-alive',
    'DNT': '1',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.110 Safari/537.36'}

SCH_SETTINGS = {'url': r'https://scholar.google.com/scholar_settings',
                'param': None}

SCH_SETTINGS_REQUIREMENT = {'url': r'https://scholar.google.com/schhp',
                            'param': {'num': '20', 'sciifh': '1'}}

URL_SCHOLAR = r'https://scholar.google.com/ncr'
URL_SEARCHING = r'https://scholar.google.com/scholar'

COOKIE_FILE = r'cache/cookies'


class ProcessFailedError(Exception):
    pass


class Browser(object):
    '''
    Return a Browser instance used to connect with Google Scholar,
    which automatically:
        [1]sets language to English,
        [2]shows bibliographical links to Refman,
        [3]excludes patents
        [4]provides 20 results with any request.
    :param proxy: the proxy provided for crossing GFW, goagent was seleted in testing
        proxy formatted as {'http': 'Address to http', 'https': 'Address'} like,
        Socks5 method are unsupported in module `Requests'
    '''

    def __init__(self, proxy=None, actiontime=15, webdriver='requests'):
        logging.debug('Browser init begin')

        # Init Web Datas
        self.s = requests.session()
        os.makedirs(os.path.split(COOKIE_FILE)[0], exist_ok=True)
        self.s.cookies = LWPCookieJar(COOKIE_FILE)
        self.header = {}
        self.header.update(ENV_HEADER)
        self.param = {
            'as_vis': '1',  # as_vis controls whether a citation is included
            'hl': 'en',
            'as_sdt': '1,5'}  # as_sdt controls patent including or maybe others I haven't figured.
        self.proxies = proxy if proxy else None
        assert isinstance(proxy, dict)
        if webdriver != 'requests':  # Only requests provided, further function
            logging.error('Webdriver option {} not provided, use default\
                          driver requests instead'.format(webdriver))

        # Init other datas
        self._queue = None  # Depercated
        self._last_time = time.time()
        self._get_failed_time = 0
        self.actiontime = actiontime

        # Cookie check and regen
        if RESET_COOKIES or not os.path.exists(COOKIE_FILE):
            self._cookie_init()
        else:
            self.param.update({'num': '20'})
            logging.info('Cookie exists, Reuse the last cookie file.')
            self.s.cookies.load()

    def _cookie_init(self):
        # Initialize Google Scholar, making it more human-like
        logging.debug('Cookie Initiating')

        while True:
            try:
                self.debug_welcome = self._get_url(URL_SCHOLAR)
                self.debug_settings_content = self._get_url(**SCH_SETTINGS)  # get cookies and set options
                self.debug_settings_done = self._get_url(**SCH_SETTINGS_REQUIREMENT)
                self.param.update({'num': '20'})
                break
            except ConnectionError as e:
                errcode, msg = e.args
                if errcode == 0:
                    logging.warning(msg)
                elif errcode == 1:
                    logging.error(msg)
                    raise ProcessFailedError()
                else:
                    raise

    def checktime(func):
        def warp(self, *args, **kargs):
            print('times begin line:118')
            now_time = time.time()
            interval_time = now_time - self._last_time
            delaytime = self.delaytime_generator()
            if interval_time < delaytime:
                time.sleep(interval_time)
            return func(self, *args, **kargs)
        return warp

    @checktime
    def _get_url(self, url, param=None, header=None):
        params = dict(self.param)
        params.update(param or {})
        headers = dict(self.header)
        headers.update(header or {})

        try:
            logging.debug('Start connecting with \n\t url: %s \n\t params: %s' %
                          (url, str(params)))
            req = self.s.get(url,
                             params=params,
                             headers=headers,
                             proxies=self.proxies,
                             verify=False)  # TODO: cert verifing
            self._get_failed_time = 0
            self.s.cookies.save()
            self._debug_cachefile(req)
            print('file write success:line 144')
            return req.content

        except ConnectionError as e:
            logging.warning('Connecting failed with Errors %s' % str(e))
            self._get_failed_time+=1
            if self._get_failed_time >= MAX_RETRIES:
                raise ConnectionError(1, 'Max retries exceeded')
            raise ConnectionError(0, 'Retrieve data failed')

    def _debug_cachefile(self, req):
        if CACHE_HTML_FILES:
            os.makedirs('temp', exist_ok=True)
            w_address = r'temp/' + req.url.split('/', 3)[3].replace('/', '-') + r'_store.html'
            logging.info('html file stored at %s' % w_address)
            with open(w_address, 'wb') as f:
                f.write(req.content)

    def delaytime_generator(self):
        delaytime = random.randint(5, self.actiontime)
        logging.debug('Wait time %ds before next move' % delaytime)
        return delaytime

    def req_item(self, req_obj):
        if isinstance(req_obj, Iterable):
            for r in req_obj:
                self.req_item(r)
        else:
            content = self._get_url(URL_SEARCHING, param=req_obj.params)
            req_obj.source = content

    '''
        Depercated functions

    def add_queue(self, queue):
        assert isinstance(queue, SQueue)
        self._queue = queue

    def startcache(self, loop=None, executor=None):
        self._pausetask = False
        if loop is None:
            loop = asyncio.get_event_loop()
            loop.set_debug(True)
        if ENABLE_BACKGROUND_WORK:
            self._run = loop.run_in_executor(executor, self.req_item)
        else:
            loop.run_until_complete(self.asy_req_item())

    def pausecache(self):
        self._pausetask = True

    def close(self):
        pass
    '''


############# Data Part ###############


RE_AMOUNT_BYTES = b'[Aa]bout ([0-9|,]+) results'
RE_AMOUNT = r'[Aa]bout ([0-9|,]+) results'
RE_ID = r'cites=([0-9]+)'
RE_CITED_NUM = r'Cited by ([0-9]+)'
RE_REFINFO = r'q=related:(.*?):scholar'


def Parsing(content):
    try:
        soup = BeautifulSoup(content, 'html.parser')
        amounttext = soup.find('div', id='gs_ab_md').text
        amount = int(re.search(RE_AMOUNT, amounttext).group(1).replace(',', ''))
        results = soup.findAll('div', class_='gs_ri')
    except Exception:
        return None, None
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


class Graph(defaultdict):
    '''
    stored as {target: source(s)} format
    '''
    def __init__(self, pkg=None):
        super(Graph, self).__init__(set)
        if pkg:
            self.builder(pkg)

    def itercheck(func):
        def warp(self, pkg):
            if isinstance(pkg, Iterable):
                for p in pkg:
                    func(self, p)
            else:
                func(self, pkg)
        return warp

    @itercheck
    def builder(self, pkg):
        target, source = pkg
        if isinstance(source, (str, int)):
            self[target].add(str(source))
        elif isinstance(source, set):
            self[target].update(source)

    @itercheck
    def reversed_builder(self, pkg):
        source, targets = pkg
        for target in targets:
            self[target].add(source)

    def select(self, count):
        return Graph((item, self[item]) for item in self
                     if len(self[item]) > count)

    def to_tree(self):
        d = defaultdict(dict)
        for (target, source) in self.items():
            print(target, source)
            for item in source:
                print('\t', source)
                d[item].update({target: None})
        return d


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

    def all_cites(self):
        return self._qkey, [str(x['id']) for x in self.results]

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

################# Control Part ################


PROXIES = {'http': 'http://127.0.0.1:8087',
           'https': 'https://127.0.0.1:8087'}


class Search(object):

    def __init__(self):
        self.driver = Browser(proxy=PROXIES)
        self.future_get = set()

    @staticmethod
    def search_with_key(key):
        nsearch = SearchObj('q', key)
        return nsearch

    @staticmethod
    def cited_by_id(idnum):
        idnum = str(int(idnum))  # To make sure it's an figure id
        nsearch = SearchObj('cite', idnum)
        return nsearch

#    def cget(self, sobj, deep=2, pages=5):  # TODO
#        q = lambda x: self.driver.req_item(x.pages(*range(pages), update=False))
#        q(sobj)
#        _, future_get = sobj.all_cites()
#        for _ in range(deep):
#
#            for cite in future_get:
#                r = self.cited_by_id(cite)
#                q(r)
