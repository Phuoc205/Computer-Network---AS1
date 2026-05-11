# Concurrent Backend Test

Start one app server:

```powershell
python start_peer.py --username alice --peer-ip 127.0.0.1 --peer-port 9001 --tracker-ip 127.0.0.1 --tracker-port 8000
```

Run many curl requests in parallel:

```powershell
1..20 | ForEach-Object {
    Start-Job { curl.exe --max-time 5 -s http://127.0.0.1:9001/channels }
}
Get-Job | Wait-Job | Receive-Job
Get-Job | Remove-Job
```

Python concurrent request script:

```powershell
@'
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.request import urlopen

def fetch(i):
    with urlopen("http://127.0.0.1:9001/channels", timeout=5) as response:
        return i, response.status, response.read().decode()

with ThreadPoolExecutor(max_workers=20) as pool:
    futures = [pool.submit(fetch, i) for i in range(20)]
    for future in as_completed(futures):
        print(future.result())
'@ | python -
```

Expected server log:

```text
[Backend] Accepted connection from (...); starting worker thread
[Backend] Thread Thread-N handling connection from (...)
```
