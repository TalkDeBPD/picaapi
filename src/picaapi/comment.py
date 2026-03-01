from datetime import datetime
from .user import User

class Comment:
    '''
    单条评论。
    '''
    def __init__(self, info):
        self.comic = info['comic']
        self.isTop = info['isTop']
        self.hide = info['hide']
        self.created_at = datetime.fromisoformat(info['created_at']).timestamp()
        self.id = info['id']
        self.isLiked = info['isLiked']
        self.comic = info['_comic']
        self.likesCount = info['likesCount']
        self.totalComments = info['totalComments']
        self.commentsCount = info['commentsCount']
        self.content = info['content']
        self.user = User(info['_user'])


class CommentPage:
    '''
    可分页的评论区。
    '''
    def __init__(self, info):
        self.docs = [Comment(i) for i in info['docs']]
        self.page = info['page']
        self.pages = info['pages']
        self.total = info['total']
        self.limit = info['limit']
