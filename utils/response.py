"""统一响应格式。

项目里所有接口（成功、业务异常、参数校验失败、未捕获异常）都返回同一结构：
    {"code": int, "message": str, "data": Any}

这样前端只需要写一套解析逻辑：永远是「看 code 判断成败，读 message 提示用户，
取 data 拿业务数据」。要调整外层字段（比如加 request_id），只改这个文件即可。
"""

from typing import Any

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse


def success_response(message: str = "success", data: Any = None) -> JSONResponse:
    """成功响应：HTTP 200，code 固定为 200。

    data 可以是 dict / list / Pydantic 模型 / ORM 对象，
    jsonable_encoder 负责把后两者转成可序列化的结构。
    """
    content = {
        "code": 200,
        "message": message,
        "data": data,
    }
    return JSONResponse(content=jsonable_encoder(content))


def error_response(
    code: int = 400,
    message: str = "请求失败",
    data: Any = None,
) -> JSONResponse:
    """错误响应：业务 code 同时作为 HTTP 状态码。

    保持「HTTP 状态码 == 业务 code」，前端既可以用 axios 的 catch 捕获，
    也能从 response.data.code 读取，两种方式拿到的值一致。
    """
    content = {
        "code": code,
        "message": message,
        "data": data,
    }
    return JSONResponse(status_code=code, content=jsonable_encoder(content))