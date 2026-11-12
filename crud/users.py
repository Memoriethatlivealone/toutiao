import uuid
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from models.news import Category, News
from sqlalchemy import func, select, update

from models.users import User, UserToken
from schemas.users import UserRequest
# 密码加密/校验统一放在 utils/security.py，这里只导入需要用到的函数
from utils import security
from utils.security import get_hash_password

# 根据用户名查询数据
async def get_user_by_username(db:AsyncSession,username:str):
    query=select(User).where(User.username==username)
    result=await db.execute(query)
    return result.scalar_one_or_none()

# 创建用户
async def create_user(db:AsyncSession,user_data:UserRequest):
    #先密码加密处理 然后add新增
    hashed_password = security.get_hash_password(user_data.password)
    user = User(username=user_data.username, password=hashed_password)
    db.add(user)
    # flush 把 INSERT 立刻发给数据库，拿到自增 id；commit 由 get_db 依赖统一处理
    await db.commit()
    # 从数据库重新读取，确保 created_at 等由数据库填充的字段也有值
    await db.refresh(user)
    return user

# 生成token
async def create_token(db:AsyncSession,user_id:int):
    # 生成token加上过期时间，查询数据库当前用户是否有token 有：更新。没有：添加
    token=str(uuid.uuid4())
    # imedelta(days=7,hours=2,minutes=30,second=10) 
    expires_at = datetime.now() + timedelta(days=7)
    query=select(UserToken).where(UserToken.user_id==user_id)
    result=await db.execute(query)
    # scalar_one_or_none 必须调用，否则拿到的是方法对象，永远为真
    user_token=result.scalar_one_or_none()
    if user_token:
        user_token.token=token
        user_token.expires_at=expires_at
    else:
        user_token=UserToken(user_id=user_id,token=token,expires_at=expires_at)
        db.add(user_token)
    # 放在 if/else 外面：新增和更新两个分支都要提交
    await db.commit()

    return token