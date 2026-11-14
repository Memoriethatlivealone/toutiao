"""收藏 / 浏览历史的请求模型。

两个模块的请求体结构一样，都是只带一个新闻 id，所以共用一个模型。
前端传的是 camelCase（newsId），后端字段用 snake_case（news_id），
通过 alias 完成映射。
"""

from pydantic import BaseModel, ConfigDict, Field


class NewsIdRequest(BaseModel):
    """收藏 / 历史操作请求体：只包含新闻ID。"""

    news_id: int = Field(..., alias="newsId", gt=0, description="新闻ID，必须大于0")

    model_config = ConfigDict(
        populate_by_name=True,  # alias 和字段名都能用来传参
    )