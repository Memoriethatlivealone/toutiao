# 启动命令：uv run uvicorn main:app --reload # FastAPI：Web 框架，负责创建应用、路由和自动生成接口文档
from pathlib import Path

from fastapi import FastAPI
# 导入新闻模块的路由文件（routers/news.py）
from routers import favorite, history, news, users
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
# 全局异常处理器：让 404、422、500 等错误也返回统一的 {code, message, data}
from utils.exceptions import register_exception_handlers
# 创建 FastAPI 应用实例，main:app 中的 app 就是它
app = FastAPI()

# 静态文件目录：项目根/static，头像等上传文件放在这里
# 挂载后 /static/avatars/xxx.png 就能直接访问，前端拼上 baseURL 即可显示
STATIC_DIR = Path(__file__).resolve().parent / "static"
# 目录不存在时 StaticFiles 会直接启动失败，所以先确保它存在
STATIC_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# 注册全局异常处理器
# 注意：必须在挂载路由之前或之后都可以，只要在应用启动前调用即可；
# 这里紧跟在 app 创建之后，保证所有异常都走统一格式
register_exception_handlers(app)

# CORS（跨域资源共享）中间件
# 浏览器的同源策略默认拦截跨域请求，加上它后端才会返回 CORS 响应头，
# 让前端（如 http://localhost:5173）能正常调用本接口
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # 允许访问的来源；* 表示任意来源（开发用，生产环境应改成具体前端域名）
    allow_credentials=True,   # 允许请求携带 Cookie、Authorization 等凭证
    allow_methods=["*"],      # 允许的 HTTP 方法，如 GET、POST、PUT、DELETE
    allow_headers=["*"],      # 允许的请求头，如 Content-Type、Authorization
)
# 注意：allow_origins=["*"] 搭配 allow_credentials=True 仅适合本地开发，
# 生产环境务必把 allow_origins 收窄为实际域名，否则等于对任何网站开放带凭证的访问

# 注册根路由 GET /
# 访问 http://127.0.0.1:8000/ 时返回 {"Hello": "World"}
@app.get("/")
def read_root():
    return {"Hello": "World"}

# 挂载/注册路由
# 把 news.py 中定义的 router 注册到 app 上，接口路径为 /api/news/...
app.include_router(news.router)
app.include_router(users.router)
# 收藏 / 浏览历史模块，接口路径为 /api/favorite/...、/api/history/...
app.include_router(favorite.router)
app.include_router(history.router)
