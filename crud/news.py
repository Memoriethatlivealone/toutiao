#数据库增删改查
from sqlalchemy.ext.asyncio import AsyncSession
from models.news import Category
from sqlalchemy import select
async def get_categories(db:AsyncSession,skip:int=0,limit:int=100):
    #获取数据库里面的新闻分类
    stmt=select(Category).offset(skip).limit(limit)
    result=await db.execute(stmt)
    return result.scalars().all()

#1模块化路由➡️API文档