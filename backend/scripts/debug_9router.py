import asyncio, os, httpx

async def main():
    base_url = os.environ.get("AI_BASE_URL", "http://localhost:20128/v1").rstrip("/")
    api_key = os.environ.get("AI_API_KEY")
    model = os.environ.get("AI_MODEL", "groq/openai/gpt-oss-120b")

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "RepoLens/0.1",
    }
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "Return only JSON."},
            {"role": "user", "content": 'Reply only with: {"status":"ok"}'}
        ],
        "stream": False,
        "temperature": 0.2,
    }

    async with httpx.AsyncClient(base_url=base_url, timeout=30.0, headers=headers,
                                 follow_redirects=True) as client:
        resp = await client.post("/chat/completions", json=payload)
        print(f"STATUS_CODE: {resp.status_code}")
        print(f"CONTENT_TYPE: {resp.headers.get('content-type')}")
        print(f"CONTENT_LENGTH: {resp.headers.get('content-length')}")
        body = resp.text
        print(f"BODY_LENGTH: {len(body)}")
        print(f"BODY_PREVIEW (first 800 chars):")
        print(body[:800])

asyncio.run(main())
