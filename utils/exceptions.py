"""全局异常处理器。

作用：把 FastAPI / Starlette 抛出的各类异常，统一包装成和 success_response
一样的 {"code", "message", "data"} 结构，避免前端遇到两种格式。

覆盖的三类异常：
    1. StarletteHTTPException —— raise HTTPException(...)、404 路由不存在、405 方法不允许
    2. RequestValidationError —— 请求体/查询参数校验失败（FastAPI 默认返回 422）
    3. Exception              —— 兜底，任何未捕获异常统一返回 500

在 main.py 中调用 register_exception_handlers(app) 一次即可生效。
"""

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from utils.response import error_response

# 使用模块级 logger，uvicorn 启动后会按自己的日志配置输出
logger = logging.getLogger(__name__)

# 参数校验失败的业务码，与 FastAPI 默认的 422 保持一致
VALIDATION_ERROR_CODE = 422

# 参数位置的来源前缀，展示给前端时去掉，只保留字段名本身
LOCATION_PREFIXES = ("body", "query", "path", "header", "cookie")


def _format_validation_errors(exc: RequestValidationError) -> list[dict]:
    """把 Pydantic 的原始错误精简成前端友好的列表。

    原始 err["loc"] 形如 ("body", "username")，这里去掉来源前缀，只留 "username"。
    注意只取 field / message / type 三个字段，不把 err["ctx"] 原样返回，
    因为 ctx 里可能包含无法 JSON 序列化的异常对象。
    """
    details: list[dict] = []
    for err in exc.errors():
        loc = err.get("loc", ())
        field = ".".join(
            str(part) for part in loc if part not in LOCATION_PREFIXES
        )
        details.append(
            {
                "field": field or "request",
                "message": err.get("msg", "参数不合法"),
                "type": err.get("type", ""),
            }
        )
    return details


async def http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    """处理业务异常和 Starlette 默认异常。

    raise HTTPException(status_code=400, detail="用户已存在")
    -> {"code": 400, "message": "用户已存在", "data": null}

    detail 除了字符串也可能是 dict/list，统一转成字符串放在 message 里。
    """
    return error_response(code=exc.status_code, message=str(exc.detail))


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """处理请求参数校验失败（422）。

    message 给出可直接展示的中文摘要，data 里放每个字段的具体错误，
    前端可以按 field 定位到具体输入框。
    """
    details = _format_validation_errors(exc)
    summary = "；".join(f"{item['field']} {item['message']}" for item in details)
    message = f"参数校验失败：{summary}" if summary else "参数校验失败"
    return error_response(code=VALIDATION_ERROR_CODE, message=message, data=details)


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """兜底处理未捕获异常，统一返回 500。

    详细堆栈只写入服务端日志，响应里不暴露任何内部信息，
    避免把 SQL、文件路径等敏感内容泄漏给前端。
    """
    logger.exception(
        "未处理的异常: %s %s", request.method, request.url.path, exc_info=exc
    )
    return error_response(code=500, message="服务器内部错误")


def register_exception_handlers(app: FastAPI) -> None:
    """把全部全局异常处理器注册到 app 上，main.py 中调用一次。"""
    # FastAPI 的 HTTPException 继承自 Starlette 的 HTTPException，
    # 注册父类即可同时接管业务异常和 404/405 等框架默认异常
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    # Exception 的处理器由 Starlette 的 ServerErrorMiddleware 调用，必须有
    # 这一条，未捕获异常才不会返回默认的纯文本 "Internal Server Error"
    app.add_exception_handler(Exception, unhandled_exception_handler)