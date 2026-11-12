# 用户模块的所有路由
# APIRouter 用于把一组相关的接口拆到单独文件里，最后在 main.py 中统一注册
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
# UserRequest：请求体模型，包含 username / password，FastAPI 会自动校验并解析 JSON
from crud import users
from schemas.users import UserRequest
# get_db：数据库会话依赖，请求进入时创建会话，请求结束后自动关闭
from config.db_config import get_db
from starlette import status
# 创建 APIRouter 实例
# prefix：该模块下所有接口的统一路径前缀，最终路径为 /api/user/xxx
# tags：OpenAPI 文档（/docs）中的分组名称
router = APIRouter(prefix="/api/user", tags=["users"])

# POST /api/user/register：用户注册
# user_data：请求体，按 UserRequest 的结构校验；校验失败时 FastAPI 自动返回 422
# db：通过 Depends(get_db) 注入的异步数据库会话
# 注：目前是写死的假数据，后续应改为「查重 → 写入数据库 → 生成 token」的真实逻辑
@router.post("/register")
async def register(user_data: UserRequest, db: AsyncSession = Depends(get_db)):
    # 返回内容会被 FastAPI 自动序列化为 JSON
    #验证用户是否存在。创建用户 生成token 响应结果
    existing_user=await users.get_user_by_username(db,user_data.username)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="用户已存在")
    user=await users.create_user(db,user_data)
    token=await users.create_token(db,user.id)
    return {
        "code": 200,
        "message": "注册成功",
        # data 中的 token 和 userInfo 是前端登录后需要保存的核心字段
        "data": {
            "token": token,
            "userInfo": {
                "id": user.id,
                "username": user.username,
                "bio": user.bio,
                "avatar": user.avatar,
            },
        },
    }