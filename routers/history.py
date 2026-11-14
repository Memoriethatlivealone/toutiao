"""浏览历史模块的路由。

所有接口都需要登录（Authorization 请求头带 token），
返回结构与项目统一格式一致：{code, message, data}。

注意：删除接口路径里的 id 是「新闻 id」，不是历史表主键，
因为前端历史列表项里的 id 就是新闻 id。
"""

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from config.db_config import get_db
from crud import history as history_crud
from crud import news as news_crud
from schemas.interaction import NewsIdRequest
from utils.auth import get_current_user
from utils.response import success_response

router = APIRouter(prefix="/api/history", tags=["history"])


@router.post("/add")
async def add_history(
    user_data: NewsIdRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """记录一次浏览。同一新闻重复浏览只更新时间，不会产生多条记录。"""
    # 先确认新闻存在，否则外键约束会直接抛数据库异常（变成 500）
    if not await news_crud.get_news_detail(db, user_data.news_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="新闻不存在")

    await history_crud.add_history(db, current_user.id, user_data.news_id)
    return success_response(message="记录浏览成功", data={"newsId": user_data.news_id})


@router.delete("/clear")
async def clear_history(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """清空当前用户的全部浏览历史。"""
    count = await history_crud.clear_history(db, current_user.id)
    return success_response(message="清空历史成功", data={"deleted": count})


@router.delete("/delete/{news_id}")
async def delete_history(
    news_id: int = Path(..., gt=0, description="新闻ID"),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """删除某条新闻的浏览记录。"""
    removed = await history_crud.delete_history(db, current_user.id, news_id)
    if not removed:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="历史记录不存在")
    return success_response(message="删除成功")


@router.get("/list")
async def get_history_list(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取浏览历史列表，按浏览时间倒序，最多 50 条。"""
    items = await history_crud.get_history_list(db, current_user.id)
    return success_response(data={"list": items, "total": len(items)})