# 用户模块的所有路由
# APIRouter 用于把一组相关的接口拆到单独文件里，最后在 main.py 中统一注册
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
# UserRequest：请求体模型，包含 username / password，FastAPI 会自动校验并解析 JSON
from crud import users
from schemas.users import (
    PasswordUpdateRequest,
    UserAuthRespense,
    UserInfoResponse,
    UserRequest,
    UserUpdateRequest,
)
# get_db：数据库会话依赖，请求进入时创建会话，请求结束后自动关闭
from config.db_config import get_db
from starlette import status

from utils.response import success_response
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
    # 验证用户是否存在。创建用户 生成token 响应结果
    existing_user=await users.get_user_by_username(db,user_data.username)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="用户已存在")
    user=await users.create_user(db,user_data)
    token=await users.create_token(db,user.id)
    # return {
    #     "code": 200,
    #     "message": "注册成功",
    #     # data 中的 token 和 userInfo 是前端登录后需要保存的核心字段
    #     "data": {
    #         "token": token,
    #         "userInfo": {
    #             "id": user.id,
    #             "username": user.username,
    #             "bio": user.bio,
    #             "avatar": user.avatar,
    #         },
    #     },
    # }
    response_data = UserAuthRespense(token=token,user_info=UserInfoResponse.model_validate(user))
    return success_response(message="注册成功", data=response_data)
# 登陆
# 路径必须以 / 开头，否则会和 prefix("/api/user") 拼成 /api/userlogin
@router.post("/login")
async def login_user(user_data: UserRequest, db: AsyncSession = Depends(get_db)):
    user=await users.authenticate_user(db,user_data.username,user_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="用户名或密码错误")
    token=await users.create_token(db,user.id)
    response_data=UserAuthRespense(token=token,user_info=UserInfoResponse.model_validate(user))
    # 忘记 return 时接口会返回 200 + null，这里必须把成功响应返回出去
    return success_response(message="登陆成功",data=response_data)

# 请求头里取 token，查出对应用户；查不到说明未登录或 token 已过期
# 前端发送的是 Authorization: <token>（没有 Bearer 前缀），所以不需要额外解析
async def get_current_user(
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db),
):
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="未登录或登录已失效")
    user = await users.get_user_by_token(db, authorization)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="未登录或登录已失效")
    return user

# GET /api/user/info：根据 token 返回当前用户信息
@router.get("/info")
async def get_user_info(current_user=Depends(get_current_user)):
    # data 直接放用户信息，前端把 response.data.data 赋给 userInfo
    return success_response(
        message="获取用户信息成功",
        data=UserInfoResponse.model_validate(current_user),
    )

# PUT /api/user/update：修改个人资料（目前只支持 bio）
@router.put("/update")
async def update_user_info(
    user_data: UserUpdateRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user = await users.update_user_bio(db, current_user, user_data.bio)
    # 返回更新后的完整用户信息，前端可以直接用它刷新本地状态
    return success_response(
        message="更新个人资料成功",
        data=UserInfoResponse.model_validate(user),
    )

# PUT /api/user/password：修改密码，需要原密码校验
@router.put("/password")
async def update_password(
    user_data: PasswordUpdateRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user = await users.update_user_password(
        db, current_user, user_data.old_password, user_data.new_password
    )
    # crud 返回 None 表示原密码校验失败
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="原密码错误")
    return success_response(message="密码修改成功")
