# 数据库增删改查
from sqlalchemy.ext.asyncio import AsyncSession
from models.news import Category, News
from sqlalchemy import func, select, update
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
    # 然后去路由里调用


async def get_news_detail(db: AsyncSession, news_id: int):
    stmt = select(News).where(News.id == news_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def increase_news_views(db: AsyncSession, news_id: int):
    # 把浏览量 +1，SQL 是：UPDATE news SET views = views + 1 WHERE id = ?
    # 为什么要在数据库里 +1，而不是先查出来再 Python 里 +1 存回去？
    # 因为「查 → 改 → 存」在并发下会互相覆盖：两个请求同时读到 100，各自写回 101，实际涨了 2 次却只 +1
    # 写成 views = views + 1，加一在数据库里一步完成，不会丢更新
    stmt = update(News).where(News.id == news_id).values(views=News.views + 1)
    result = await db.execute(stmt)
    # 手动提交，让浏览量立刻落库；get_db 在请求结束时还会再 commit 一次
    # 重复 commit 没有副作用（没有未提交的改动时它就是空操作）
    await db.commit()
    # 更新 → 检查数据库是否真的命中了数据 → 命中了返回True
    # rowcount 是本次 UPDATE 实际影响的行数：0 表示库里没有这个 id
    return result.rowcount > 0


async def get_related_news(
    db: AsyncSession, news_id: int, category_id: int, limit: int = 5):
    #获取同类推荐新闻news
    stmt = (
        select(News)
        .where(News.category_id == category_id, News.id != news_id)
        .order_by(
            News.views.desc(), News.publish_time.desc()  # order_by排序，默认是升序，desc表示降序按浏览量推荐给前端
        )#浏览量最高 发布时间最新
        .limit(limit)  # 只取前 limit 条，避免相关新闻一次返回太多
    )
    result = await db.execute(stmt)
    # scalars()：从「行」里取出 ORM 对象本身；all()：把所有结果收成列表
    # 上面两行也可以一行写完：result.scalars().all()
    related_news = result.scalars().all()#执行它
    # 列表推导式 推导出新闻的核心数据，然后再 return
    # 为什么不直接 return related_news？因为那是 ORM 对象，不能直接放进 FastAPI 的响应里，
    # 要转成纯 dict；顺便把字段名改成前端习惯的驼峰命名（publishTime、categoryId）
    # 注意：这里每一条都带上了 content（正文全文），数据量偏大，
    # 相关新闻一般只给前端渲染标题和封面，可以按需删掉 content 这一项
    return [
        {
            "id": news_detail.id,
            "title": news_detail.title,
            "content": news_detail.content,
            "image": news_detail.image,
            "author": news_detail.author,
            "publishTime": news_detail.publish_time,
            "categoryId": news_detail.category_id,
            "views": news_detail.views,
        }
        for news_detail in related_news
    ]
