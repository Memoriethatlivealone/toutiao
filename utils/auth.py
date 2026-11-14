"""登录校验依赖。

收藏、历史、用户信息等接口都需要「先拿到当前登录用户」，
把这段逻辑抽成 FastAPI 依赖，路由里写 current_user=Depends(get_current_user) 即可。

token 的传递方式与前端约定一致：
    Authorization: <token>    （没有 Bearer 前缀）
"""

from typing import Optional

from fastapi import Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from config.db_config import get_db
from crud import users


async def get_current_user(
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db),
):
    """从请求头取 token 并查出对应用户，失败统一返回 401。

    依赖注入会有缓存：路由函数里再声明一次 db=Depends(get_db) 时拿到的是同一个会话，
    不会重复创建连接。
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未登录或登录已失效",
        )
    user = await users.get_user_by_token(db, authorization)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未登录或登录已失效",
        )
    return user