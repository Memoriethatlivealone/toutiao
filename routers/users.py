# 用户模块的所有路由
# APIRouter 用于把一组相关的接口拆到单独文件里，最后在 main.py 中统一注册
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
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

from utils.auth import get_current_user
from utils.response import success_response
# 创建 APIRouter 实例
# prefix：该模块下所有接口的统一路径前缀，最终路径为 /api/user/xxx
# tags：OpenAPI 文档（/docs）中的分组名称
router = APIRouter(prefix="/api/user", tags=["users"])

# ---------------------------------------------------------------------------
# 头像上传配置
# ---------------------------------------------------------------------------
# 头像保存目录：项目根/static/avatars，通过 /static/avatars/xxx.png 访问
# 用绝对路径，避免从不同目录启动 uvicorn 时写错位置
AVATAR_DIR = Path(__file__).resolve().parent.parent / "static" / "avatars"
# 只允许常见的图片格式，content_type -> 扩展名
ALLOWED_IMAGE_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/gif": ".gif",
    "image/webp": ".webp",
}
# 头像大小上限：2MB
MAX_AVATAR_SIZE = 2 * 1024 * 1024


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

# GET /api/user/info：根据 token 返回当前用户信息
@router.get("/info")
async def get_user_info(current_user=Depends(get_current_user)):
    # data 直接放用户信息，前端把 response.data.data 赋给 userInfo
    return success_response(
        message="获取用户信息成功",
        data=UserInfoResponse.model_validate(current_user),
    )

# PUT /api/user/update：修改个人资料（昵称、简介）
@router.put("/update")
async def update_user_info(
    user_data: UserUpdateRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # exclude_unset=True：只取请求体里真正传了的字段
    # 这样前端只传 nickname 时，bio 不会被覆盖成 None
    fields = user_data.model_dump(exclude_unset=True)
    user = await users.update_user_profile(db, current_user, **fields)
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


# POST /api/user/logout：退出登录，删除服务端 token
@router.post("/logout")
async def logout(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # 删掉 token 后，旧 token 再请求任何需要登录的接口都会返回 401
    await users.delete_token(db, current_user.id)
    return success_response(message="退出登录成功")


# POST /api/user/avatar：上传头像
# 前端用 multipart/form-data 提交，字段名必须是 file
@router.post("/avatar")
async def upload_avatar(
    file: UploadFile = File(..., description="头像图片，支持 jpg/png/gif/webp，最大 2MB"),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # 1. 校验格式：content_type 由客户端声明，这里只做基础过滤
    suffix = ALLOWED_IMAGE_TYPES.get(file.content_type)
    if not suffix:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="只支持 jpg / png / gif / webp 格式的图片",
        )

    # 2. 读取内容并校验大小（一次性读进内存，2MB 上限可控）
    content = await file.read()
    if not content:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="上传的文件为空")
    if len(content) > MAX_AVATAR_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="图片大小不能超过 2MB",
        )

    # 3. 用 uuid 生成文件名：避免同名覆盖，也避免用户提供的文件名带路径穿越
    AVATAR_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid.uuid4().hex}{suffix}"
    (AVATAR_DIR / filename).write_bytes(content)

    # 4. 删除旧头像文件，避免 static/avatars 越积越多
    old_avatar = current_user.avatar or ""
    if old_avatar.startswith("/static/avatars/"):
        old_file = AVATAR_DIR / old_avatar.rsplit("/", 1)[-1]
        if old_file.exists():
            old_file.unlink()

    # 5. 把新地址写进数据库，前端拼上 baseURL 就能显示
    avatar_url = f"/static/avatars/{filename}"
    user = await users.update_user_avatar(db, current_user, avatar_url)
    return success_response(
        message="头像上传成功",
        data={"avatar": user.avatar},
    )
