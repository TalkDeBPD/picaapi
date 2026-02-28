from .picture import *
from .user import User

class Comic:
    def __init__(self, info: dict):
        self.author = info['author']
        self.categories = info['categories']
        self.epsCount = info['epsCount']
        self.finished = info['finished']
        self.likesCount = info['likesCount']
        self.pagesCount = info['pagesCount']
        self.tags = info['tags']
        self.thumb = Picture(info['thumb'])
        self.title = info['title']
        self.totalViews = info['totalViews']
        self.id = info['_id']


class ComicDetailed(Comic):
    def __init__(self, info: dict):
        Comic.__init__(self, info)
        self.description = info['description']
        self.creator = User(info['_creator'])
        self.chineseTeam = info['chineseTeam']
