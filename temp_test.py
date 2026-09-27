import json, urllib.request, sys
url='http://localhost:8000/api/v1/analyze'
payload=json.dumps({"repo_url":"https://github.com/tiangolo/fastapi"}).encode()
req=urllib.request.Request(url, data=payload, headers={'Content-Type':'application/json'}, method='POST')
with urllib.request.urlopen(req) as resp:
    print('status', resp.status)
    data=resp.read().decode()
    print('body', data[:300])
