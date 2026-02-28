from .base import *
from .user import *
from .comic import *


class Client:
    def __init__(self, domain: str, token: str | None= None):
        self.__domain = domain
        self.__token = token

    @property
    def token(self) -> str | None:
        return self.__token

    def login(self, email: str, password: str) -> None:
        response = makeAPIRequest(self.__domain, 'auth/sign-in', 'POST', { 'email': email, 'password': password })
        self.__token = response['token'];

    def profile(self) -> User:
        response = makeAPIRequest(self.__domain, 'users/profile', token=self.__token)
        return Profile(response)

    def punchin(self) -> None:
        makeAPIRequest(self.__domain, 'users/punch-in', 'POST', token=self.__token)
    
    def comic(self, id: str) -> ComicDetailed:
        return ComicDetailed(makeAPIRequest(self.__domain, f'comics/{id}', token=self.token)['comic'])
    