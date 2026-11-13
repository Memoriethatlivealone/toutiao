from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict,Field

class UserRequest(BaseModel):
    username:str=Field(...,max_length=50,description="用户名，登录账号，最长50个字符")
    password:str=Field(...,max_length=72,description="明文密码，最长72字节（bcrypt 算法的长度上限）")
# user_info对应的类 ：基础类+info类（id、用户名）
class UserInfoBase(BaseModel):
    """用户信息基础模型：只放公开展示、可复用的用户字段。"""
    # 以下字段在数据库中都允许为空，所以这里用 Optional 并默认 None
    # max_length 与 models/users.py 中对应列的 String(n) 保持一致
    nickname:Optional[str]=Field(None,max_length=50,description="昵称")
    avatar:Optional[str]=Field(None,max_length=255,description="头像URL")
    # 性别用枚举校验：只允许 male / female / unknown，与数据库 Enum 一致
    gender:Optional[Literal["male","female","unknown"]]=Field(None,description="性别：male / female / unknown")
    bio:Optional[str]=Field(None,max_length=500,description="个人简介")

class UserInfoResponse(UserInfoBase):
    """用户信息响应模型：在基础模型上追加主键 id。"""
    id:int
    username:str
    #模型类配置
    model_config=ConfigDict(
        populate_by_name=True,#alias/字段名兼容
        from_attributes=True,#允许从orm对象属性中取值
    )
    
# 修改个人资料：目前只开放 bio，后续要改昵称/头像在这里加字段即可
class UserUpdateRequest(BaseModel):
    bio:Optional[str]=Field(None,max_length=500,description="个人简介，传 null 表示清空")

    model_config=ConfigDict(
        populate_by_name=True,#alias/字段名兼容
    )

# 修改密码：前端传的是 camelCase（oldPassword/newPassword），所以这里用 alias 对应
class PasswordUpdateRequest(BaseModel):
    old_password:str=Field(...,alias="oldPassword",max_length=72,description="原密码")
    new_password:str=Field(...,alias="newPassword",min_length=6,max_length=72,description="新密码，至少6位")

    model_config=ConfigDict(
        populate_by_name=True,#alias/字段名兼容
    )

# data
class UserAuthRespense(BaseModel):
    token:str
    user_info: UserInfoResponse=Field(...,alias="userInfo")

    #模型类配置
    model_config=ConfigDict(
        populate_by_name=True,#alias/字段名兼容
        from_attributes=True,#允许从orm对象属性中取值

    )