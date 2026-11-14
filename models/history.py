"""浏览历史相关 ORM 模型定义。

对应 database.sql 中的 history 表：
    - 记录「哪个用户在什么时候看了哪条新闻」
    - 表里没有唯一约束，但业务上同一用户同一条新闻只保留一条最新记录
      （由 crud 层在新增时先删旧记录来保证）
    - 只有 view_time 一列时间字段，所以继承 PlainBase
"""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer
from sqlalchemy.orm import Mapped, mapped_column

from models.base import PlainBase


class History(PlainBase):
    __tablename__ = "history"
    # 表级约束：与 database.sql 中的索引名保持一致
    __table_args__ = (
        Index("fk_history_user_idx", "user_id"),
        Index("fk_history_news_idx", "news_id"),
        # 浏览时间索引，按时间倒序取列表是最高频的查询
        Index("idx_view_time", "view_time"),
    )

    # 历史ID，自增主键
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="历史ID",
    )
    # 浏览人ID，用户删除时历史记录级联删除
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("user.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        comment="用户ID",
    )
    # 被浏览的新闻ID，新闻删除时历史记录级联删除
    news_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("news.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        comment="新闻ID",
    )
    # 浏览时间
    view_time: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        comment="浏览时间",
    )

    def __repr__(self):
        """调试时打印历史关键信息。"""
        return f"<History(id={self.id}, user_id={self.user_id}, news_id={self.news_id})>"