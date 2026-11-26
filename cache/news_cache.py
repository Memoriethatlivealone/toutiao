# 新闻相关的缓存方法：新闻分类的读取和写入
from typing import Any, Dict, List

from config.cache import get_json_cache, set_cache

# Redis 里的缓存键
CATEGORIES_KEY = "news:categories"


# 获取新闻分类缓存；没有缓存（或已过期）时返回 None
async def get_cached_categories():
    return await get_json_cache(CATEGORIES_KEY)


# 写入新闻分类缓存的方法：缓存的数据、过期的时间
# 分类配置 7200；列表 600；详情 1800；验证码 120
async def set_cache_categories(data: List[Dict[str, Any]], expire: int = 7200):
    return await set_cache(CATEGORIES_KEY, data, expire)