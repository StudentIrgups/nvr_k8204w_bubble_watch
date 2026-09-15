#!/usr/bin/env python3
import socket, sys, select, time

HOST = '192.168.2.177'
PORT = 80
CH = int(sys.argv[1]) if len(sys.argv) > 1 else 0

PKT1 = bytes.fromhex(
    "aa00000035000004813f0000002c0000000061646d696e"
    "000000000000000000000000000000000000000000000000"
    "0000000000000000000000"
)

PKT2 = bytes.fromhex("aa0000000d00000483610000000401000000")

PKT3_CH0 = bytes.fromhex("aa000000150a00048d6f00000000010000000100000000000000")

# === ПОДКЛЮЧЕНИЕ С TCP_NODELAY ===
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)  # ← ОТКЛЮЧАЕМ NAGLE
s.connect((HOST, PORT))
print(f"[+] Connected", file=sys.stderr)

# Шаг 1: GET
s.sendall(f"GET /bubble/live?ch={CH}&stream=0 HTTP/1.1\r\n\r\n".encode())
print(f"[+] Sent GET", file=sys.stderr)

# Шаг 2: PKT1, PKT2, PKT3 — с БОЛЬШИМИ паузами
time.sleep(1.0)
s.sendall(PKT1)
print(f"[+] Sent PKT1 ({len(PKT1)} bytes)", file=sys.stderr)

time.sleep(1.0)
s.sendall(PKT2)
print(f"[+] Sent PKT2 ({len(PKT2)} bytes)", file=sys.stderr)

time.sleep(1.0)
s.sendall(PKT3_CH0)
print(f"[+] Sent PKT3 ({len(PKT3_CH0)} bytes)", file=sys.stderr)

# Шаг 3: Читаем поток
in_header = True
buf = b''
total = 0
start_time = time.time()

while True:
    ready, _, _ = select.select([s], [], [], 30)
    if not ready:
        print(f"[-] Timeout. Total: {total}", file=sys.stderr)
        break

    try:
        chunk = s.recv(65536)
    except Exception as e:
        print(f"[-] Error: {e}", file=sys.stderr)
        break

    if not chunk:
        print(f"[-] Closed. Total: {total}", file=sys.stderr)
        break

    elapsed = time.time() - start_time
    print(f"[{elapsed:.1f}s] Recv {len(chunk)} bytes", file=sys.stderr)

    if in_header:
        buf += chunk
        if b'####' in buf:
            idx = buf.find(b'####')
            end = idx
            while end < len(buf) and buf[end:end+1] == b'#':
                end += 1
            while end < len(buf) and buf[end:end+1] in (b'\r', b'\n'):
                end += 1

            data = buf[end:]
            if data:
                sys.stdout.buffer.write(data)
                sys.stdout.buffer.flush()
                total += len(data)
                print(f"[+] #### found, wrote {len(data)} bytes", file=sys.stderr)

            in_header = False
            buf = b''
    else:
        sys.stdout.buffer.write(chunk)
        sys.stdout.buffer.flush()
        total += len(chunk)

s.close()
print(f"[+] Done. Total: {total}", file=sys.stderr)
