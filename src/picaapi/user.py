from datetime import datetime
from .picture import *


class User:
    '''
    用户信息。
    '''
    def __init__(self, info):
        self.avatar = Picture(info['avatar'])
        self.characters = info['characters']
        self.exp = info['exp']
        self.gender = info['gender']
        self.level = info['level']
        self.name = info['name']
        self.role = info['role']
        self.slogan = info['slogan']
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
