from datetime import datetime


class Page:
    '''
    用于存储哔咔API分页返回的信息。

    Attributes:
        docs(list): 本页内容，具体元素类型与调用方法有关。
        limit(int): 一页的最大可承载数量
        page(int): 页码
        pages(int): 全部页码
        total(int): 总内容量
    '''

    def __init__(self, info: dict, constructor):
        self.docs = [constructor(i) for i in info['docs']]
        self.page = int(info['page']) # 有的返回会出现字符串
        self.pages = info['pages']
        self.total = info['total']
        self.limit = info['limit']


class Picture:
    '''
    用于存储哔咔API返回的图片地址。

    Attributes:
        fileServer(str): 访问的文件服务器，为URL前缀，不以斜杠结尾，返回的仅供参考
        originalName(str): 源文件名称
        path(str): 路径，不以斜杠开头
    '''
    
    def __init__(self, info: dict):
        self.fileServer = info['fileServer']
        self.originalName = info['originalName']
        self.path = info['path']
    
    def url(self, server: str = '') -> str:
        '''
        生成指定图片服务器的URL。

        Args:
            server(str, optional): 指定的图片服务器，如果为空则为默认服务器
        '''

        if server == '': server = self.fileServer
        server = server.replace('https://', '').replace('http://', '') + '/static/' + self.path
        server = 'https://' + server.replace('//', '/')
        return server


class ComicPicture(Picture):
    '''
    针对漫画页面的图片类。
    
    Attributes:
        id(str): 漫画图片ID
    '''

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
        self.likes = info['likesCount']
        self.comments = info.get('commentsCount', info['totalComments'])
        self.content = info['content']
        self.user = User(info['_user'])


class Comic:
    '''
    存储漫画基本信息，用于搜索和列表。

    Attributes:
        id(str): 漫画ID
        title: 标题
        author(str): 作者
        categories(list[str]): 分类
        tags(list[str]): 标签
        thumb(Picture): 封面
        views(int): 浏览次数（绅士指名数）
        likes(int): 赞数
        finished(bool): 完结情况
    '''

    def __init__(self, info: dict):
        self.author = info['author']
        self.categories = info['categories']
        self.finished = info['finished']
        self.likes = info.get('likesCount', info.get('totalLikes', 0))
        self.tags = info['tags']
        self.thumb = Picture(info['thumb'])
        self.title = info['title']
        self.views = info.get('totalViews', 0)
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
        self.isFavourite = info['isFavourite']
        self.isLiked = info['isLiked']


class Eps:
    '''
    存储漫画单话信息。
    '''
    def __init__(self, info: dict):
        self.id = info['_id']
        self.order = info['order']
        self.title = info['title']
        self.updated_at = datetime.fromisoformat(info['updated_at']).timestamp()
