#!/usr/bin/env python
# encoding: utf-8

import logging


class CommObj(object):
    def __init__(self, querytype, querykey):
        self._num_per_page = None
        self._req_str = None
        self._if_cached = False
        self._source = None
        if querytype in ('q', 'cite'):
            self._qtype = querytype
            self._qkey = querykey
        else:
            raise ValueError('Invalid query type: %s' % querytype)

    @property
    def cached(self):
        return self._if_cached

    @property
    def source(self):
        if self.cached:
            return self._source
        logging.info('Not Cached!')
        return None

    @source.setter
    def source(self, source):
        self.checkvali(source)
        self._source = source
        if not source:
            self._if_cached = True

    @property
    def params(self):
        return {self._qtype: self._qkey}

    def checkvali(self, source):
        # TODO: check if page is broken
        if True:
            pass
        else:
            raise ValueError('Not a useful page!')


class PageObj(CommObj):
    def __init__(self, pagenum, *awrgs):
        self.pagenum = pagenum
        super(PageObj, self).__init__(*awrgs)


class SearchObj(CommObj):
    def __init__(self, *awrgs):
        super(SearchObj, self).__init__(*awrgs)
        self._pages = [PageObj(0, *awrgs)]

    @property
    def source(self):
        return self._pages[0].source

    @source.setter
    def source(self, source):
        self._pages[0].source = source

    @property
    def cached(self):
        return self._pages[0]._if_cached



class SQueue(object):
    '''
    SQueue is the main controller of Scholar program. SQueue makes it possible that
    users continue ask datas while driver is working in background. This feather
    provided a way to use it in a scriptify way.
    '''

    def __init__(self):
        '''
        _comm_queue used to store the list of uncomplete queries, every item in it is a
        SearchObj or a PageObj which drivers get them before working.
        '''

        self._search_queue=[]
        self._page_queue=[]

    def objcheck(func):
        def warps(self, obj):
            if isinstance(obj, SearchObj):
                return func(self, obj, self._search_queue)
            elif isinstance(obj, PageObj):
                return func(self, obj, self._page_queue)
        return warps

    @objcheck
    def add_queue(self, obj, queue):
        queue.append(obj)

    @objcheck
    def add_queue_at_top(self, obj, queue):
        queue.insert(0, obj)

    def pop_queue(self):
        logging.debug('A obj is asked poping from queue')
        if self._search_queue:
            return self._search_queue.pop(0)
        elif self._page_queue:
            return self._page_queue.pop(0)
        else:
            logging.info('Stack is empty!')
            return None

    def search_key(self, key):
        nsearch = SearchObj('q', key)
        self.add_queue(nsearch)
        return nsearch

    def cited_by_id(self, idnum):
        idnum = str(int(idnum))  # To make sure it's an id
        nsearch = SearchObj('cite', idnum)
        self.add_queue(nsearch)
        return nsearch


class Controller(object):
    '''
       process controller
    '''


