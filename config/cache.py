"""Redis 缓存配置模块。

负责创建全局异步 Redis 客户端，并对外提供缓存读写方法和 FastAPI 依赖项。
用的是 redis.asyncio 异步客户端，读写都要配合 async/await 使用。
"""

import json
import os
from collections.abc import AsyncGenerator
from pathlib import Path
from typing import Any

import redis.asyncio as redis
from dotenv import load_dotenv

# 和 db_config 一样，从项目根目录 .env 读取连接参数
# 用绝对路径，避免从其他目录启动时找不到文件
ENV_FILE = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(ENV_FILE)

# ---------------------------------------------------------------------------
# Redis 连接参数
# 和 db_config 一样，统一从项目根目录 .env 读取，第二个参数是默认值
# ---------------------------------------------------------------------------
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "1"))
# 没设置密码时传 None，而不是空字符串，否则 Redis 会当作“密码为空”去认证
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD") or None

# ---------------------------------------------------------------------------
# 创建 Redis 连接对象（全局单例）
# ---------------------------------------------------------------------------
# 客户端内部自带连接池，全局创建一次共享即可，不需要每个请求新建
# decode_responses=True：读出来的键值自动解码成 str，不用再手动 .decode()
# socket_connect_timeout / socket_timeout：连接、读写超过 5 秒抛异常，避免请求一直挂起
# health_check_interval：空闲超过 30 秒的连接，使用前先 PING 一次，
#   防止拿到已被服务端断开的死连接
redis_client: redis.Redis = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    password=REDIS_PASSWORD,
    decode_responses=True,
    socket_connect_timeout=5,
    socket_timeout=5,
    health_check_interval=30,
)


async def get_redis() -> AsyncGenerator[redis.Redis, None]:
    """FastAPI 依赖项：提供全局 Redis 客户端。

    用法：在路由函数参数里声明 `r: redis.Redis = Depends(get_redis)`。
    客户端是全局共享的，这里不像数据库会话那样需要手动关闭。
    """
    yield redis_client


async def close_redis() -> None:
    """关闭 Redis 客户端，释放连接池。

    在 FastAPI 应用关闭时调用（main.py 的 lifespan 里）：
        @asynccontextmanager
        async def lifespan(app: FastAPI):
            yield
            await close_redis()

        app = FastAPI(lifespan=lifespan)
    """
    await redis_client.aclose()


# ---------------------------------------------------------------------------
# 缓存读写（设置和读取）
# ---------------------------------------------------------------------------
# 读取字符串
async def get_cache(key: str) -> str | None:
    """读取字符串缓存；键不存在或已过期时返回 None。"""
    return await redis_client.get(key)


# 读取：列表或字典
async def get_json_cache(key: str) -> Any | None:
    """读取以 JSON 存储的列表或字典；键不存在时返回 None。"""
    value = await redis_client.get(key)
    if value is None:
        return None
    return json.loads(value)


# 设置缓存
async def set_cache(key: str, value: Any, expire: int | None = 60) -> None:
    """写入缓存。

    - value 是字符串时原样存储，用 get_cache 读取
    - value 是列表、字典等对象时自动转成 JSON，用 get_json_cache 读取
    - expire：过期秒数，默认 60 秒；传 None 表示永不过期
    """
    # Redis 只能存字符串或字节：列表/字典必须先转成 JSON；字符串则原样存
    if isinstance(value, str):
        data = value
    else:
        data = json.dumps(value, ensure_ascii=False, default=str)

    await redis_client.set(key, data, ex=expire)