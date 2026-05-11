# Manual curl tests

Start the sample app:

```powershell
python start_sampleapp.py --server-ip 127.0.0.1 --server-port 2026
```

GET route/static fallback:

```powershell
curl -i http://127.0.0.1:2026/index.html
```

POST route with JSON body:

```powershell
Set-Content -Path .\curl-body.json -Value '{"msg":"hello"}' -NoNewline
curl -i -X POST http://127.0.0.1:2026/echo -H "Content-Type: application/json" --data-binary "@curl-body.json"
Remove-Item .\curl-body.json
```

Route not found:

```powershell
curl -i http://127.0.0.1:2026/missing
```

Expected results:

- `GET /index.html` returns `HTTP/1.1 200 OK` with HTML content.
- `POST /echo` returns `HTTP/1.1 200 OK` and `Content-Type: application/json; charset=utf-8`.
- `GET /missing` returns `HTTP/1.1 404 Not Found`.
