import time
import random
import hashlib
from .error import *


def randomStr(length = 32) -> str:
    '''
    生成随机的Nonce字串。

    Args:
        length(str, optional): 字串长度，默认32

    Returns:
        str: Nonce字串
    '''
    lib = 'ABCDEFGHJKMNPQRSTWXYZabcdefhijkmnprstwxyz2345678'
    result = ''
    for _ in range(0, length):
        result += lib[int(random.random() * 48)]
    return result


def makeSignature(dir: str, time: str, method: str, nonce: str) -> str:
    '''
    生成哔咔API签名。

    Args:
        dir(str): 请求路径（包含URL参数，没有前导斜杠）
        time(str): 以秒计的时间戳
        method(str): 请求方法
        nonce(str): 随机密钥
    
    Returns:
        str: Signature签名
    '''
    ready = dir + time + nonce + method + 'C69BAF41DA5ABD1FFEDC6D2FEA56B'
    rb = ready.lower().encode()
    key = b'~d}$Q7$eIni=V)9\\RK/P.RM4;9[7|@/CA}b~OW!3?EV`:<>M7pddUBL5n|0/*Cn\0'
    a = bytes(92 ^ b for b in key)
    b = bytes(54 ^ b for b in key)
    c = hashlib.sha256(b + rb).digest()
    m = hashlib.sha256(a + c)
    return m.hexdigest()


def makeHeaders(dir: str, method: str, authorization: str | None = None, quality: str = 'medium') -> dict:
    '''
    生成哔咔API请求头。

    Args:
        dir(str): 请求路径（包含URL参数，没有前导斜杠）
        method(str): 请求方法
        authorization(str, optional): 登录用户token，默认为None，注意除注册登录外不可为None
        quality(str, optional): 图像品质，可选项：low, medium, high, original，默认为medium

    Returns:
        dict: 构造的headers
    '''
    sTime = str(int(time.time()))
    nonce = randomStr()
    signature = makeSignature(dir, sTime, method, nonce)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0',
        'Accept': 'application/vnd.picacomic.com.v1+json',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN, zh; q=0.9, en; q=0.8',
        'App-Channel': '1',
        'App-Platform': 'android',
        'App-Uuid': 'webUUIDv2',
        'App-Version': '20251017',
        'Time': sTime,
        'Image-Quality': quality,
        'Content-Type': 'application/json; charset=UTF-8',
        'Nonce': nonce,
        'Signature': signature,
        'Origin': 'https://manhuabika.com',
        'Referer': 'https://manhuabika.com/',
    }
    if authorization != None:
        headers['Authorization'] = authorization
    return headers
