from bs4 import BeautifulSoup

class Parsing(object):

    def __init__(self, obj):
        self._content = obj.source
        self._soup = BeautifulSoup(self._content, 'html.parser')

