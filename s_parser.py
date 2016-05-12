from bs4 import Beautifulsoup
import scholar_queue

class Parsing(object):

    def __init__(self, obj):
        
        self._content = obj.sourse
        self._soup = Beautifulsoup(self.content)

