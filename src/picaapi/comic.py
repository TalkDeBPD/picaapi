from datetime import datetime
from .picture import *
from .user import User


class Comic:
    '''
    存储漫画基本信息，用于搜索和列表。
    '''
    def __init__(self, info: dict):
        self.author = info['author']
        self.categories = info['categories']
        self.finished = info['finished']
        self.likesCount = info['likesCount']
        self.tags = info['tags']
        self.thumb = Picture(info['thumb'])
        self.title = info['title']
        self.id = info['_id']


class ComicDetailed(Comic):
    '''
    存储漫画完整信息，用于漫画详情页。
    '''
    def __init__(self, info: dict):
        Comic.__init__(self, info)
        self.description = info['description']
        self.creator = User(info['_creator'])
        self.chineseTeam = info['chineseTeam']
        self.epsCount = info['epsCount']
        self.pagesCount = info['pagesCount']
        self.updated_at = datetime.fromisoformat(info['updated_at']).timestamp
        self.created_at = datetime.fromisoformat(info['created_at']).timestamp
        self.totalViews = info['totalViews']


class ComicListPage:
    '''
    用于需要分页的漫画列表，包括搜索。
    '''
    def __init__(self, info):
        self.docs = [Comic(i) for i in info['docs']]
        self.page = info['page']
        self.pages = info['pages']
        self.total = info['total']
        self.limit = info['limit']
