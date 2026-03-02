from datetime import datetime


class Page:
    def __init__(self, info: dict, constructor):
        self.docs = [constructor(i) for i in info['docs']]


class Picture:
    def __init__(self, info: dict):
        self.fileServer = info['fileServer']
        self.originalName = info['originalName']
        self.path = info['path']
    
    @property
    def url(self) -> str:
        return self.fileServer + '/' + self.path


class ComicPicture(Picture):
    def __init__(self, info: dict):
        Picture.__init__(self, info['media'])
        self.id = info['_id']


class User:
    '''
    用户信息。
    '''
    def __init__(self, info: dict):
        # TODO: 这个不返回avatar的情况怎么办啊
        self.avatar = Picture(info['avatar']) if 'avatar' in info else None
        self.characters = info['characters']
        self.exp = info['exp']
        self.gender = info['gender']
        self.level = info['level']
        self.name = info['name']
        self.role = info['role']
        self.slogan = info['slogan'] if 'slogan' in info else ''
        self.title = info['title']
        self.verified = info['verified']
        self.id = info['_id']


class Profile(User):
    '''
    当前登录账号的个人信息。
    '''
    def __init__(self, info):
        User.__init__(self, info)
        self.isPunched = info['isPunched']
        self.birthday = datetime.fromisoformat(info['birthday']).timestamp()
        self.created_at = datetime.fromisoformat(info['created_at']).timestamp()


class Comment:
    '''
    单条评论。
    '''
    def __init__(self, info: dict):
        '''
        从API返回的JSON构造。

        Args:
            info: (dict[str, Any]): 单条comment的JSON字典
        '''
        self.isTop = info['isTop']
        self.hide = info['hide']
        self.created_at = datetime.fromisoformat(info['created_at']).timestamp()
        self.id = info['id']
        self.isLiked = info['isLiked']
        self.comic = info['_comic']
        self.likesCount = info['likesCount']
        self.commentsCount = info['commentsCount']
        self.totalComments = info.get('totalComments', self.commentsCount)
        self.content = info['content']
        self.user = User(info['_user'])


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


class Eps:
    '''
    存储漫画单话信息。
    '''
    def __init__(self, info: dict):
        self.id = info['_id']
        self.order = info['order']
        self.title = info['title']
        self.updated_at = datetime.fromisoformat(info['updated_at']).timestamp()
