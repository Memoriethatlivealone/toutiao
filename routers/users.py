# 用户模块的所有路由
# APIRouter 用于把一组相关的接口拆到单独文件里，最后在 main.py 中统一注册
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
# UserRequest：请求体模型，包含 username / password，FastAPI 会自动校验并解析 JSON
from schemas.users import UserRequest
# get_db：数据库会话依赖，请求进入时创建会话，请求结束后自动关闭
from config.db_config import get_db

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
    return {
        "code": 200,
        "message": "注册成功",
        # data 中的 token 和 userInfo 是前端登录后需要保存的核心字段
        "data": {
            "token": "用户访问令牌",
            "userInfo": {
                "id": 1,
                "username": user_data.username,
                "bio": "这个人很懒，什么都没留下",
                "avatar": "https://fastly.jsdelivr.net/npm/@vant/assets/cat.jpeg",
            },
        },
    }