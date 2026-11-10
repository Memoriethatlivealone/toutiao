"""数据库配置模块。

负责创建 SQLAlchemy 异步引擎、异步会话工厂，并对外提供 FastAPI 依赖项 get_db。
"""

import os
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

# ---------------------------------------------------------------------------
# 数据库连接参数
# 默认值对应本地开发环境，部署时通过环境变量覆盖，避免把密码写死在代码里
# ---------------------------------------------------------------------------
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "1851622159")
DB_NAME = os.getenv("DB_NAME", "news_app")

# 异步数据库 URL，驱动为 aiomysql，字符集必须为 utf8mb4（支持 emoji）
ASYNC_DATABASE_URL = (
    f"mysql+aiomysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    "?charset=utf8mb4"
)

# ---------------------------------------------------------------------------
# 异步引擎
# ---------------------------------------------------------------------------
# echo：是否打印执行的 SQL，调试时设置环境变量 DB_ECHO=1 打开
# pool_size：连接池中保持的常驻连接数
# max_overflow：连接繁忙时允许临时额外创建的连接数（上限 = pool_size + max_overflow）
# pool_recycle：连接存活超过该秒数后回收重建，避免被 MySQL 的 wait_timeout 主动断开
async_engine: AsyncEngine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=os.getenv("DB_ECHO", "0") == "1",
    pool_size=10,
    max_overflow=20,
    pool_recycle=3600,
)

# ---------------------------------------------------------------------------
# 异步会话工厂
# ---------------------------------------------------------------------------
# expire_on_commit=False：commit 之后对象属性仍然可读，不会触发额外的查询
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI 依赖项：为每个请求提供独立的数据库会话。
    正常流程：请求处理完成后自动 commit。
    异常流程：捕获异常后 rollback，再把异常抛给上层，由 FastAPI 统一返回错误响应。
    会话的关闭由 `async with` 负责，无需手动 close。
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise