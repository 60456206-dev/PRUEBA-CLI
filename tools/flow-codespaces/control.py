#!/usr/bin/env python3
"""Ejecuta una acción Playwright local leída por stdin; no imprime cookies."""
import json,socket,sys
from pathlib import Path
with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as s:
    s.settimeout(55)
    s.connect(str(Path.home()/'.local/share/master-series-flow-codespaces/control.sock'))
    s.sendall((json.dumps({'code':sys.stdin.read()})+'\n').encode())
    response=b''
    while b'\n' not in response:
        part=s.recv(65536)
        if not part:break
        response+=part
    print(response.decode())
