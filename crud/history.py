"""浏览历史模块的数据访问层。

业务约定：同一用户同一条新闻只保留一条记录，再次浏览时更新浏览时间。
history 表没有唯一约束，所以新增时先删除旧记录再插入。
"""

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.history import History
from models.news import News

# 时间输出格式，与前端展示习惯一致
TIME_FORMAT = "%Y-%m-%d %H:%M:%S"

# 历史列表最多返回的条数（与前端本地最多保存 50 条保持一致）
DEFAULT_HISTORY_LIMIT = 50


def _format_time(value):
    """把 datetime 转成字符串；空值原样返回 None。"""
    return value.strftime(TIME_FORMAT) if value else None


def _to_dict(history: History, news: News) -> dict:
    """把历史记录和新闻拼成前端需要的结构。

    id 用新闻 id：前端用 item.id 跳转详情、删除单条记录。
    """
    return {
        "id": news.id,
        "title": news.title,
        "image": news.image,
        "author": news.author,
        "publishTime": _format_time(news.publish_time),
        "categoryId": news.category_id,
        "viewTime": _format_time(history.view_time),
    }


async def add_history(db: AsyncSession, user_id: int, news_id: int) -> None:
    """记录一次浏览。

    先删掉该用户对这条新闻的旧记录，再插入新记录，
    这样列表里同一条新闻永远只出现一次，且时间是最新的。
    """
    await db.execute(
        delete(History).where(
            History.user_id == user_id,
            History.news_id == news_id,
        )
    )
    db.add(History(user_id=user_id, news_id=news_id))
    await db.commit()


async def clear_history(db: AsyncSession, user_id: int) -> int:
    """清空某用户的全部浏览历史，返回删除数量。"""
    stmt = delete(History).where(History.user_id == user_id)
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount


async def delete_history(db: AsyncSession, user_id: int, news_id: int) -> int:
    """删除某条新闻的历史记录，返回删除行数（0 表示记录不存在）。"""
    stmt = delete(History).where(
        History.user_id == user_id,
        History.news_id == news_id,
    )
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount


async def get_history_list(
    db: AsyncSession, user_id: int, limit: int = DEFAULT_HISTORY_LIMIT
) -> list[dict]:
    """查询浏览历史，按浏览时间倒序，默认最多 50 条。"""
    query = (
        select(History, News)
        .join(News, History.news_id == News.id)
        .where(History.user_id == user_id)
        # 同秒内多条记录时按 id 倒序兜底，保证「最近插入的排最前」的顺序稳定
        .order_by(History.view_time.desc(), History.id.desc())
        .limit(limit)
    )
    result = await db.execute(query)
    return [_to_dict(history, news) for history, news in result.all()]