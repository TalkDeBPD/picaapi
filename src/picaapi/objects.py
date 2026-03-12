from datetime import datetime
from typing import TypeVar, Generic, Callable


T = TypeVar('T')


class Page(Generic[T]):
    """
    用于存储哔咔API分页返回的信息。

    Attributes:
        docs(list[T]): 本页内容，具体元素类型与调用方法有关。
        limit(int): 一页的最大可承载数量
        page(int): 页码
        pages(int): 全部页码
        total(int): 总内容量
    """

    def __init__(self, info: dict, constructor: Callable[[dict], T]):
        self.docs: list[T] = [constructor(i) for i in info['docs']]
        self.page: int = int(info['page']) # 有的返回会出现字符串
        self.pages: int = info['pages']
        self.total: int = info['total']
        self.limit: int = info['limit']


class Picture:
    """
    用于存储哔咔API返回的图片地址。

    Attributes:
        fileServer(str): 访问的文件服务器，为URL前缀，不以斜杠结尾，返回的仅供参考
        originalName(str): 源文件名称
        path(str): 路径，不以斜杠开头
    """
    
    def __init__(self, info: dict):
        self.fileServer: str = info['fileServer']
        self.originalName: str = info['originalName']
        self.path: str = info['path']
    
    def url(self, server: str = '') -> str:
        """
        生成指定图片服务器的URL。

        Args:
            server(str, optional): 指定的图片服务器，如果为空则为默认服务器

        Returns:
            str: 指定图片服务器的URL
        """

        if server == '': server = self.fileServer
        server = server.replace('https://', '').replace('http://', '') + '/static/' + self.path
        server = 'https://' + server.replace('//', '/')
        return server


class ComicPicture(Picture):
    """
    针对漫画页面的图片类。

    Attributes:
        id(str): 漫画图片ID
    """

    def __init__(self, info: dict):
        Picture.__init__(self, info['media'])
        self.id: str = info['_id']


class User:
    """
    用户信息。
    """

    def __init__(self, info: dict):
        # TODO: 这个不返回avatar的情况怎么办啊
        self.avatar: Picture | None = Picture(info['avatar']) if 'avatar' in info else None
        self.characters: list[str] = info['characters']
        self.exp: int = info['exp']
        self.gender: str = info['gender']
        self.level: int = info['level']
        self.name: str = info['name']
        self.role: str = info['role']
        self.slogan: str = info['slogan'] if 'slogan' in info else ''
        self.title: str = info['title']
        self.verified: bool = info['verified']
        self.id: str = info['_id']


class Profile(User):
    """
    当前登录账号的个人信息。
    """

    def __init__(self, info):
        User.__init__(self, info)
        self.isPunched: bool = info['isPunched']
        self.birthday: float = datetime.fromisoformat(info['birthday']).timestamp()
        self.created_at: float = datetime.fromisoformat(info['created_at']).timestamp()


class Comment:
    """
    单条评论。
    """

    def __init__(self, info: dict):
        """
        从API返回的JSON构造。

        Args:
            info: (dict[str, Any]): 单条comment的JSON字典
        """

        self.isTop: bool = info['isTop']
        self.hide: bool = info['hide']
        self.created_at: float = datetime.fromisoformat(info['created_at']).timestamp()
        self.id: str = info['id']
        self.isLiked: bool = info['isLiked']
        self.comic: str = info['_comic']
        self.likes: int = info['likesCount']
        self.comments: int = info.get('commentsCount', info['totalComments'])
        self.content: str = info['content']
        self.user: User = User(info['_user'])


class Comic:
    """
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
        pagesCount(int): 页数
        epsCount(int): 集数
        finished(bool): 完结情况
    """

    def __init__(self, info: dict):
        self.author: str = info['author']
        self.categories: list[str] = info['categories']
        self.finished: bool = info['finished']
        self.likes: int = info.get('likesCount', info.get('totalLikes', 0))
        self.tags: list[str] = info['tags']
        self.thumb: Picture = Picture(info['thumb'])
        self.title: str = info['title']
        self.views: int = info.get('totalViews', 0)
        self.pagesCount: int = info.get('pagesCount', 0)
        self.epsCount: int = info.get('epsCount', 0)
        self.id: str = info['_id']


class ComicDetailed(Comic):
    """
    存储漫画完整信息，用于漫画详情页。
    """

    def __init__(self, info: dict):
        Comic.__init__(self, info)
        self.description: str = info['description']
        self.creator: User = User(info['_creator'])
        self.chineseTeam: str = info['chineseTeam']
        self.updated_at: float = datetime.fromisoformat(info['updated_at']).timestamp()
        self.created_at: float = datetime.fromisoformat(info['created_at']).timestamp()
        self.isFavourite: bool = info['isFavourite']
        self.isLiked: bool = info['isLiked']


class Eps:
    """
    存储漫画单话信息。
    """

    def __init__(self, info: dict):
        self.id: str = info['_id']
        self.order: int = info['order']
        self.title: str = info['title']
        self.updated_at: float = datetime.fromisoformat(info['updated_at']).timestamp()


class Category:
    """
    存储分类信息。
    """

    def __init__(self, info: dict):
        self.active: bool = info['active']
        self.isWeb: bool = info['isWeb']
        self.link: str | None = info.get('link', None)
        self.thumb: Picture = Picture(info['thumb'])
        self.title: str = info['title']
