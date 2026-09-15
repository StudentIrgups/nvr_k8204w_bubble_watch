#!/usr/bin/env python3
import socket, sys, select, time

HOST = '192.168.2.177'
PORT = 80
CH = int(sys.argv[1]) if len(sys.argv) > 1 else 0
STREAM = int(sys.argv[2]) if len(sys.argv) > 2 else 0

PKT1 = bytes.fromhex(
    "aa00000035000004813f0000002c0000000061646d696e"
    "000000000000000000000000000000000000000000000000"
    "0000000000000000000000"
)
PKT2 = bytes.fromhex("aa0000000d00000483610000000401000000")

# PKT3 — для stream=0 и stream=1 может отличаться.
# Из pcap IE: только stream=0. Для stream=1 — используем тот же.
PKT3_BY_CH = {
    0: bytes.fromhex("aa000000150a00048d6f00000000010000000100000000000000"),
    1: bytes.fromhex("aa000000150a00048d6f01000000010000000100000000000000"),
    2: bytes.fromhex("aa000000150a00048d6f02000000010000000100000000000000"),
    3: bytes.fromhex("aa000000150a00048d6f03000000010000000100000000000000"),
}
PKT3 = PKT3_BY_CH[CH]

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
s.connect((HOST, PORT))

s.sendall(f"GET /bubble/live?ch={CH}&stream={STREAM} HTTP/1.1\r\n\r\n".encode())
print(f"[+] GET ch={CH} stream={STREAM}", file=sys.stderr)

time.sleep(1.0)
s.sendall(PKT1)
time.sleep(1.0)
s.sendall(PKT2)
time.sleep(1.0)
s.sendall(PKT3)

in_header = True
buf = b''
total = 0
sps_found = False

while True:
    ready, _, _ = select.select([s], [], [], 30)
    if not ready:
        break
    try:
        chunk = s.recv(65536)
    except:
        break
    if not chunk:
        break

    if in_header:
        buf += chunk
        if b'####' in buf:
            idx = buf.find(b'####')
            end = idx
            while end < len(buf) and buf[end:end+1] == b'#':
                end += 1
            while end < len(buf) and buf[end:end+1] in (b'\r', b'\n'):
                end += 1
            buf = buf[end:]
            in_header = False
        continue

    # Ищем SPS H.264 (00 00 00 01 27) или VPS H.265 (00 00 00 01 40)
    if not sps_found:
        buf += chunk
        sps_h264 = buf.find(b'\x00\x00\x00\x01\x27')
        sps_h265 = buf.find(b'\x00\x00\x00\x01\x40')
        
        sps = -1
        if sps_h264 >= 0 and sps_h265 >= 0:
            sps = min(sps_h264, sps_h265)
        elif sps_h264 >= 0:
            sps = sps_h264
        elif sps_h265 >= 0:
            sps = sps_h265
        
        if sps >= 0:
            data = buf[sps:]
            sys.stdout.buffer.write(data)
            sys.stdout.buffer.flush()
            total += len(data)
            sps_found = True
            buf = b''
    else:
        sys.stdout.buffer.write(chunk)
        sys.stdout.buffer.flush()
        total += len(chunk)

s.close()
print(f"[+] Done. Total: {total}", file=sys.stderr)
