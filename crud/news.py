# 数据库增删改查
from sqlalchemy.ext.asyncio import AsyncSession
from models.news import Category, News
from sqlalchemy import func, select
async def get_categories(db:AsyncSession,skip:int=0,limit:int=100):
    #获取数据库里面的新闻分类
    stmt=select(Category).offset(skip).limit(limit)
    result=await db.execute(stmt)
    return result.scalars().all()

async def get_news_list(db:AsyncSession,category_id:int,skip:int=0,limit:int=10):
    # 查询指定分类下的新闻
    stmt=select(News).where(News.category_id==category_id).offset(skip).limit(limit)
    result=await db.execute(stmt)
    return result.scalars().all()


async def get_news_count(db: AsyncSession, category_id: int):
    # 查询的是指定分类下的新闻数量
    # func 是 SQLAlchemy 的SQL 函数调用入口——你可以用它生成任意数据库内置函数
    # （COUNT、SUM、MAX、NOW、CONCAT 等），不用手写 SQL。
    stmt = select(func.count(News.id)).where(News.category_id == category_id)
    result = await db.execute(stmt)
    return result.scalar_one()  # 只能有一个结果，否则报错 
    #然后去路由里调用
