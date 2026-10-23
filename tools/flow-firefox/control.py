#!/usr/bin/env python3
"""Enviar una orden JSON por stdin o consultar con --estado. No reintenta órdenes."""
import json
from pathlib import Path
import sys
import time
import urllib.request

key = (Path.home()/'.local/share/master-series-flow-firefox/clave.txt').read_text().strip()
def request(path, data=None):
    req = urllib.request.Request('http://127.0.0.1:8765'+path,
        data=None if data is None else json.dumps(data).encode(),
        headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'})
    with urllib.request.urlopen(req, timeout=10) as response:
        return json.load(response)

if '--estado' in sys.argv:
    print(json.dumps(request('/status')))
else:
    ident = request('/command', json.load(sys.stdin))['id']
    for _ in range(40):
        result = request('/result/'+ident)
        if result['state'] == 'done':
            if '--imagen' in sys.argv:
                import base64
                destination = Path(sys.argv[sys.argv.index('--imagen')+1])
                value = result['result']
                if not isinstance(value,str) or not value.startswith('data:image/png;base64,'):
                    raise SystemExit(json.dumps(result))
                destination.write_bytes(base64.b64decode(value.split(',',1)[1]))
                print(str(destination))
            else:
                print(json.dumps(result,ensure_ascii=False))
            break
        time.sleep(1)
    else:
        raise SystemExit('Sin respuesta. No repetir una generación sin comprobar Flow. Orden: '+ident)
