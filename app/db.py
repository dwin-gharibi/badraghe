import aiomysql
from app.config import settings

pool = None

async def connect_db():
    global pool
    pool = await aiomysql.create_pool(
        host=settings.mysql_host,
        port=settings.mysql_port,
        user=settings.mysql_user,
        password=settings.mysql_password,
        db=settings.mysql_db,
        autocommit=True,
    )

async def close_db():
    global pool
    if pool:
        pool.close()
        await pool.wait_closed()

async def execute_query(query: str, params: tuple = (), fetch_one=False, fetch_all=False, return_lastrowid=False):
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(query, params)
            if return_lastrowid:
                await conn.commit()
                return cur.lastrowid
            if fetch_one:
                return await cur.fetchone()
            if fetch_all:
                return await cur.fetchall()
            await conn.commit()

