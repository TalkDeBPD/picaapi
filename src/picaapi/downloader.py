import niquests
import io
from concurrent.futures import ThreadPoolExecutor, Future
from typing import Callable
from .objects import Picture
from .client import *


class Downloader:
    '''
    掌管图片下载类。
    '''

    DEFAULT_PICTURE_SERVER: list[str] = ['storage-b.go2778.com', 'storage1.go2778.com']
    DEFAULT_HEADERS: dict[str, str] = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0',
        'Accept': 'image/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN, zh; q=0.9, en; q=0.8',
        'Referer': 'https://manhuabika.com/',
    }

    def __init__(self, servers: list[str] = DEFAULT_PICTURE_SERVER):
        self.servers = servers

    def downloadPicture(self, picture:Picture, ofilename: str | None = None) -> bool:
        '''
        下载单个图片。

        Args:
            picture(Picture): 哔咔API图片对象
            ofilename(str, optional): 保存文件路径，为空则按照picture的源名称保存

        Returns:
            bool: 是否成功，成功为True
        '''

        data = None
        for server in self.servers:
            try:
                response = niquests.get(picture.url(server), headers=Downloader.DEFAULT_HEADERS)
                data = response.content
                break
            except (ConnectionError, TimeoutError):
                pass
        if data is None:
            return False
        with io.open(picture.originalName if ofilename is None else ofilename, 'wb') as f:
            f.write(data)
        return True

    def downloadPictures(self, pictures:list[Picture], ofilename: Callable[[int, Picture], str|None], max_workers: int | None = None) -> list[bool]:
        '''
        批量下载图片。

        Args:
            pictures(list[Picture]): 哔咔API图片列表
            ofilename(Callable[[int, Picture], str|None]): 保存文件路径构造器，传入图片的列表索引与其自身，返回路径
            max_workers(int, optional): 多线程下载线程池的最大并发数
        
        Returns:
            list[bool]: 对应于每张图片是否成功下载
        '''

        results:list[bool] = []
        with ThreadPoolExecutor(max_workers=max_workers) as tp:
            futures:list[Future] = []
            for i, picture in enumerate(pictures):
                futures.append(tp.submit(self.downloadPicture, picture, ofilename(i, picture)))
            for i in range(0, len(pictures)):
                results.append(futures[i].result())
        return results

    def downloadEps(self, client: Client, comic_id: str, ofilename: Callable[[int, Picture], str | None], order: int = 1, max_workers: int | None = None) -> list[bool]:
        '''
        下载单话漫画。

        Args:
            client(Client): 用于哔咔API请求的客户端实例
            comic_id(str): 漫画ID
            ofilename(Callable[[int, Picture], str|None]): 保存文件路径构造器，传入图片的列表索引与其自身，返回路径
            order(int, optional): 代表具体的单话编号，默认为1
            max_workers(int, optional): 多线程下载线程池的最大并发数
        
        Returns:
            list[bool]: 对应于每张图片是否成功下载
        '''
        
        p1 = client.pages(comic_id, order)
        picture_list = p1.docs
        for i in range(2, p1.pages + 1):
            p = client.pages(comic_id, order, i)
            picture_list += p.docs
        return self.downloadPictures(picture_list, ofilename, max_workers)
