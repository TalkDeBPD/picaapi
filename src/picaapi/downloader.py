import asyncio
import aiofiles
from httpx import HTTPError
from abc import abstractmethod, ABC
from typing import AsyncIterator, Any
from typing_extensions import override

from .client import *
from .objects import Picture


DEFAULT_HEADERS: dict[str, str] = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0',
    'Accept': 'image/*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN, zh; q=0.9, en; q=0.8',
    'Referer': 'https://manhuabika.com/',
}
DEFAULT_PICTURE_SERVER: list[str] = ['https://storage-b.go2778.com/static/', 'https://storage1.go2778.com/static/']


class BasePictureClient(ABC):
    @abstractmethod
    async def fetch(self, path: str) -> bytes:
        pass

    @abstractmethod
    async def aclose(self):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.aclose()


class PictureClient(BasePictureClient):
    """
    图片服务器客户端类。仅可进行简单的图片下载。
    """
    def __init__(self, base_url: str, headers: dict[str, str] | None = None, max_conn: int | None = None):
        """
        Args:
            base_url(str): 根目录，注意是否有/static/
            headers(dict[str, str], optional): 请求头，默认为DEFAULT_HEADERS
            max_conn(int, optional): 最大连接数，建议10，默认遵循httpx
        """
        if headers is None:
            headers = DEFAULT_HEADERS
        self.client = AsyncClient(base_url=base_url, headers=headers, limits=Limits(max_connections=max_conn), follow_redirects=True, timeout=(5.0, 30.0, 5.0, 5.0))
        self.closed = False

    @override
    async def aclose(self) -> None:
        if not self.closed:
            await self.client.aclose()
            self.closed = True

    @override
    async def fetch(self, path: str) -> bytes:
        """
        请求图片。一次性返回bytes。

        Args:
            path(str): 图片路径

        Returns:
            bytes: 图片数据
        """
        response = await self.client.get(path)
        response.raise_for_status()
        return response.content

    async def fetch_stream(self, path: str, chunk_size: int | None = None) -> AsyncIterator[bytes]:
        """
        请求图片。流式返回生成器。

        Args:
            path(str): 图片路径
            chunk_size(int, optional): 每块大小

        Returns:
            AsyncIterator[bytes]: 生成器
        """
        async with self.client.stream('GET', path) as stream:
            stream.raise_for_status()
            async for chunk in stream.aiter_bytes(chunk_size=chunk_size):
                yield chunk


class MultiHostPictureClient(BasePictureClient):
    """
    图片服务器客户端类。用于从多个源尝试下载图片。
    """
    def __init__(self, base_urls: list[str] | None = None, headers: dict[str, str] | None = None, max_conn: int | None = None):
        """
        Args:
            base_urls(list[str]): 根目录，注意是否有/static/
            headers(dict[str, str], optional): 请求头，默认为DEFAULT_HEADERS
            max_conn(int, optional): 最大连接数，建议10，默认遵循httpx
        """
        self.base_urls = base_urls if base_urls else DEFAULT_PICTURE_SERVER
        if headers is None:
            headers = DEFAULT_HEADERS
        self.client = AsyncClient(headers=headers, limits=Limits(max_connections=max_conn), follow_redirects=True, timeout=(5.0, 30.0, 5.0, 5.0))
        self.closed = False

    @override
    async def aclose(self) -> None:
        if not self.closed:
            await self.client.aclose()
            self.closed = True

    @override
    async def fetch(self, path: str) -> bytes:
        """
        请求图片。一次性返回bytes。

        Args:
            path(str): 图片路径

        Returns:
            bytes: 图片数据
        """
        tasks = [asyncio.create_task(self.client.get(parse.urljoin(base_url, path))) for base_url in self.base_urls]
        last_e = None
        try:
            for task in asyncio.as_completed(tasks):
                try:
                    response = await task
                    response.raise_for_status()
                    return response.content
                except HTTPError as e:
                    last_e = e
        finally:
            for task in tasks:
                task.cancel()
        if last_e: raise last_e
        return b''


class Downloader:
    """
    掌管图片下载类。
    """

    def __init__(self, client: BasePictureClient):
        """
        Args:
            client(BasePictureClient): 用于执行请求的下载客户端
        """
        self.client = client

    async def download_picture(self, picture: Picture, filename: str | None = None) -> bool:
        """
        下载单个图片。

        Args:
            picture(Picture): 哔咔API图片对象
            filename(str, optional): 保存文件路径，为空则按照picture的源名称保存

        Returns:
            bool: 是否成功，成功为True
        """
        data = await self.client.fetch(picture.path)
        async with aiofiles.open(picture.originalName if filename is None else filename, 'wb') as f:
            await f.write(data)
        return True

    async def download_pictures(self, pictures:list[Picture], filename: Callable[[int, Picture], str | None]) -> tuple[BaseException | Any]:
        """
        批量下载图片。

        Args:
            pictures(list[Picture]): 哔咔API图片列表
            filename(Callable[[int, Picture], str|None]): 保存文件路径构造器，传入图片的列表索引与其自身，返回路径

        Returns:
            tuple[BaseException | Any]: 对应于每张图片是否成功下载，会回复下载的错误消息
        """
        tasks = [self.download_picture(pic, filename(i, pic)) for i, pic in enumerate(pictures)]
        return await asyncio.gather(*tasks, return_exceptions=True)

    async def download_eps(self, client: Client, comic_id: str, filename: Callable[[int, Picture], str | None], order: int = 1) -> tuple[BaseException | Any]:
        """
        下载单话漫画。

        Args:
            client(Client): 用于哔咔API请求的客户端实例
            comic_id(str): 漫画ID
            filename(Callable[[int, Picture], str|None]): 保存文件路径构造器，传入图片的列表索引与其自身，返回路径
            order(int, optional): 代表具体的单话编号，默认为1
        
        Returns:
            list[bool | BaseException]: 对应于每张图片是否成功下载，会回复下载的错误消息
        """
        p1, title = await client.pages(comic_id, order)
        picture_list = p1.docs
        tasks = [client.pages(comic_id, order, i) for i in range(2, p1.pages + 1)]
        pages = await asyncio.gather(*tasks)
        for page in pages:
            picture_list += page.docs
        return await self.download_pictures(picture_list, filename)
