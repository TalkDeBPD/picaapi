# picaapi

![GitHub License](https://img.shields.io/github/license/TalkDeBPD/picaapi)

## 简介

基于httpx的便捷的哔咔漫画API的Python调用库，允许手动设置API服务器和图片服务器。支持异步调用，支持并发下载图片。

## 开发进度

> 这个还没有开发完呢！
> 下载漫画的异常处理方面尚有缺陷！

- [x] API调用签名验证
- [x] 登录和打哔卡
- [x] 搜索漫画、查看分类、查看收藏
- [x] 查看漫画、下载漫画
- [x] 点赞、收藏、评论
- [ ] 骑士榜
- [ ] 游戏区
- [ ] 举报违规评论

## 示例

打哔卡
``` Python
import asyncio
from picaapi.client import Client
async def main():
    async with Client() as client:
        await client.login(input('用户名：'), input('密码：'))
        await client.punchin()
asyncio.run(main())
```

## 注意事项

爱护哔咔服务器，严禁滥用，禁止将该项目用于商用。
