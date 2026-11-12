"""所有 ORM 模型的公共基类。

news.py、users.py 等模型文件都从这里导入 Base，
这样所有模型共用同一个 metadata，建表、迁移时才能看到全部表。
"""

from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """所有模型的基类。

    统一提供 created_at / updated_at 两个时间字段，
    子类建表时会自动继承这两列，无需重复定义。
    """

    # 创建时间：插入记录时自动填充，之后不再变化
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        comment="创建时间",
    )
    # 更新时间：插入时填充，每次更新记录时自动刷新
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        comment="更新时间",
    )