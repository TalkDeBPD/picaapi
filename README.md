# picaapi

![GitHub License](https://img.shields.io/github/license/TalkDeBPD/picaapi)

## 简介

基于niquests的便捷的哔咔漫画API的Python调用库，允许下载图片，并允许手动设置API服务器和图片服务器。

## 开发进度

> 这个还没有开发完呢！

- [x] API调用签名验证
- [x] 登录和打哔卡
- [x] 搜索漫画、查看分类、查看收藏
- [x] 查看漫画、下载漫画
- [x] 点赞、收藏、评论
- [ ] 骑士榜
- [ ] 游戏区
- [ ] 举报违规评论

## 示例

``` Python
# 打哔卡
from picaapi.client import Client
from picaapi.err import PicaAPIError
try:
    client = Client()
    client.login(input('用户名：'), input('密码：'))
    client.punchin()
except PicaAPIError as e:
    print(str(e))
```

## 注意事项

爱护哔咔服务器，严禁滥用，禁止将该项目用于商用。
