import json, urllib.request
url='http://localhost:8000/api/v1/analyze'
payload=json.dumps({"repo_url":"https://github.com/tiangolo/fastapi"}).encode()
req=urllib.request.Request(url, data=payload,
    headers={'Content-Type':'application/json'}, method='POST')
with urllib.request.urlopen(req, timeout=120) as resp:
    print('status', resp.status)
    data=resp.read().decode()
    print('body[:300]', data[:300])
