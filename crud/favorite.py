"""收藏模块的数据访问层。

所有查询都带 user_id 条件，保证用户只能操作自己的收藏。
时间字段统一格式化成 "YYYY-MM-DD HH:MM:SS" 返回，前端可以直接展示。
"""

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.favorite import Favorite
from models.news import News

# 时间输出格式，与前端展示习惯一致
TIME_FORMAT = "%Y-%m-%d %H:%M:%S"


def _format_time(value):
    """把 datetime 转成字符串；空值原样返回 None。"""
    return value.strftime(TIME_FORMAT) if value else None


def _to_dict(favorite: Favorite, news: News) -> dict:
    """把收藏记录和新闻拼成前端需要的结构。

    id 用新闻 id（不是收藏表主键）：前端用 item.id 跳转详情、判断是否已收藏。
    """
    return {
        "id": news.id,
        "title": news.title,
        "image": news.image,
        "author": news.author,
        "publishTime": _format_time(news.publish_time),
        "categoryId": news.category_id,
        "favoriteTime": _format_time(favorite.created_at),
    }


async def is_favorite(db: AsyncSession, user_id: int, news_id: int) -> bool:
    """判断某用户是否已收藏某条新闻。"""
    query = select(Favorite.id).where(
        Favorite.user_id == user_id,
        Favorite.news_id == news_id,
    )
    result = await db.execute(query)
    return result.scalar_one_or_none() is not None


async def add_favorite(db: AsyncSession, user_id: int, news_id: int) -> bool:
    """添加收藏。

    返回 True 表示新增成功，False 表示之前已经收藏过（幂等，不报错）。
    """
    if await is_favorite(db, user_id, news_id):
        return False
    db.add(Favorite(user_id=user_id, news_id=news_id))
    await db.commit()
    return True


async def remove_favorite(db: AsyncSession, user_id: int, news_id: int) -> int:
    """取消收藏，返回实际删除的行数（0 表示本来就没收藏）。"""
    stmt = delete(Favorite).where(
        Favorite.user_id == user_id,
        Favorite.news_id == news_id,
    )
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount


async def clear_favorites(db: AsyncSession, user_id: int) -> int:
    """清空某用户的全部收藏，返回删除数量。"""
    stmt = delete(Favorite).where(Favorite.user_id == user_id)
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount


async def get_favorite_list(
    db: AsyncSession, user_id: int, page: int = 1, page_size: int = 10
) -> tuple[list[dict], int]:
    """分页查询收藏列表，按收藏时间倒序。

    返回 (当前页列表, 总条数)，总条数用于前端判断是否还有更多。
    """
    total = await db.scalar(
        select(func.count()).select_from(Favorite).where(Favorite.user_id == user_id)
    )

    query = (
        select(Favorite, News)
        # 内连接新闻表：新闻被删除时外键级联删掉了收藏，这里自然也不会出现
        .join(News, Favorite.news_id == News.id)
        .where(Favorite.user_id == user_id)
        # 同秒内多条记录时按 id 倒序兜底，保证「最近收藏的排最前」的顺序稳定
        .order_by(Favorite.created_at.desc(), Favorite.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await db.execute(query)
    items = [_to_dict(favorite, news) for favorite, news in result.all()]
    return items, int(total or 0)