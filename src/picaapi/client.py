from .base import *
from .user import *
from .comic import *


class Client:
    '''
    用于执行各项逻辑的PicaAPI客户端。
    '''
    def __init__(self, domain: str, token: str | None= None):
        self.domain = domain
        self.token = token

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
    
    def advancedSearch(self, keyword:str, sort:str, page:int = 1, categories:list[str] = []) -> ComicListPage:
        json_map:dict[str, str|list[str]] = { 'keyword': keyword, 'sort': sort }
        if categories != []: json_map['categories'] = categories
        request = makeAPIRequest(self.domain, f'comics/advanced-search?page={page}&s={sort}', 'POST', json_map, self.token)
        return ComicListPage(request['comics'])
