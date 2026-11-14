"""收藏相关 ORM 模型定义。

对应 database.sql 中的 favorite 表：
    - 记录「哪个用户收藏了哪条新闻」
    - (user_id, news_id) 联合唯一，同一用户不能重复收藏同一条新闻
    - 只有 created_at 一列时间字段，所以继承 PlainBase
"""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer
from sqlalchemy.orm import Mapped, mapped_column

from models.base import PlainBase


class Favorite(PlainBase):
    __tablename__ = "favorite"
    # 表级约束：与 database.sql 中的索引名保持一致
    __table_args__ = (
        # 联合唯一索引：同一用户 + 同一条新闻只能有一条记录
        Index("user_news_unique", "user_id", "news_id", unique=True),
        Index("fk_favorite_user_idx", "user_id"),
        Index("fk_favorite_news_idx", "news_id"),
    )

    # 收藏ID，自增主键
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="收藏ID",
    )
    # 收藏人ID，用户删除时收藏记录级联删除
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("user.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        comment="用户ID",
    )
    # 被收藏的新闻ID，新闻删除时收藏记录级联删除
    news_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("news.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        comment="新闻ID",
    )
    # 收藏时间
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        comment="收藏时间",
    )

    def __repr__(self):
        """调试时打印收藏关键信息。"""
        return f"<Favorite(id={self.id}, user_id={self.user_id}, news_id={self.news_id})>"