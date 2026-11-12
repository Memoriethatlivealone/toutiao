"""新闻相关 ORM 模型定义。

使用 SQLAlchemy 2.0 声明式风格（Mapped / mapped_column），
包含两个表：
    - news_category：新闻分类表
    - news：新闻内容表
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

# Base 是公共基类，放在 models/base.py 中，供所有模型文件共用
from models.base import Base


# 新闻分类表：如「科技」「财经」「体育」等
class Category(Base):
    __tablename__ = "news_category"

    # 分类主键，自增
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="分类id",
    )
    # 分类名称，唯一，不允许重复
    name: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        comment="分类名称",
    )
    # 排序值，越小越靠前，默认 0
    sort_order: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="排序",
    )

    def __repr__(self):
        """调试时打印分类信息，便于查看对象内容。"""
        return (
            f"<Category(id={self.id}, name={self.name}, "
            f"sort_order={self.sort_order})>"
        )


# 新闻表：存储新闻正文及关联的分类
class News(Base):
    __tablename__ = "news"

    # 联合建索引：提升查询速度。
    # 按分类筛选新闻、按发布时间排序是高频查询，因此对这两列建索引。
    __table_args__ = (
        Index("fk_news_category_idx", "category_id"),  # 分类外键索引
        Index("idx_publish_time", "publish_time"),  # 发布时间索引
    )

    # 新闻主键，自增
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="新闻ID",
    )
    # 新闻标题，必填
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="新闻标题",
    )
    # 新闻简介，用于列表页摘要，可为空
    description: Mapped[Optional[str]] = mapped_column(
        String(500),
        comment="新闻简介",
    )
    # 新闻正文，长文本类型，必填
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="新闻内容",
    )
    # 封面图片地址，可为空
    image: Mapped[Optional[str]] = mapped_column(
        String(255),
        comment="封面图片URL",
    )
    # 作者，可为空
    author: Mapped[Optional[str]] = mapped_column(
        String(50),
        comment="作者",
    )
    # 分类外键，关联 news_category.id，必填
    category_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("news_category.id"),
        nullable=False,
        comment="分类ID",
    )
    # 浏览量，默认 0
    views: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="浏览量",
    )
    # 发布时间，默认取当前时间
    publish_time: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        comment="发布时间",
    )

    def __repr__(self):
        """调试时打印新闻关键信息，避免输出整篇正文。"""
        return f"<News(id={self.id}, title='{self.title}', views={self.views})>"