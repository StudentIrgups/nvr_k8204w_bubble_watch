#!/usr/bin/env python3
import socket, sys, time

HOST_NVR = '192.168.2.177'
PORT_NVR = 80
LISTEN_PORT = int(sys.argv[1])
CH = int(sys.argv[2])
STREAM = int(sys.argv[3]) if len(sys.argv) > 3 else 1

PKT1 = bytes.fromhex(
    "aa00000035000004813f0000002c0000000061646d696e"
    "000000000000000000000000000000000000000000000000"
    "0000000000000000000000"
)
PKT2 = bytes.fromhex("aa0000000d00000483610000000401000000")
PKT3_BY_CH = {
    0: bytes.fromhex("aa000000150a00048d6f00000000010000000100000000000000"),
    1: bytes.fromhex("aa000000150a00048d6f01000000010000000100000000000000"),
    2: bytes.fromhex("aa000000150a00048d6f02000000010000000100000000000000"),
    3: bytes.fromhex("aa000000150a00048d6f03000000010000000100000000000000"),
}

def handle(conn):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    s.connect((HOST_NVR, PORT_NVR))
    s.sendall(f"GET /bubble/live?ch={CH}&stream={STREAM} HTTP/1.1\r\n\r\n".encode())
    time.sleep(1.0)
    s.sendall(PKT1)
    time.sleep(1.0)
    s.sendall(PKT2)
    time.sleep(1.0)
    s.sendall(PKT3_BY_CH[CH])

    in_header = True
    buf = b''
    sps_found = False
    while True:
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
        if not sps_found:
            buf += chunk
            sps = buf.find(b'\x00\x00\x00\x01\x27')
            if sps >= 0:
                conn.sendall(buf[sps:])
                sps_found = True
                buf = b''
        else:
            conn.sendall(chunk)

srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
srv.bind(('127.0.0.1', LISTEN_PORT))
srv.listen(1)
print(f"[+] Listening on {LISTEN_PORT} ch={CH} stream={STREAM}", file=sys.stderr)

while True:
    conn, addr = srv.accept()
    print(f"[+] Client connected", file=sys.stderr)
    try:
        handle(conn)
    except Exception as e:
        print(f"[-] {e}", file=sys.stderr)
    finally:
        conn.close()
