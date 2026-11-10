# 启动命令：uv run uvicorn main:app --reload
# FastAPI：Web 框架，负责创建应用、路由和自动生成接口文档
from fastapi import FastAPI
# 导入新闻模块的路由文件（routers/news.py）
from routers import news
from fastapi.middleware.cors import CORSMiddleware
# 创建 FastAPI 应用实例，main:app 中的 app 就是它
app = FastAPI()

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