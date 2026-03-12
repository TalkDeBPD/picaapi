import aiofiles
import asyncio
from httpx import AsyncClient, HTTPError, Limits
from typing import Callable
from .objects import Picture
from .client import *


class Downloader:
    '''
    掌管图片下载类。允许使用多个服务器进行下载。
    '''

    DEFAULT_PICTURE_SERVER: list[str] = ['https://storage-b.go2778.com/static/', 'https://storage1.go2778.com/static/']
    DEFAULT_HEADERS: dict[str, str] = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0',
        'Accept': 'image/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN, zh; q=0.9, en; q=0.8',
        'Referer': 'https://manhuabika.com/',
    }

    def __init__(self, servers: list[str] = DEFAULT_PICTURE_SERVER, max_conn: int | None = None):
        '''
        Args:
            servers(list[str]): 服务器根
        '''
        limits = Limits(max_connections=max_conn)
        self.servers = servers
        self.clients = [AsyncClient(base_url=server, headers=Downloader.DEFAULT_HEADERS, limits=limits, follow_redirects=True) for server in self.servers]
        self.closed = False

    async def close(self) -> None:
        '''
        关闭我。请避免在关闭后再调用。
        '''
        if not self.closed:
            tasks = [client.aclose() for client in self.clients]
            await asyncio.gather(*tasks)
            self.closed = True

    async def __aenter__(self):
        return self
    
    async def __aexit__(self, *args):
        await self.close()

    async def downloadPicture(self, picture: Picture, ofilename: str | None = None) -> bool:
        '''
        下载单个图片。

        Args:
            picture(Picture): 哔咔API图片对象
            ofilename(str, optional): 保存文件路径，为空则按照picture的源名称保存

        Returns:
            bool: 是否成功，成功为True
        '''
        data = None
        for i, client in enumerate(self.clients):
            try:
                response = await client.get(picture.path)
                data = response.content
                break
            except HTTPError as e:
                if i + 1 == len(self.clients):
                    raise
        if data == None:
            return False
        async with aiofiles.open(picture.originalName if ofilename == None else ofilename, 'wb') as f:
            await f.write(data)
        return True

    async def downloadPictures(self, pictures:list[Picture], ofilename: Callable[[int, Picture], str|None]) -> list[bool | BaseException]:
        '''
        批量下载图片。

        Args:
            pictures(list[Picture]): 哔咔API图片列表
            ofilename(Callable[[int, Picture], str|None]): 保存文件路径构造器，传入图片的列表索引与其自身，返回路径
        
        Returns:
            list[bool | BaseException]: 对应于每张图片是否成功下载，会回复下载的错误消息
        '''
        tasks = [self.downloadPicture(pic, ofilename(i, pic)) for i, pic in enumerate(pictures)]
        return await asyncio.gather(*tasks, return_exceptions=True)

    async def downloadEps(self, client: Client, comic_id: str, ofilename: Callable[[int, Picture], str | None], order: int = 1) -> list[bool | BaseException]:
        '''
        下载单话漫画。

        Args:
            client(Client): 用于哔咔API请求的客户端实例
            comic_id(str): 漫画ID
            ofilename(Callable[[int, Picture], str|None]): 保存文件路径构造器，传入图片的列表索引与其自身，返回路径
            order(int, optional): 代表具体的单话编号，默认为1
        
        Returns:
            list[bool | BaseException]: 对应于每张图片是否成功下载，会回复下载的错误消息
        '''
        
        p1 = await client.pages(comic_id, order)
        picture_list = p1.docs
        tasks = [client.pages(comic_id, order, i) for i in range(2, p1.pages + 1)]
        pages = await asyncio.gather(*tasks)
        for page in pages:
            picture_list += page.docs
        return await self.downloadPictures(picture_list, ofilename)
