# !/usr/bin/env python
# encoding: utf-8

import logging
import time
import random
import os

import requests
from http.cookiejar import LWPCookieJar


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s')
PYTHONASYNCIODEBUG = True
ENABLE_BACKGROUND_WORK = False

MAX_RETRIES = 1
WAIT_AFTER_INCONNECTED = False
RESET_COOKIES = True
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
                            'param': {'num': '20'}}

URL_SCHOLAR = r'https://scholar.google.com/ncr'
URL_SEARCHING = r'https://scholar.google.com/scholar'

COOKIE_FILE = r'cache/cookies'

debug_item = None  # Use for debug in Python shell

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
        if webdriver != 'requests': # Only requests provided
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


