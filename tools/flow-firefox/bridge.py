#!/usr/bin/env python3
"""Cola privada en loopback. Sin acceso al perfil ni ejecución de código remoto."""
import hmac
import json
import os
from pathlib import Path
import secrets
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

STATE = Path.home() / '.local/share/master-series-flow-firefox'
STATE.mkdir(parents=True, exist_ok=True, mode=0o700)
STATE.chmod(0o700)
os.umask(0o077)
KEY = STATE / 'clave.txt'
if not KEY.exists():
    KEY.write_text(secrets.token_hex(32) + '\n')
KEY.chmod(0o600)
TOKEN = KEY.read_text().strip()
lock = threading.Lock()
jobs = {}
last_seen = 0

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_):
        pass

    def reply(self, status, value):
        data = json.dumps(value).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def handle_request(self):
        global last_seen
        if not hmac.compare_digest(self.headers.get('Authorization', ''), 'Bearer ' + TOKEN):
            return self.reply(401, {'error':'No autorizado'})
        origin = self.headers.get('Origin', '')
        if origin and not origin.startswith('moz-extension://'):
            return self.reply(403, {'error':'Origen no permitido'})
        data = {}
        if self.command == 'POST':
            try:
                size = int(self.headers.get('Content-Length', 0))
                if not 0 < size <= 20_000_000:
                    return self.reply(413, {'error':'Tamaño no permitido'})
                data = json.loads(self.rfile.read(size))
                if not isinstance(data, dict):
                    raise ValueError()
            except (ValueError, json.JSONDecodeError):
                return self.reply(400, {'error':'JSON inválido'})
        with lock:
            now = time.monotonic()
            for ident in list(jobs):
                if now - jobs[ident]['created'] > 300:
                    del jobs[ident]
            if self.command == 'GET' and self.path == '/status':
                return self.reply(200, {'connected':now-last_seen < 5, 'jobs':len(jobs)})
            if self.command == 'GET' and self.path == '/next':
                last_seen = now
                for ident, job in jobs.items():
                    if job['state'] == 'queued':
                        if now-job['created'] > 15:
                            job.update(state='done', result={'error':'Orden caducada; no ejecutada'})
                            continue
                        job['state'] = 'delivered'
                        return self.reply(200, {'id':ident, 'command':job['command']})
                return self.reply(200, {})
            if self.command == 'POST' and self.path == '/command':
                if now-last_seen >= 5:
                    return self.reply(409, {'error':'Firefox no está conectado'})
                if data.get('op') not in ('snapshot','click','fill','upload','screenshot'):
                    return self.reply(400, {'error':'Acción no permitida'})
                if any(j['state'] != 'done' for j in jobs.values()):
                    return self.reply(409, {'error':'Hay una orden pendiente; no reintentar automáticamente'})
                ident = secrets.token_hex(12)
                jobs[ident] = {'created':now,'command':data,'state':'queued'}
                return self.reply(200, {'id':ident})
            if self.command == 'POST' and self.path == '/result':
                job = jobs.get(data.get('id'))
                if not job or job['state'] != 'delivered':
                    return self.reply(409, {'error':'Orden no pendiente'})
                job.update(state='done',result=data.get('result'))
                return self.reply(200, {'ok':True})
            if self.command == 'GET' and self.path.startswith('/result/'):
                job = jobs.get(self.path.split('/')[-1])
                return self.reply(200 if job else 404, {'state':job['state'], 'result':job.get('result')} if job else {})
        return self.reply(404, {'error':'Ruta desconocida'})

    def do_GET(self):
        self.handle_request()

    def do_POST(self):
        self.handle_request()

if __name__ == '__main__':
    print('Puente privado: 127.0.0.1:8765. Clave en ' + str(KEY), flush=True)
    ThreadingHTTPServer(('127.0.0.1', 8765), Handler).serve_forever()
