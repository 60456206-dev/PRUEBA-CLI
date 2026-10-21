#!/usr/bin/env python3
"""Prepara los dos archivos del plano activo y una ayuda local, sin red."""
from pathlib import Path
import html
import shutil

base = Path(__file__).resolve().parent
repo = base.parent.parent
package = repo / 'MASTER_SERIES_PACKAGE'
prompt = package / 'VIDEO_PROMPTS/GOOGLE_FLOW/EP01_SH03_GOOGLE_FLOW.txt'
image = package / 'SHOT_REFERENCES/SALT_DROP.png'
for source in (prompt, image):
    if not source.is_file():
        raise SystemExit(f'Falta el archivo del repositorio: {source}')
text = prompt.read_text(encoding='utf-8')
out = base / 'preparado'
out.mkdir(exist_ok=True)
shutil.copy2(image, out / image.name)
shutil.copy2(prompt, out / prompt.name)
page = '''<!doctype html><html lang="es"><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>MASTER SERIES · Plano 3</title>
<style>body{font:18px system-ui;max-width:850px;margin:40px auto;padding:20px;background:#171717;color:#eee}a{color:#9cd3ff}textarea{box-sizing:border-box;width:100%;height:320px;font:15px monospace}img{max-width:240px}button{font:inherit;padding:10px;margin:10px 0}</style>
<h1>Plano 3 · Google Flow</h1>
<p>Inicia sesión en la pestaña oficial de Google Flow con tu cuenta institucional. Esta página no pide ni recibe credenciales.</p>
<p>Esta ayuda prepara los archivos. No conecta el navegador con el asistente ni genera vídeos automáticamente.</p>
<ol><li>Abre un proyecto en Flow y selecciona fotogramas a vídeo, vertical 9:16.</li>
<li>Carga <a href="SALT_DROP.png" download>SALT_DROP.png</a> como imagen inicial.</li>
<li>Copia el prompt de abajo. Genera una sola variante. Si permite 6 segundos, usa esa duración; el montaje utilizará 5 segundos.</li>
<li>Descarga el resultado y compártelo con el asistente antes de reintentar. Para ante cualquier límite o solicitud de pago.</li></ol>
<p>Aceptamos pequeñas imprecisiones si se entiende: gota → contacto con sal → humedad localizada.</p>
<label for="prompt">Prompt del repositorio</label><textarea id="prompt" readonly>TEXT</textarea>
<button id="copy">Copiar prompt</button><span id="status" role="status"></span>
<p><a href="EP01_SH03_GOOGLE_FLOW.txt" download>Descargar prompt</a></p>
<img src="SALT_DROP.png" alt="Gota en la pipeta sobre la sal del abrigo">
<script>document.getElementById('copy').onclick=async()=>{const p=document.getElementById('prompt');p.focus();p.select();try{await navigator.clipboard.writeText(p.value);document.getElementById('status').textContent=' Copiado';}catch{document.getElementById('status').textContent=' Pulsa Ctrl+C para copiar el texto seleccionado';}};</script></html>'''
(out / 'index.html').write_text(page.replace('TEXT', html.escape(text)), encoding='utf-8')
print(f'Archivos preparados: {out}')
