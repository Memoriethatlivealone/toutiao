import uuid
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from models.news import Category, News
from sqlalchemy import delete, func, select, update

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

async def authenticate_user(db:AsyncSession,username:str,password:str):
    user=await get_user_by_username(db,username)
    if not user:
        return None
    #明文和密文的对比
    if not security.verify_password(password,user.password):
        return None

    return user

# 根据 token 查询用户：token 必须存在且未过期
async def get_user_by_token(db:AsyncSession,token:str):
    query=(
        select(User)
        # user_token.user_id -> user.id 关联，一个用户同一时间只会有一条 token 记录
        .join(UserToken,UserToken.user_id==User.id)
        .where(UserToken.token==token)
        # 过期时间必须大于当前时间，过期 token 视为未登录
        .where(UserToken.expires_at>datetime.now())
    )
    result=await db.execute(query)
    return result.scalar_one_or_none()

# 更新个人资料：只更新明确传进来的字段
# 用 UNSET 哨兵区分「没传这个字段」和「传了 null 想清空」，
# 比如只改昵称时 bio 是 UNSET，不会被误清空
UNSET = object()


async def update_user_profile(
    db: AsyncSession,
    user: User,
    nickname=UNSET,
    bio=UNSET,
):
    # 直接改 ORM 对象的属性，SQLAlchemy 会自动标记为脏数据并生成 UPDATE
    if nickname is not UNSET:
        user.nickname = nickname
    if bio is not UNSET:
        user.bio = bio
    await db.commit()
    await db.refresh(user)
    return user


# 更新头像地址（图片文件本身由路由层负责保存）
async def update_user_avatar(db: AsyncSession, user: User, avatar_url: str):
    user.avatar = avatar_url
    await db.commit()
    await db.refresh(user)
    return user


# 退出登录：删除该用户的 token，之后的请求都会返回 401
async def delete_token(db: AsyncSession, user_id: int) -> int:
    stmt = delete(UserToken).where(UserToken.user_id == user_id)
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount

# 修改密码：先校验原密码，正确才写入新哈希
# 返回 None 表示原密码不对，由路由层转换成 400
async def update_user_password(db:AsyncSession,user:User,old_password:str,new_password:str):
    if not security.verify_password(old_password,user.password):
        return None
    # 新密码同样要加密，数据库里永远不存明文
    user.password=security.get_hash_password(new_password)
    await db.commit()
    await db.refresh(user)
    return user