import time
import random
import hashlib
import niquests
from .error import *


def randomStr(length=32) -> str:
    lib = 'ABCDEFGHJKMNPQRSTWXYZabcdefhijkmnprstwxyz2345678'
    result = ''
    for i in range(0, length):
        result += lib[int(random.random() * 48)]
    return result


def makeSignature(dir: str, time: str, method: str, nonce: str) -> str:
    ready = dir + time + nonce + method + 'C69BAF41DA5ABD1FFEDC6D2FEA56B'
    rb = ready.lower().encode()
    key = b'~d}$Q7$eIni=V)9\\RK/P.RM4;9[7|@/CA}b~OW!3?EV`:<>M7pddUBL5n|0/*Cn\0'
    a = bytes(92 ^ b for b in key)
    b = bytes(54 ^ b for b in key)
    c = hashlib.sha256(b + rb).digest()
    m = hashlib.sha256(a + c)
    return m.hexdigest()


def makeHeaders(dir: str, method: str, authorization: str | None = None) -> dict:
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
        'Image-Quality': 'medium',
        'Content-Type': 'application/json; charset=UTF-8',
        'Nonce': nonce,
        'Signature': signature,
        'Origin': 'https://manhuabika.com',
        'sec-ch-ua': '"Not:A-Brand";v="99", "Microsoft Edge";v="145", "Chromium";v="145"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'Referer': 'https://manhuabika.com/',
        'Authorization': authorization
    }
    return headers


def makeAPIRequest(domain: str, dir: str, method: str='GET', json = None, token: str | None = None):
    '''
    通用哔咔API请求函数
    '''
    response = niquests.request(method, 'https://picaapi.' + domain + '/' + dir, json=json, headers=makeHeaders(dir, method, token))
    if response.json()['code'] != 200:
        raise PicaAPIError(response.json()['error'], response.json()['message'])
    return response.json()['data']

