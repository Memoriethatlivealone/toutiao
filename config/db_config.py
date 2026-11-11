"""数据库配置模块。

负责创建 SQLAlchemy 异步引擎、异步会话工厂，并对外提供 FastAPI 依赖项 get_db。
"""

import os
from collections.abc import AsyncGenerator
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

# 把项目根目录 .env 里的键值对加载到环境变量中
# 用绝对路径，避免从其他目录启动时找不到文件
# 默认 override=False：已存在的系统环境变量优先，不会被 .env 覆盖
ENV_FILE = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(ENV_FILE)

# ---------------------------------------------------------------------------
# 数据库连接参数
# 统一从环境变量读取（.env 已由上面的 load_dotenv 载入）
# 第二个参数是默认值，.env 里没配时使用
# ---------------------------------------------------------------------------
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "news_app")
DB_ECHO = os.getenv("DB_ECHO", "0") == "1"

# 异步数据库 URL，驱动为 aiomysql，字符集必须为 utf8mb4（支持 emoji）
# 用 URL.create 构造，密码里有 @ : / 等特殊字符时也能正确转义
ASYNC_DATABASE_URL = URL.create(
    drivername="mysql+aiomysql",
    username=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT,
    database=DB_NAME,
    query={"charset": "utf8mb4"},
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
    echo=DB_ECHO,
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