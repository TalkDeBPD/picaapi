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
        self.domain = domain
        self.token = token
        self.quality = quality

    def login(self, email: str, password: str) -> None:
        response = makeAPIRequest(self.domain, 'auth/sign-in', 'POST', { 'email': email, 'password': password })
        self.token = response['token'];

    def profile(self) -> User:
        response = makeAPIRequest(self.domain, 'users/profile', token=self.token)
        return Profile(response)

    def punchin(self) -> None:
        makeAPIRequest(self.domain, 'users/punch-in', 'POST', token=self.token)
    
    def comic(self, id: str) -> ComicDetailed:
        return ComicDetailed(makeAPIRequest(self.domain, f'comics/{id}', token=self.token)['comic'])
    
    def advancedSearch(self, keyword: str, categories: list[str] = [], sort: str = 'dd', page: int = 1) -> Page:
        json_map:dict[str, str|list[str]] = { 'keyword': keyword, 'sort': sort }
        if categories != []: json_map['categories'] = categories
        response = makeAPIRequest(self.domain, f'comics/advanced-search?page={page}&s={sort}', 'POST', json_map, self.token)
        return Page(response['comics'], Comic)
    
    def comments(self, comic_id: str, page: int = 1) -> Page:
        response = makeAPIRequest(self.domain, f"comics/{comic_id}/comments?page={page}", token=self.token)
        return Page(response['comments'], Comment)
    
    def childrens(self, comment_id: str, page: int = 1) -> Page:
        response = makeAPIRequest(self.domain, f"comments/{comment_id}/childrens?page={page}", token=self.token)
        return Page(response['comments'], Comment)
    
    def favourite(self, sort: str = 'dd', page: int = 1, limit: int = 20) -> Page:
        response = makeAPIRequest(self.domain, f'users/favourite?page={page}&s={sort}&limit={limit}', token=self.token)
        return Page(response['comics'], Comic)

    def eps(self, comic_id: str, page: int = 1) -> Page:
        response = makeAPIRequest(self.domain, f'comics/{comic_id}/rps?page={page}', token=self.token)
        return Page(response['eps'], Eps)
    
    def pages(self, comic_id: str, order: int = 1, page: int = 1) -> Page:
        response = makeAPIRequest(self.domain, f'comics/{comic_id}/order/{order}/pages?page={page}', token=self.token, quality=self.quality)
        return Page(response['pages'], ComicPicture)

    def leaderboard(self, tt: str='H24') -> list[Comic]:
        response = makeAPIRequest(self.domain, f'comics/leaderboard?tt={tt}&ct=VC', token=self.token)
        return [Comic(comic) for comic in response['comics']]

    def likeComic(self, comic_id: str) -> None:
        makeAPIRequest(self.domain, f'comics/{comic_id}/like', method='POST', token=self.token)
    
    def favouriteComic(self, comic_id: str) -> None:
        makeAPIRequest(self.domain, f'comics/{comic_id}/favourite', method='POST', token=self.token)

    def likeComment(self, comment_id: str) -> None:
        makeAPIRequest(self.domain, f'comments/{comment_id}/like', method='POST', token=self.token)

    def commentComic(self, comic_id: str, content: str) -> None:
        makeAPIRequest(self.domain, f'comics/{comic_id}/comments', json={'content': content},  method='POST', token=self.token)
    
    def commentComment(self, comment_id: str, content: str) -> None:
        makeAPIRequest(self.domain, f'comments/{comment_id}', json={'content': content}, method='POST', token=self.token)
