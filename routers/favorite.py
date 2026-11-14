"""收藏模块的路由。

所有接口都需要登录（Authorization 请求头带 token），
返回结构与项目统一格式一致：{code, message, data}。
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from config.db_config import get_db
from crud import favorite as favorite_crud
from crud import news as news_crud
from schemas.interaction import NewsIdRequest
from utils.auth import get_current_user
from utils.response import success_response

router = APIRouter(prefix="/api/favorite", tags=["favorite"])


@router.get("/check")
async def check_favorite(
    news_id: int = Query(..., alias="newsId", gt=0, description="新闻ID"),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """查询当前用户是否收藏了指定新闻，前端用它决定按钮的选中状态。"""
    is_favorite = await favorite_crud.is_favorite(db, current_user.id, news_id)
    return success_response(data={"isFavorite": is_favorite})


@router.post("/add")
async def add_favorite(
    user_data: NewsIdRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """添加收藏。重复收藏不会报错，直接返回成功。"""
    # 先确认新闻存在，否则外键约束会直接抛数据库异常（变成 500）
    if not await news_crud.get_news_detail(db, user_data.news_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="新闻不存在")

    created = await favorite_crud.add_favorite(db, current_user.id, user_data.news_id)
    # created=False 表示之前已经收藏过，属于幂等场景，同样返回成功
    message = "收藏成功" if created else "已收藏过该新闻"
    return success_response(message=message, data={"newsId": user_data.news_id})


@router.delete("/remove")
async def remove_favorite(
    news_id: int = Query(..., alias="newsId", gt=0, description="新闻ID"),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """取消收藏。"""
    removed = await favorite_crud.remove_favorite(db, current_user.id, news_id)
    if not removed:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="未收藏该新闻")
    return success_response(message="取消收藏成功")


@router.delete("/clear")
async def clear_favorites(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """清空当前用户的全部收藏。"""
    count = await favorite_crud.clear_favorites(db, current_user.id)
    return success_response(message="清空收藏成功", data={"deleted": count})


@router.get("/list")
async def get_favorite_list(
    page: int = Query(1, ge=1, description="页码，从1开始"),
    page_size: int = Query(10, alias="pageSize", ge=1, le=100, description="每页条数"),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """分页获取收藏列表，按收藏时间倒序。"""
    items, total = await favorite_crud.get_favorite_list(
        db, current_user.id, page, page_size
    )
    return success_response(
        data={
            "list": items,
            "total": total,
            "hasMore": page * page_size < total,
        }
    )