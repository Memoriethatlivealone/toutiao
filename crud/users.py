from sqlalchemy.ext.asyncio import AsyncSession
from models.news import Category, News
from sqlalchemy import func, select, update

from models.users import User
from schemas.users import UserRequest
# 密码加密/校验统一放在 utils/security.py，这里只导入需要用到的函数
from utils.security import hash_password

#根据用户名查询数据
async def get_user_by_username(db:AsyncSession,username:str):
    query=select(User).where(User.username==username)
    result=await db.execute(query)
    return result.scalar_one_or_none()

#创建用户
async def create_user(db:AsyncSession,user_data:UserRequest):
    #先密码加密处理 然后add新增
    hashed_password = hash_password(user_data.password)
    user = User(username=user_data.username, password=hashed_password)
    db.add(user)
    # flush 把 INSERT 立刻发给数据库，拿到自增 id；commit 由 get_db 依赖统一处理
    await db.flush()
    # 从数据库重新读取，确保 created_at 等由数据库填充的字段也有值
    await db.refresh(user)
    return user
