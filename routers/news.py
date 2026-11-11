# 新闻模块的所有路由
# APIRouter 用于把一组相关的接口拆到单独文件里，最后在 main.py 中统一注册
from fastapi import APIRouter, Depends, HTTPException, Query
from crud import news
from config.db_config import get_db
from sqlalchemy.ext.asyncio import AsyncSession 
# 创建 APIRouter 实例
# prefix：该模块下所有接口的统一路径前缀，最终路径为 /api/news/xxx
# tags：OpenAPI 文档（/docs）中的分组名称
router = APIRouter(prefix="/api/news", tags=["news"])


# GET /api/news/categories：获取新闻分类列表
# @router.get("/categories") 会把函数注册为 GET 请求处理器
# async def 表示异步处理函数，适合包含 IO 操作（数据库、网络）的场景
@router.get("/categories")
async def get_categories(skip:int=0,limit:int=100,db:AsyncSession=Depends(get_db)):
    #获取数据库里面的新闻分类
    # 返回内容会被 FastAPI 自动序列化为 JSON
    # 注意：这里返回的是字符串，会变成 JSON 字符串；想返回 JSON 对象应写成 {"message": "获取分类成功!"}
    categories=await news.get_categories(db,skip,limit)
    return {
        "code":200,
        "message": "获取分类成功!",
        "data":categories
    }
@router.get("/list")
async def get_news_list(
    category_id: int = Query(..., alias="categoryId"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, alias="pageSize", le=100),
    db: AsyncSession = Depends(get_db),
):
    # 处理分页规则 查询新闻列表 计算总量 计算是否还有更多
    offset=(page-1)*page_size
    news_list=await news.get_news_list(db,category_id,offset,page_size)
    total=await news.get_news_count(db,category_id)
    # (跳过的 + 当前列表里面的数量) < 总量
    has_more = (offset + len(news_list)) < total
    return {
        "code": 200,
        "message": "获取新闻列表成功",
        "data": {
            "list":news_list,
            "total":total,
            "hasmore": has_more,
        }
    }


@router.get("/detail")
async def get_news_detail(
    news_id: int = Query(..., alias="id"), db: AsyncSession = Depends(get_db)
):
    # 获取新闻详情 + 浏览量+1 + 相关新闻
    news_detail = await news.get_news_detail(db, news_id)
    if not news_detail:
        raise HTTPException(status_code=404, detail="新闻不存在")

    views_res = await news.increase_news_views(db, news_detail.id)
    if not views_res:
        raise HTTPException(status_code=404, detail="新闻不存在")

    related_news = await news.get_related_news(
        db, news_detail.id, news_detail.category_id
    )
    return {
        "code": 200,
        "message": "success",
        "data": {
            "id": news_detail.id,
            "title": news_detail.title,
            "content": news_detail.content,
            "image": news_detail.image,
            "author": news_detail.author,
            "publishTime": news_detail.publish_time,
            "categoryId": news_detail.category_id,
            "views": news_detail.views,
            "relatedNews": related_news,
        },
    }
