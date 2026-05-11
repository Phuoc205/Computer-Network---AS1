# Hybrid Chat App

Hybrid Chat App la mot ung dung chat demo chay tren HTTP server tu xay dung trong project. He thong dung Tracker server de dang ky va tim peer dang online, nhung message chat that su duoc gui truc tiep giua cac Peer server.

## Kien Truc

### Tracker Server

Tracker server chay mac dinh tai `127.0.0.1:8000`.

Nhiem vu:

- Luu danh sach peer online trong memory.
- Cho peer dang ky thong tin qua `/login` hoac `/submit-info`.
- Cung cap danh sach peer qua `/get-list`.
- Khong luu message chat.
- Khong forward message chat.

### Peer Server

Moi user la mot HTTP server rieng chay tren port rieng.

Vi du:

- Alice: `127.0.0.1:9001`
- Bob: `127.0.0.1:9002`

Moi peer luu local:

- `username`
- `channels`
- `messages`
- `notifications`
- `known_peers`

### Peer-to-Peer Direct Message

Khi Alice gui direct message cho Bob:

1. Alice goi tracker `/get-list`.
2. Alice tim peer co username `bob`.
3. Alice gui HTTP POST truc tiep toi `http://bob_ip:bob_port/send-peer`.
4. Bob luu message voi `direction = "incoming"`.
5. Alice luu message voi `direction = "outgoing"`.

Tracker chi duoc dung de discovery, khong truyen message chat.

### Broadcast Message

Khi Alice broadcast:

1. Alice goi tracker `/get-list`.
2. Alice lay tat ca peer khac, bo qua chinh Alice.
3. Alice gui POST `/send-peer` truc tiep toi tung peer.
4. Message co `type = "broadcast"`.
5. Neu mot peer fail, broadcast van tiep tuc voi cac peer con lai.

### Channel

Moi peer co danh sach channel local, mac dinh co:

```json
["general"]
```

Peer co the join channel moi qua `/join-channel`. Khi gui hoac nhan message tren channel chua co, peer tu them channel do vao local list.

Co the loc message theo channel:

```text
GET /messages?channel=general
```

### Notification

Khi peer nhan message qua `/send-peer`, peer tao notification local:

```json
{
  "type": "new_message",
  "from": "alice",
  "channel": "general",
  "message": "Hello",
  "timestamp": "..."
}
```

Notification duoc xem qua `/notifications` va xoa qua `/notifications/clear`.

## Chay Demo Bang 3 Terminal

Terminal 1: chay tracker.

```powershell
python start_tracker.py --server-ip 127.0.0.1 --server-port 8000
```

Terminal 2: chay Alice.

```powershell
python start_peer.py --username alice --peer-ip 127.0.0.1 --peer-port 9001 --tracker-ip 127.0.0.1 --tracker-port 8000
```

Terminal 3: chay Bob.

```powershell
python start_peer.py --username bob --peer-ip 127.0.0.1 --peer-port 9002 --tracker-ip 127.0.0.1 --tracker-port 8000
```

Khi peer start, peer tu dong dang ky len tracker bang API `/submit-info`.

## Curl Test

## Web Chat UI

Sau khi chay tracker va cac peer, mo UI tren tung peer:

```text
http://127.0.0.1:9001/chat.html
http://127.0.0.1:9002/chat.html
```

UI co cac phan co ban theo yeu cau de bai:

- Danh sach channel va nut join channel.
- Khung message co scroll theo channel hien tai.
- O nhap username dich, o nhap message, nut Send va Broadcast.
- Danh sach peer online lay qua tracker.
- Khu vuc notification va nut clear notification.

UI dung Basic Auth mac dinh `admin:password` khi goi API cua peer.

### Register Peer

Peer da tu register khi start. Neu muon test tracker thu cong:

```powershell
Set-Content .\alice.json '{"username":"alice","ip":"127.0.0.1","port":9001,"channels":["general"]}' -NoNewline
curl -i -X POST http://127.0.0.1:8000/submit-info -H "Content-Type: application/json" --data-binary "@alice.json"
```

### Get Peer List

```powershell
curl -i http://127.0.0.1:8000/get-list
```

### Direct Message

Goi API tren Alice de gui truc tiep toi Bob:

```powershell
Set-Content .\direct-message.json '{"to":"bob","channel":"general","message":"Hello Bob"}' -NoNewline
curl -i -u admin:password -X POST http://127.0.0.1:9001/direct-message -H "Content-Type: application/json" --data-binary "@direct-message.json"
```

### Broadcast

Goi API tren Alice de broadcast toi cac peer khac:

```powershell
Set-Content .\broadcast.json '{"channel":"general","message":"Hello everyone"}' -NoNewline
curl -i -u admin:password -X POST http://127.0.0.1:9001/broadcast-peer -H "Content-Type: application/json" --data-binary "@broadcast.json"
```

### Get Messages

Lay tat ca message cua Bob:

```powershell
curl -i -u admin:password http://127.0.0.1:9002/messages
```

Loc message cua Bob theo channel:

```powershell
curl -i -u admin:password "http://127.0.0.1:9002/messages?channel=general"
```

### Get Notifications

```powershell
curl -i -u admin:password http://127.0.0.1:9002/notifications
```

Xoa notifications:

```powershell
curl -i -u admin:password -X POST http://127.0.0.1:9002/notifications/clear
```

## Phan Client-Server

Phan Client-Server nam o quan he giua Peer va Tracker:

- Peer la client khi goi tracker `/submit-info`.
- Peer la client khi goi tracker `/get-list`.
- Tracker la server trung tam de luu danh sach peer online.

Tracker cung cap discovery service, giong mot directory server.

## Phan Peer-to-Peer

Phan Peer-to-Peer nam o viec gui message giua cac Peer server:

- Alice goi truc tiep Bob `/send-peer`.
- Alice broadcast bang cach goi truc tiep tung peer `/send-peer`.
- Message chat khong di qua tracker.

Moi peer vua la server, vua la client:

- Server khi nhan `/send-peer`.
- Client khi gui request toi peer khac.

## Security / Auth

Peer server hien co Basic Auth demo cho cac API thao tac chat. Mac dinh:

```text
username: admin
password: password
```

Co the doi credential khi chay peer:

```powershell
python start_peer.py --username alice --peer-ip 127.0.0.1 --peer-port 9001 --tracker-ip 127.0.0.1 --tracker-port 8000 --auth-user admin --auth-password password
```

Hoac dung bien moi truong:

```powershell
$env:CHAT_AUTH_USER="admin"
$env:CHAT_AUTH_PASSWORD="password"
```

Neu doi credential, nen dung cung credential cho cac peer trong demo de peer co the gui message truc tiep qua endpoint `/send-peer`.

Nhung endpoint can auth:

- `/send-peer`
- `/direct-message`
- `/broadcast-peer`
- `/connect-peer`
- `/messages`
- `/channels`
- `/notifications`
- `/notifications/clear`
- `/join-channel`

Khi Basic Auth dung, server tao session cookie `ASYNAPROUS_SESSION` de cac request sau co the dung cookie thay vi gui lai username/password.
Web UI se hoi username/password khi mo `chat.html`, khong con gan san password trong ma JavaScript.

## Vi Sao Tracker Khong Truyen Message Chat

Tracker chi lam nhiem vu dang ky va discovery:

- Giam tai cho server trung tam.
- Giu dung tinh chat hybrid: tracker la Client-Server, chat la Peer-to-Peer.
- Peer co the gui message truc tiep den nhau sau khi biet IP va port.
- Tracker khong can luu noi dung chat, nen don gian hon va it phu thuoc hon.

## Non-Blocking / Concurrent Handling

Backend server hien tai dung multi-threading toi thieu:

- Main server thread chay loop `accept()`.
- Moi connection moi duoc xu ly trong mot thread rieng.
- Thread goi `handle_client(...)` hien co.
- Neu mot client bi loi, exception duoc bat trong thread va server chinh khong crash.
- Cach nay giup server tiep tuc nhan request moi khi mot client dang duoc xu ly.

Day la co che concurrent toi thieu de demo chac chan. Callback/coroutine chua can hoan thien trong phase nay.

## Test Flow Tu Dong

Sau khi tracker, Alice, Bob da chay, co the dung script:

```powershell
python scripts\test_chat_flow.py
```

Script se test:

- Tracker `/get-list`
- Alice direct message toi Bob
- Bob `/messages`
- Alice broadcast
- Bob `/messages`
- Bob `/notifications`

## Gioi Han Hien Tai

- Du lieu luu trong memory.
- Restart server la mat du lieu.
- Chua co database.
- Chua co UI dep.
- Chua co encryption.
- Chua co authentication/authorization that su.
- Chua co retry nang cao khi peer offline.
- Chua co delivery receipt/read receipt.
