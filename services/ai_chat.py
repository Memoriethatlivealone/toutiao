"""AI 问答服务。

基于 LangChain agent + OpenAI 兼容接口（阿里云 MaaS），
给 agent 配备新闻查询工具，让它能回答“今天有什么体育新闻”这类问题。
"""

import json
import os
from collections.abc import AsyncIterator
from pathlib import Path

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from sqlalchemy import select

from config.db_config import AsyncSessionLocal
from crud import news as news_crud
from models.news import Category, News

# 和 db_config/cache 一样，从项目根目录 .env 读取 AI 配置
ENV_FILE = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(ENV_FILE)

AI_API_KEY = os.getenv("AI_API_KEY", "")
AI_BASE_URL = os.getenv(
    "AI_BASE_URL", "https://maas.qianwenaiapi.com/compatible-mode/v1"
)
AI_MODEL = os.getenv("AI_MODEL", "deepseek-v4.1-flash")


def _news_to_dict(item: News, include_content: bool = False) -> dict:
    """把新闻 ORM 对象转成 agent 容易理解的 dict。"""
    data = {
        "id": item.id,
        "title": item.title,
        "description": item.description,
        "author": item.author,
        "publishTime": item.publish_time.isoformat() if item.publish_time else None,
        "views": item.views,
        "categoryId": item.category_id,
    }
    if include_content:
        # 正文可能很长，截断避免占满上下文
        data["content"] = (item.content or "")[:800]
    return data


@tool
async def get_categories() -> str:
    """获取所有新闻分类，返回每个分类的 id 和名称。

    当用户提到某个频道（如头条、体育、科技）时，先调用这个工具找到对应的 category_id。
    """
    async with AsyncSessionLocal() as db:
        categories = await news_crud.get_categories(db, 0, 100)
        data = [
            {"id": c.id, "name": c.name, "sortOrder": c.sort_order}
            for c in categories
        ]
    return json.dumps(data, ensure_ascii=False)


@tool
async def get_news_list(category_id: int, page: int = 1, page_size: int = 5) -> str:
    """按分类分页查询新闻列表。

    Args:
        category_id: 分类 id，先用 get_categories 获取
        page: 页码，从 1 开始
        page_size: 每页条数，建议 5
    """
    page = max(1, page)
    page_size = min(max(1, page_size), 10)
    offset = (page - 1) * page_size
    async with AsyncSessionLocal() as db:
        items = await news_crud.get_news_list(db, category_id, offset, page_size)
        total = await news_crud.get_news_count(db, category_id)
    return json.dumps(
        {
            "total": total,
            "page": page,
            "list": [_news_to_dict(item) for item in items],
        },
        ensure_ascii=False,
    )


@tool
async def get_news_detail(news_id: int) -> str:
    """根据新闻 id 获取详情，包括标题、作者、发布时间和正文摘要。"""
    async with AsyncSessionLocal() as db:
        item = await news_crud.get_news_detail(db, news_id)
    if item is None:
        return json.dumps({"error": f"没有找到 id 为 {news_id} 的新闻"})
    return json.dumps(_news_to_dict(item, include_content=True), ensure_ascii=False)


@tool
async def search_news(keyword: str, limit: int = 5) -> str:
    """按关键词模糊搜索新闻标题，返回匹配的新闻列表。"""
    keyword = keyword.strip()
    if not keyword:
        return json.dumps({"error": "关键词不能为空"})
    limit = min(max(1, limit), 10)
    async with AsyncSessionLocal() as db:
        stmt = (
            select(News)
            .where(News.title.contains(keyword))
            .order_by(News.publish_time.desc())
            .limit(limit)
        )
        result = await db.execute(stmt)
        items = result.scalars().all()
    return json.dumps(
        {"keyword": keyword, "list": [_news_to_dict(item) for item in items]},
        ensure_ascii=False,
    )


SYSTEM_PROMPT = """你是「新闻资讯」网站的 AI 助手，负责回答用户关于新闻内容的问题。

工作方式：
1. 用户问某个频道（头条、体育、科技等）的新闻时，先调用 get_categories 找到分类 id，
   再调用 get_news_list 获取新闻列表。
2. 用户问具体某条新闻的细节时，先拿到新闻 id，再调用 get_news_detail。
3. 用户给出关键词时，可以用 search_news 搜索标题。
4. 新闻内容必须以工具返回的数据为准，不要编造不存在的新闻。
5. 引用新闻时给出标题和 id，方便用户查看详情。
6. 与新闻无关的问题也可以正常回答。用中文回答，简洁清晰。
"""

_agent = None


def get_agent():
    """懒加载 agent：第一次调用时创建，之后复用。"""
    global _agent
    if _agent is None:
        if not AI_API_KEY:
            raise RuntimeError("AI_API_KEY 未配置，请在 .env 中填写")
        llm = ChatOpenAI(
            model=AI_MODEL,
            api_key=AI_API_KEY,
            base_url=AI_BASE_URL,
            temperature=0.3,
            streaming=True,
            timeout=60,
            max_retries=2,
        )
        _agent = create_agent(
            model=llm,
            tools=[get_categories, get_news_list, get_news_detail, search_news],
            system_prompt=SYSTEM_PROMPT,
        )
    return _agent


async def stream_chat(messages: list[dict]) -> AsyncIterator[str]:
    """把对话交给 agent 处理，逐个产出模型生成的文本片段。"""
    agent = get_agent()
    async for event in agent.astream_events({"messages": messages}, version="v2"):
        if event.get("event") != "on_chat_model_stream":
            continue
        chunk = event.get("data", {}).get("chunk")
        content = getattr(chunk, "content", None)
        if not content:
            continue
        if isinstance(content, list):
            # 少数模型会返回内容块列表
            text = "".join(
                block.get("text", "") if isinstance(block, dict) else getattr(block, "text", "")
                for block in content
            )
        else:
            text = content
        if text:
            yield text