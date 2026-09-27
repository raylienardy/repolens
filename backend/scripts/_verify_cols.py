import asyncio
import asyncpg

async def m():
    c = await asyncpg.connect('postgresql://repolens:repolens@localhost:5433/repolens')
    r = await c.fetch("SELECT column_name, data_type FROM information_schema.columns WHERE table_name='repository_analysis' ORDER BY ordinal_position")
    for x in r:
        print(dict(x))
    await c.close()

asyncio.run(m())
