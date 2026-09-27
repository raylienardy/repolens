import asyncio
import httpx

async def main():
    async with httpx.AsyncClient(
        base_url="https://api.github.com",
        headers={
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "RepoLens/0.1",
        },
        timeout=30,
    ) as client:
        resp = await client.get("/repos/tiangolo/fastapi")
        print("STATUS:", resp.status_code)
        print("HEADERS:", dict(resp.headers))
        print("BODY:", resp.text[:600])

asyncio.run(main())
