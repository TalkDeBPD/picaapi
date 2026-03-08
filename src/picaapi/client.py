from .base import *
from .objects import *


class Client:
    '''
    用于执行各项逻辑的PicaAPI客户端，代表一个登录用户。

    Attributes:
        domain(str): 哔咔API的域名
        token(str): 哔咔用户令牌
        quality(str): 图像品质，可选项：low, medium, high, original
        DEFAULT_DOMAIN(str, static): 默认哔咔API域名
        COMMENTS_BOARD(str, static): 哔咔留言板漫画ID
    '''

    DEFAULT_DOMAIN = 'go2778.com'
    COMMENTS_BOARD = '5822a6e3ad7ede654696e482'

    def __init__(self, domain: str = DEFAULT_DOMAIN, token: str | None = None, quality: str = 'medium'):
        '''
        Args:
            domain(str, optional): 哔咔API域名，默认为DEFAULT_DOMAIN
            token(str, optional): 用户令牌，默认为None（未登录）
            quality(str, optional): 图像品质，默认为medium（中等）
        '''
        self.domain = domain
        self.token = token
        self.quality = quality

    def login(self, email: str, password: str) -> None:
        '''
        登录哔咔。

        Args:
            email(str): 邮箱或用户名
            password(str): 密码
        '''
        response = makeAPIRequest(self.domain, 'auth/sign-in', 'POST', { 'email': email, 'password': password })
        self.token = response['token'];

    def profile(self) -> User:
        '''
        获取登录用户信息。

        Returns:
            User: 登录用户信息
        '''
        response = makeAPIRequest(self.domain, 'users/profile', token=self.token)
        return Profile(response)

    def punchin(self) -> None:
        '''
        每日签到（打哔卡）。
        '''
        makeAPIRequest(self.domain, 'users/punch-in', 'POST', token=self.token)
    
    def comic(self, id: str) -> ComicDetailed:
        '''
        获取漫画详细信息。

        Args:
            id(str): 漫画ID
        
        Returns:
            ComicDetailed: 漫画详细信息
        '''
        response = makeAPIRequest(self.domain, f'comics/{id}', token=self.token)
        return ComicDetailed(response['comic'])
    
    def advancedSearch(self, keyword: str, categories: list[str] = [], sort: str = 'dd', page: int = 1) -> Page:
        '''
        哔咔高级搜索。

        Args:
            keyword(str): 搜索关键字
            categories(list[str], optional): 分类
            sort(str, optional): 排序方式，默认为dd（新到旧）
            page(int, optional): 分页页码，默认为1
        
        Returns:
            Page: 返回结果页，数据类型为Comic
        '''
        json_map:dict[str, str|list[str]] = { 'keyword': keyword, 'sort': sort }
        if categories != []: json_map['categories'] = categories
        response = makeAPIRequest(self.domain, f'comics/advanced-search?page={page}&s={sort}', 'POST', json_map, self.token)
        return Page(response['comics'], Comic)
    
    def comments(self, comic_id: str, page: int = 1) -> Page:
        '''
        查看某漫画的评论。

        Args:
            comic_id(str): 漫画ID
            page(int, optional): 分页页码，默认为1
        
        Returns:
            Page: 返回结果页，数据类型为Comment
        '''
        response = makeAPIRequest(self.domain, f"comics/{comic_id}/comments?page={page}", token=self.token)
        return Page(response['comments'], Comment)
    
    def childrens(self, comment_id: str, page: int = 1) -> Page:
        '''
        查看某评论的评论。

        Args:
            comment_id(str): 评论ID
            page(int, optional): 分页页码，默认为1
        
        Returns:
            Page: 返回结果页，数据类型为Comment
        '''
        response = makeAPIRequest(self.domain, f"comments/{comment_id}/childrens?page={page}", token=self.token)
        return Page(response['comments'], Comment)
    
    def favourite(self, sort: str = 'dd', page: int = 1, limit: int = 20) -> Page:
        '''
        查看收藏夹。

        Args:
            sort(str, optional): 排序方式，默认为dd（新到旧）
            page(int, optional): 分页页码，默认为1
            limit(int, optional): 单页最大值，默认为20
        
        Returns:
            Page: 返回结果页，数据类型为Comic
        '''
        response = makeAPIRequest(self.domain, f'users/favourite?page={page}&s={sort}&limit={limit}', token=self.token)
        return Page(response['comics'], Comic)

    def eps(self, comic_id: str, page: int = 1) -> Page:
        '''
        查看某漫画的各话信息。

        Args:
            comic_id(str): 漫画ID
            page(int, optional): 分页页码，默认为1
        
        Returns:
            Page: 返回结果页，数据类型为Eps
        '''
        response = makeAPIRequest(self.domain, f'comics/{comic_id}/rps?page={page}', token=self.token)
        return Page(response['eps'], Eps)
    
    def pages(self, comic_id: str, order: int = 1, page: int = 1) -> Page:
        '''
        获取漫画内容的图片路径。

        Args:
            comic_id(str): 漫画ID
            order(int, optional): 单话序号，默认为1
            page(int, optional): 分页页码，默认为1
        
        Returns:
            Page: 返回结果页，数据类型为ComicPicture
        '''
        response = makeAPIRequest(self.domain, f'comics/{comic_id}/order/{order}/pages?page={page}', token=self.token, quality=self.quality)
        return Page(response['pages'], ComicPicture)

    def leaderboard(self, tt: str='H24') -> list[Comic]:
        '''
        获取哔咔排行榜。

        Args:
            tt(str, optional): 时间，默认为H24（近24小时）
        
        Returns:
            list[Comic]: 排行榜
        '''
        response = makeAPIRequest(self.domain, f'comics/leaderboard?tt={tt}&ct=VC', token=self.token)
        return [Comic(comic) for comic in response['comics']]

    def likeComic(self, comic_id: str) -> None:
        '''
        点赞漫画。

        Args:
            comic_id(str): 漫画ID
        '''
        makeAPIRequest(self.domain, f'comics/{comic_id}/like', method='POST', token=self.token)
    
    def favouriteComic(self, comic_id: str) -> None:
        '''
        收藏漫画。

        Args:
            comic_id(str): 漫画ID
        '''
        makeAPIRequest(self.domain, f'comics/{comic_id}/favourite', method='POST', token=self.token)

    def likeComment(self, comment_id: str) -> None:
        '''
        点赞评论。
        
        Args:
            comment_id(str): 评论ID
        '''
        makeAPIRequest(self.domain, f'comments/{comment_id}/like', method='POST', token=self.token)

    def commentComic(self, comic_id: str, content: str) -> None:
        '''
        评论漫画。

        Args:
            comic_id(str): 漫画ID
            content(str): 评论内容
        '''
        makeAPIRequest(self.domain, f'comics/{comic_id}/comments', json={'content': content},  method='POST', token=self.token)
    
    def commentComment(self, comment_id: str, content: str) -> None:
        '''
        评论评论。

        Args:
            comment_id(str): 评论ID
            content(str): 评论内容
        '''
        makeAPIRequest(self.domain, f'comments/{comment_id}', json={'content': content}, method='POST', token=self.token)
