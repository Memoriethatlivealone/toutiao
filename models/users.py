"""用户相关 ORM 模型定义。

使用 SQLAlchemy 2.0 声明式风格（Mapped / mapped_column），对应 database.sql 中的：
    - user：用户信息表

created_at / updated_at 由 models.news 中的 Base 统一提供，与 user 表结构一致。
"""

from typing import Optional

from sqlalchemy import Enum, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

# Base 是公共基类（定义在 models/base.py），所有模型共用同一个 metadata
from models.base import Base


# 用户表：存储账号、密码及个人资料
class User(Base):
    __tablename__ = "user"
    # 表级约束：与 database.sql 中的索引名保持一致
    __table_args__ = (
        # 用户名唯一索引，登录账号不能重复
        # 参数顺序：索引名、列名、unique=True 表示唯一索引
        Index("username_UNIQUE", "username", unique=True),
        # 手机号唯一索引，多个 NULL 不冲突（未填手机号时）
        Index("phone_UNIQUE", "phone", unique=True),
    )
    # 用户主键，自增
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="用户ID",
    )
    # 用户名，唯一且必填，用于登录
    username: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="用户名",
    )
    # 密码，存的是 bcrypt 加密后的哈希，绝不能存明文
    password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="密码（加密存储）",
    )
    # 昵称，展示用，可为空
    nickname: Mapped[Optional[str]] = mapped_column(
        String(50),
        comment="昵称",
    )
    # 头像地址，可为空
    avatar: Mapped[Optional[str]] = mapped_column(
        String(255),
        comment="头像URL",
    )
    # 性别：枚举值 male / female / unknown，默认为 unknown
    gender: Mapped[Optional[str]] = mapped_column(
        Enum("male", "female", "unknown", name="user_gender"),
        default="unknown",
        nullable=True,
        comment="性别",
    )
    # 个人简介，可为空
    bio: Mapped[Optional[str]] = mapped_column(
        String(500),
        comment="个人简介",
    )
    # 手机号，唯一但允许为空（MySQL 中多个 NULL 不冲突）
    phone: Mapped[Optional[str]] = mapped_column(
        String(20),
        comment="手机号",
    )
    # created_at / updated_at 两列由 Base 继承而来，无需重复定义

    def __repr__(self):
        """调试时打印用户关键信息，避免输出密码哈希。"""
        return f"<User(id={self.id}, username='{self.username}')>"