from httpx import AsyncClient, Limits
from urllib import parse
from .base import *
from .error import PicaAPIError
from .objects import *


class Client:
    """
    用于执行各项逻辑的PicaAPI客户端，代表一个登录用户。

    Attributes:
        client(AsyncClient): 异步连接池
        token(str): 哔咔用户令牌
        quality(str): 图像品质，可选项：low, medium, high, original
        DEFAULT_DOMAIN(str, static): 默认哔咔API域名
        COMMENTS_BOARD(str, static): 哔咔留言板漫画ID
    """

    DEFAULT_DOMAIN = 'go2778.com'
    COMMENTS_BOARD = '5822a6e3ad7ede654696e482'

    def __init__(self, domain: str = DEFAULT_DOMAIN, token: str | None = None, quality: str = 'medium', max_conn: int | None = None):
        """
        Args:
            domain(str, optional): 哔咔API域名，默认为DEFAULT_DOMAIN
            token(str, optional): 用户令牌，默认为None（未登录）
            quality(str, optional): 图像品质，默认为medium（中等）
        """
        self.token = token
        self.quality = quality
        self.client: AsyncClient = AsyncClient(base_url='https://picaapi.' + domain + '/', limits=Limits(max_connections=max_conn))
        self.closed = False

    async def __aenter__(self):
        return self
    
    async def __aexit__(self, *args):
        await self.close()
    
    async def close(self) -> None:
        """
        关闭我。请避免在关闭后再调用。
        """
        if not self.closed:
            await self.client.aclose()
            self.closed = True

    async def request(self, method: str, url: str, json = None):
        """
        发送一般哔咔API请求。

        Args:
            method(str): 请求方法
            url(str): 请求路径（包含URL参数，没有前导斜杠）
            json(dict, optional): 请求负载，默认为None

        Returns:
            dict: 返回数据data

        Raises:
            PicaAPIError: 请求失败
        """
        response = await self.client.request(method=method, url=url, json=json, headers=make_headers(url, method, self.token, self.quality))
        json = response.json()
        if json['code'] != 200:
            raise PicaAPIError(response.json()['error'], response.json()['message'])
        return json.get('data', {})

    async def login(self, email: str, password: str) -> None:
        """
        登录哔咔并自动保存token。

        Args:
            email(str): 邮箱或用户名
            password(str): 密码
        """
        response = await self.request('POST', 'auth/sign-in', { 'email': email, 'password': password })
        self.token = response['token']

    async def profile(self) -> User:
        """
        获取登录用户信息。

        Returns:
            User: 登录用户信息
        """
        response = await self.request('GET', 'users/profile')
        return Profile(response)

    async def punch_in(self) -> None:
        """
        每日签到（打哔卡）。
        """
        await self.request('POST', 'users/punch-in')
    
    async def comic(self, comic_id: str) -> ComicDetailed:
        """
        获取漫画详细信息。

        Args:
            comic_id(str): 漫画ID

        Returns:
            ComicDetailed: 漫画详细信息
        """
        response = await self.request('GET', f'comics/{comic_id}')
        return ComicDetailed(response['comic'])
    
    async def advanced_search(self, keyword: str, categories: list[str] | None = None, sort: str = 'dd', page: int = 1) -> Page:
        """
        哔咔高级搜索。

        Args:
            keyword(str): 搜索关键字
            categories(list[str], optional): 分类
            sort(str, optional): 排序方式，默认为dd（新到旧）
            page(int, optional): 分页页码，默认为1

        Returns:
            Page: 返回结果页，数据类型为Comic
        """
        if categories is None:
            categories = []
        json_map:dict[str, str|list[str]] = { 'keyword': keyword, 'sort': sort }
        if categories != []: json_map['categories'] = categories
        response = await self.request('POST', f'comics/advanced-search?page={page}&s={sort}', json_map)
        return Page(response['comics'], Comic)
    
    async def comments(self, comic_id: str, page: int = 1) -> tuple[Page, list[Comment]]:
        """
        查看某漫画的评论。

        Args:
            comic_id(str): 漫画ID
            page(int, optional): 分页页码，默认为1

        Returns:
            Page: 返回结果页，数据类型为Comment
            list[Comment]: 置顶评论
        """
        response = await self.request('GET', f'comics/{comic_id}/comments?page={page}')
        return Page(response['comments'], Comment), [Comment(com) for com in response['topComments']]
    
    async def children(self, comment_id: str, page: int = 1) -> Page:
        """
        查看某评论的评论。

        Args:
            comment_id(str): 评论ID
            page(int, optional): 分页页码，默认为1

        Returns:
            Page: 返回结果页，数据类型为Comment
        """
        response = await self.request('GET', f'comments/{comment_id}/children?page={page}')
        return Page(response['comments'], Comment)
    
    async def favourite(self, sort: str = 'dd', page: int = 1, limit: int = 20) -> Page:
        """
        查看收藏夹。

        Args:
            sort(str, optional): 排序方式，默认为dd（新到旧）
            page(int, optional): 分页页码，默认为1
            limit(int, optional): 单页最大值，默认为20

        Returns:
            Page: 返回结果页，数据类型为Comic
        """
        response = await self.request('GET', f'users/favourite?page={page}&s={sort}&limit={limit}')
        return Page(response['comics'], Comic)

    async def eps(self, comic_id: str, page: int = 1) -> Page:
        """
        查看某漫画的各话信息。

        Args:
            comic_id(str): 漫画ID
            page(int, optional): 分页页码，默认为1

        Returns:
            Page: 返回结果页，数据类型为Eps
        """
        response = await self.request('GET', f'comics/{comic_id}/eps?page={page}')
        return Page(response['eps'], Eps)
    
    async def pages(self, comic_id: str, order: int = 1, page: int = 1) -> Page:
        """
        获取漫画内容的图片路径。

        Args:
            comic_id(str): 漫画ID
            order(int, optional): 单话序号，默认为1
            page(int, optional): 分页页码，默认为1

        Returns:
            Page: 返回结果页，数据类型为ComicPicture
        """
        response = await self.request('GET', f'comics/{comic_id}/order/{order}/pages?page={page}')
        return Page(response['pages'], ComicPicture)

    async def leaderboard(self, tt: str='H24') -> list[Comic]:
        """
        获取哔咔排行榜。

        Args:
            tt(str, optional): 时间，默认为H24（近24小时）

        Returns:
            list[Comic]: 排行榜
        """
        response = await self.request('GET', f'comics/leaderboard?tt={tt}&ct=VC')
        return [Comic(comic) for comic in response['comics']]

    async def categories(self) -> list[Category]:
        """
        获取哔咔分类。

        Returns:
            list[Category]: 分类列表
        """
        response = await self.request('GET', 'categories')
        return [Category(cate) for cate in response['categories']]

    async def comics(self, key: str, value: str, sort: str = 'dd', page: int = 1) -> Page[Comic]:
        """
        通过分类/标签/作者/汉化/骑士查询漫画

        Args:
            key(str): 键
            value(str): 查询值
            sort(str, optional): 排序方式，默认为dd（旧到新）
            page(int, optional): 分页页码

        Returns:
            Page[Comic]: 查询结果
        """
        response = await self.request('GET', f'comics?page={page}&s={sort}&{key}={parse.quote(value)}')
        return Page(response['comics'], Comic)

    async def like_comic(self, comic_id: str) -> None:
        """
        点赞漫画。

        Args:
            comic_id(str): 漫画ID
        """
        await self.request('POST', f'comics/{comic_id}/like')
    
    async def favourite_comic(self, comic_id: str) -> None:
        """
        收藏漫画。

        Args:
            comic_id(str): 漫画ID
        """
        await self.request('POST', f'comics/{comic_id}/favourite')

    async def like_comment(self, comment_id: str) -> None:
        """
        点赞评论。

        Args:
            comment_id(str): 评论ID
        """
        await self.request('POST', f'comments/{comment_id}/like')

    async def comment_comic(self, comic_id: str, content: str) -> None:
        """
        评论漫画。

        Args:
            comic_id(str): 漫画ID
            content(str): 评论内容
        """
        await self.request('POST', f'comics/{comic_id}/comments', {'content': content})
    
    async def comment_comment(self, comment_id: str, content: str) -> None:
        """
        评论评论。

        Args:
            comment_id(str): 评论ID
            content(str): 评论内容
        """
        await self.request('POST', f'comments/{comment_id}', {'content': content})

    async def status(self) -> None:
        """
        检查状态。
        """
        await self.request('GET', 'status.json')
