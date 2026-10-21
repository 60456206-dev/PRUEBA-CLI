#!/usr/bin/env python3
"""Escritorio de Flow: noVNC local, autenticado y sin puerto CDP."""
import os
from pathlib import Path
import secrets
import signal
import socket
import subprocess
import sys
import time
import urllib.request

BASE = Path(__file__).resolve().parent
STATE = Path.home() / '.local/share/master-series-flow-codespaces'
SCRIPT = str(Path(__file__).resolve())
STATE.mkdir(parents=True, exist_ok=True, mode=0o700)
STATE.chmod(0o700)
os.umask(0o077)
PID = STATE / 'supervisor.pid'

def alive():
    try:
        pid = int(PID.read_text())
        cmd = Path(f'/proc/{pid}/cmdline').read_bytes()
        return pid if SCRIPT.encode() in cmd and b'--serve' in cmd else None
    except (OSError, ValueError):
        return None

def info():
    name = os.environ.get('CODESPACE_NAME')
    domain = os.environ.get('GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN', 'app.github.dev')
    url = f'https://{name}-6080.{domain}' if name else 'http://localhost:6080'
    print(f'Escritorio: {url}/vnc.html?autoconnect=1&resize=scale')
    print('En PUERTOS, reenviar únicamente 6080 y mantener visibilidad PRIVADA.')
    print(f'Para ver tu clave de escritorio: cat {STATE / "clave.txt"}')
    print('La clave de escritorio es distinta de tu contraseña de Google.')

if len(sys.argv) < 2:
    raise SystemExit('Uso: python3 tools/flow-codespaces/escritorio.py iniciar|estado|detener')
action = sys.argv[1]
if action == 'estado':
    print('Activo' if alive() else 'Detenido')
    info()
elif action == 'detener':
    if pid := alive():
        os.kill(pid, signal.SIGTERM)
        print('Cierre solicitado; la sesión de navegador permanece en el perfil privado.')
    else:
        print('Ya está detenido.')
elif action == 'iniciar':
    if not alive():
        # No tomar puertos de otros servicios.
        for port in (6080, 5942):
            with socket.socket() as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind(('127.0.0.1', port))
        with (STATE / 'supervisor.log').open('ab') as log:
            proc = subprocess.Popen([sys.executable, SCRIPT, '--serve'], stdin=subprocess.DEVNULL,
                                    stdout=log, stderr=log, start_new_session=True)
        for _ in range(100):
            if proc.poll() is not None:
                raise SystemExit(f'No arrancó. Consulta {STATE / "supervisor.log"}')
            try:
                with urllib.request.urlopen('http://127.0.0.1:6080/vnc.html', timeout=1) as r:
                    if r.status == 200:
                        time.sleep(2)
                        if proc.poll() is not None:
                            raise SystemExit(f'El navegador falló. Consulta {STATE / "supervisor.log"}')
                        break
            except OSError:
                time.sleep(.2)
        else:
            proc.terminate()
            raise SystemExit('Tiempo de arranque agotado; revisar supervisor.log.')
    info()
elif action == '--serve':
    children = []
    PID.write_text(str(os.getpid()))
    def stop(*_):
        raise KeyboardInterrupt
    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    def launch(args, env=None):
        p = subprocess.Popen(args, env=env, stdin=subprocess.DEVNULL)
        children.append(p)
        return p
    try:
        password = STATE / 'clave.txt'
        if not password.exists():
            password.write_text(secrets.token_urlsafe(6) + '\n')
        result = subprocess.run(['tigervncpasswd', '-f'], input=password.read_bytes(), capture_output=True, check=True)
        (STATE / 'vnc.passwd').write_bytes(result.stdout)
        auth = STATE / 'Xauthority'
        auth.touch(mode=0o600)
        subprocess.run(['xauth', '-f', str(auth), 'add', ':42', '.', secrets.token_hex(16)], check=True)
        env = dict(os.environ, DISPLAY=':42', XAUTHORITY=str(auth))
        launch(['Xtigervnc', ':42', '-geometry', '1366x900', '-depth', '24', '-rfbport', '5942',
                '-localhost', 'yes', '-SecurityTypes', 'VncAuth', '-PasswordFile', str(STATE / 'vnc.passwd'),
                '-auth', str(auth), '-nolisten', 'tcp'], env)
        for _ in range(60):
            if subprocess.run(['xdpyinfo'], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=3).returncode == 0:
                break
            time.sleep(.2)
        else:
            raise RuntimeError('El escritorio no respondió.')
        launch(['openbox'], env)
        profile = STATE / 'browser'
        profile.mkdir(mode=0o700, exist_ok=True)
        if (STATE / 'automation/node_modules/playwright').is_dir():
            launch(['node', str(BASE / 'browser-control.cjs')], env)
        else:
            launch(['chromium', '--user-data-dir=' + str(profile), '--no-first-run', '--no-sandbox', '--disable-dev-shm-usage',
                    '--start-maximized', 'https://labs.google/fx/tools/flow'], env)
        # Solo noVNC se sirve por HTTP; nunca perfiles, contraseñas o archivos del repo.
        launch(['websockify', '--web=/usr/share/novnc', '127.0.0.1:6080', '127.0.0.1:5942'])
        while True:
            if any(p.poll() is not None for p in children):
                raise RuntimeError('Un componente se cerró; escritorio detenido.')
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        for p in reversed(children):
            if p.poll() is None:
                p.terminate()
        for p in reversed(children):
            try:
                p.wait(timeout=8)
            except subprocess.TimeoutExpired:
                p.kill()
        PID.unlink(missing_ok=True)
else:
    raise SystemExit('Acción desconocida.')
