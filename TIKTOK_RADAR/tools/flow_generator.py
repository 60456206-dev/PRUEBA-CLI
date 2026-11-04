#!/usr/bin/env python3
"""
TIKTOK RADAR · Inyector Autónomo y Tolerante a Fallos para Google Flow (Veo)
Diseñado para operar 100% desatendido en servidor AWS Ubuntu con sesión persistente.

Características Anti-Bugs y Auto-Recuperación (Self-Healing):
1. Limpieza automática de bloqueos huérfanos de Chrome (SingletonLock / SingletonSocket).
2. Checkpointing inteligente: verifica con ffprobe qué planos (SH01..SH13) ya existen y son válidos.
3. Navegación autónoma: entra a Google Flow, abre o crea un proyecto automáticamente y configura formato 9:16.
4. Escudo Anti-Popups: envía Escape x3 y cierra modales intrusivos antes de cada acción.
5. Auto-Aprobación de Agente: detecta y aprueba tarjetas de confirmación de Flow si aparecen.
6. Recuperación ante Bloqueo de Políticas o Fallo de Red: si un prompt da error o timeout,
   recarga la página, limpia el estado y reintenta automáticamente con el `fallback_prompt` sanitizado.
7. Doble vía de descarga: descarga oficial por menú (720p/1080p) + intercepción directa de red (.mp4) de respaldo.
"""

import argparse
import asyncio
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.request
from pathlib import Path
from typing import Dict, Any, List, Optional

from playwright.async_api import async_playwright, Page, BrowserContext

ROOT_DIR = Path(__file__).resolve().parent.parent
ENTREGAS_DIR = ROOT_DIR / "entregas"
PROFILE_DIR = Path(os.path.expanduser("~/flow-profile"))
FLOW_URL = "https://labs.google/fx/es/tools/flow"


def log(msg: str) -> None:
    ts = time.strftime("%H:%M:%S")
    print(f"[{ts}] [FLOW-BOT] {msg}", flush=True)


def clean_stale_chrome_locks(profile_dir: Path) -> None:
    """Elimina archivos SingletonLock huérfanos si Chrome se cerró abruptamente en una ejecución previa."""
    for lock_name in ("SingletonLock", "SingletonCookie", "SingletonSocket"):
        lock_path = profile_dir / lock_name
        if lock_path.exists() or lock_path.is_symlink():
            try:
                lock_path.unlink()
                log(f"Lock huérfano eliminado preventivamente: {lock_name}")
            except Exception as e:
                log(f"Aviso al limpiar {lock_name}: {e}")


def verify_mp4(path: Path) -> bool:
    """Verifica con ffprobe que el archivo MP4 exista, no esté corrupto y dure > 1.5s."""
    if not path.exists() or path.stat().st_size < 25_000:
        return False
    try:
        cmd = [
            "ffprobe", "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(path),
        ]
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT, timeout=10).decode().strip()
        dur = float(out)
        return dur >= 1.5
    except Exception:
        return False


def get_latest_delivery_dir(custom_dir: Optional[str] = None) -> Path:
    if custom_dir:
        p = Path(custom_dir).resolve()
        if not p.exists():
            raise FileNotFoundError(f"No existe el directorio especificado: {p}")
        return p
    dirs = sorted(
        [d for d in ENTREGAS_DIR.iterdir() if d.is_dir() and (d / "metadata.json").exists()],
        key=lambda x: x.stat().st_mtime,
        reverse=True,
    )
    if not dirs:
        raise FileNotFoundError(f"No se encontró ninguna carpeta con metadata.json en {ENTREGAS_DIR}")
    return dirs[0]


async def dismiss_stray_popups(page: Page) -> None:
    """Cierra cualquier menú flotante, modal o diálogo intrusivo de la interfaz."""
    try:
        for _ in range(3):
            await page.keyboard.press("Escape")
            await asyncio.sleep(0.15)
        # Cerrar botones de diálogo de bienvenida/avisos si existen
        await page.evaluate("""() => {
            const closeLabels = ['Cerrar', 'Close', 'Entendido', 'Got it', 'Descartar', 'Dismiss'];
            for (const btn of document.querySelectorAll('button')) {
                const txt = (btn.innerText || btn.getAttribute('aria-label') || '').trim();
                if (closeLabels.includes(txt)) {
                    btn.click();
                }
            }
        }""")
    except Exception:
        pass


async def ensure_inside_flow_project(page: Page) -> bool:
    """
    Asegura que el navegador esté dentro del editor de un proyecto de Flow
    (donde existe la caja de texto de prompt) y no en la portada.
    """
    for attempt in range(1, 4):
        try:
            # ¿Ya estamos viendo el cuadro de texto de generación?
            textbox = page.locator(
                'div[role="textbox"][aria-label*="crear"], '
                'div[role="textbox"][aria-label*="create"], '
                'div[role="textbox"], textarea'
            ).first
            if await textbox.count() > 0 and await textbox.is_visible():
                return True

            log(f"Navegando hacia editor de proyecto Flow (intento {attempt}/3)...")
            await dismiss_stray_popups(page)

            # Buscar primero un proyecto existente (/project/) para reutilizar ajustes 9:16 + x1
            clicked = await page.evaluate("""() => {
                // Prioridad 1: Enlace a un proyecto existente (/project/)
                for (const a of document.querySelectorAll('a[href*="/project/"]')) {
                    a.click();
                    return 'existing_project';
                }
                // Prioridad 2: Botón de Nuevo Proyecto / New Project
                const buttons = Array.from(document.querySelectorAll('button, a'));
                for (const b of buttons) {
                    const t = (b.innerText || b.getAttribute('aria-label') || '').toLowerCase();
                    if (t.includes('nuevo proyecto') || t.includes('new project') || t.includes('crear con flow') || t.includes('create with flow')) {
                        b.click();
                        return 'new_project:' + t;
                    }
                }
                return null;
            }""")
            if clicked:
                log(f"Acción de entrada a proyecto ejecutada: {clicked}")
                await asyncio.sleep(5)

            if await textbox.count() > 0 and await textbox.is_visible():
                return True

            # Si sigue sin aparecer, recargar URL base
            await page.goto(FLOW_URL, wait_until="domcontentloaded", timeout=35000)
            await asyncio.sleep(5)
        except Exception as e:
            log(f"Aviso en ensure_inside_flow_project: {e}")
            await asyncio.sleep(3)

    return False


async def configure_vertical_9_16(page: Page) -> None:
    """
    Abre el panel 'tune' (Configuración del agente de este proyecto),
    selecciona '9:16' y 'x1' tanto para imagen como para vídeo (Omni 1.1 Flash),
    y pulsa 'Guardar'.
    """
    try:
        await dismiss_stray_popups(page)
        tune_btn = page.locator('button:has-text("tune")').first
        if await tune_btn.count() > 0 and await tune_btn.is_visible():
            await tune_btn.click(force=True)
            await asyncio.sleep(1.5)
            await page.evaluate("""() => {
                for (const b of document.querySelectorAll('button.mat-button-toggle-button')) {
                    const t = (b.innerText || '').replace(/\\s+/g, ' ').trim();
                    if (t.includes('9:16') || t === 'x1') {
                        b.click();
                    }
                }
            }""")
            await asyncio.sleep(0.6)
            save_btn = page.locator('button.settings-save-button, button:has-text("Guardar")').first
            if await save_btn.count() > 0 and await save_btn.is_visible():
                await save_btn.click(force=True)
                log("Ajustes del agente Flow fijados y guardados: Vídeo 9:16 Vertical (1x - Omni 1.1 Flash).")
                await asyncio.sleep(1.5)
        await dismiss_stray_popups(page)
    except Exception as e:
        log(f"Nota al configurar 9:16 + x1: {e}")


async def get_tile_states(page: Page) -> List[Dict[str, Any]]:
    """Inspecciona todos los tiles [role='group'] en el DOM de Flow."""
    try:
        return await page.evaluate("""() => {
            return Array.from(document.querySelectorAll('[role="group"]')).map((el, idx) => {
                const txt = (el.innerText || '').trim();
                const lower = txt.toLowerCase();
                const isGenerating = txt.includes('%') || lower.includes('generando') || lower.includes('generating') || lower.includes('cola');
                const isReady = !isGenerating && txt.includes('play_circle');
                const isError = lower.includes('error') || lower.includes('infringir') || lower.includes('policy') ||
                                lower.includes('bloqueado') || lower.includes('no se pudo') || lower.includes('failed');
                const videoEl = el.querySelector('video');
                const videoSrc = videoEl ? (videoEl.src || videoEl.currentSrc || '') : '';
                return {
                    idx,
                    isGenerating,
                    isReady,
                    isError,
                    videoSrc,
                    preview: txt.replace(/\\n+/g, ' ').substring(0, 120)
                };
            });
        }""")
    except Exception:
        return []


async def auto_approve_if_prompted(page: Page) -> bool:
    """Si el agente conversacional de Flow muestra botón 'Aprobar' / 'Approve', lo pulsa automáticamente."""
    try:
        clicked = await page.evaluate("""() => {
            const radios = Array.from(document.querySelectorAll('[role="radio"][aria-label*="Aprobar"], [role="radio"][aria-label*="Approve"]'));
            for (const r of radios) {
                if (r.getAttribute('aria-disabled') !== 'true') {
                    r.click();
                    return 'radio_approve';
                }
            }
            const btns = Array.from(document.querySelectorAll('button:not([disabled])'));
            for (const b of btns) {
                const t = (b.innerText || '').trim().toLowerCase();
                if (t === 'aprobar' || t === 'approve' || t === 'continuar' || t === 'confirmar') {
                    b.click();
                    return 'btn_' + t;
                }
            }
            return null;
        }""")
        if clicked:
            log(f"Confirmación de agente Flow aprobada automáticamente ({clicked}).")
            return True
    except Exception:
        pass
    return False


async def submit_prompt_to_flow(page: Page, prompt_text: str) -> bool:
    """Rellena el prompt forzando modo Vídeo (Omni 1.1 Flash), pulsa Iniciar generación y aprueba la tarjeta."""
    await dismiss_stray_popups(page)

    selectors = [
        'div[role="textbox"][aria-label="¿Qué quieres crear?"]',
        'div[role="textbox"][aria-label*="crear"]',
        'div[role="textbox"][aria-label*="create"]',
        'div[role="textbox"]',
        'textarea',
    ]
    box = None
    for sel in selectors:
        loc = page.locator(sel).first
        if await loc.count() > 0 and await loc.is_visible():
            box = loc
            break

    if box is None:
        log("No se encontró la caja de prompt visible. Intentando recuperar vista de proyecto...")
        if not await ensure_inside_flow_project(page):
            return False
        box = page.locator('div[role="textbox"], textarea').first

    # Prefijo explícito para que el agente de Flow use siempre Omni 1.1 Flash (Vídeo) y nunca Nano Banana (Imagen)
    video_directive = "Generate a video directly using Omni 1.1 Flash (text-to-video, do NOT generate images with Nano Banana): "
    full_prompt = prompt_text if "Omni 1.1 Flash" in prompt_text else (video_directive + prompt_text)

    try:
        await box.click(force=True, timeout=5000)
        await asyncio.sleep(0.3)
        await box.fill(full_prompt)
        await asyncio.sleep(0.7)

        gen_btn = page.locator(
            'button[aria-label="Iniciar generación"], '
            'button[aria-label*="generación"], '
            'button[aria-label*="Generate"], '
            'button[aria-label*="Enviar"]'
        ).first

        if await gen_btn.count() > 0:
            await gen_btn.click(force=True)
        else:
            await page.keyboard.press("Enter")

        # Esperar hasta 25s a que el agente muestre el botón 'Aprobar' y pulsarlo
        for sec in range(25):
            await asyncio.sleep(1.0)
            if await auto_approve_if_prompted(page):
                await asyncio.sleep(2.5)
                break
        return True
    except Exception as e:
        log(f"Error al enviar prompt: {e}")
        return False


async def download_completed_tile(
    page: Page,
    tile_idx: int,
    output_path: Path,
    captured_urls: List[str],
) -> bool:
    """
    Descarga el vídeo del tile completado usando dos estrategias:
    Estrategia A: Menú 'Más opciones' -> 'Descargar' -> '720p'/'1080p' con expect_download.
    Estrategia B (Fallback): Descarga directa del stream MP4 capturado por red o atributo <video src>.
    """
    await dismiss_stray_popups(page)

    # Estrategia A: Menú nativo de descarga de Flow
    try:
        groups = page.locator('[role="group"]')
        target_group = groups.nth(tile_idx)
        await target_group.scroll_into_view_if_needed(timeout=5000)
        await target_group.hover(timeout=5000)
        await asyncio.sleep(0.6)

        more_btn = target_group.locator(
            'button[aria-label="Más opciones"], button[aria-label="More options"], button:has-text("more_vert")'
        ).first
        await more_btn.click(force=True, timeout=5000)
        await asyncio.sleep(1.0)

        dl_item = page.locator('[role="menuitem"]').filter(has_text="Descargar").first
        if await dl_item.count() == 0:
            dl_item = page.locator('[role="menuitem"]').filter(has_text="Download").first

        await dl_item.hover(timeout=4000)
        await dl_item.click(timeout=4000)
        await asyncio.sleep(1.0)

        async with page.expect_download(timeout=45000) as dl_info:
            res_item = page.locator('[role="menuitem"]').filter(has_text="720p").first
            if await res_item.count() > 0 and await res_item.is_visible():
                await res_item.click()
            else:
                res_1080 = page.locator('[role="menuitem"]').filter(has_text="1080p").first
                if await res_1080.count() > 0 and await res_1080.is_visible():
                    await res_1080.click()

        download = await dl_info.value
        await download.save_as(str(output_path))
        if verify_mp4(output_path):
            log(f"Descarga oficial UI exitosa: {output_path.name} ({output_path.stat().st_size // 1024} KB)")
            return True
    except Exception as e:
        log(f"Aviso en descarga por menú UI ({e}). Activando Estrategia B (red directa)...")

    # Estrategia B: Extraer URL de vídeo del DOM o de las respuestas de red interceptadas
    try:
        states = await get_tile_states(page)
        candidate_urls = []
        if 0 <= tile_idx < len(states) and states[tile_idx].get("videoSrc"):
            candidate_urls.append(states[tile_idx]["videoSrc"])
        candidate_urls.extend(reversed(captured_urls))

        for url in candidate_urls:
            if not url or not url.startswith("http"):
                continue
            log(f"Descargando stream directo de respaldo: {url[:80]}...")
            subprocess.run(
                ["curl", "-sL", "--max-time", "45", "-o", str(output_path), url],
                check=False,
            )
            if verify_mp4(output_path):
                log(f"Descarga directa por red verificada: {output_path.name}")
                return True
    except Exception as e:
        log(f"Error en Estrategia B de descarga: {e}")

    return False


async def generate_single_shot(
    page: Page,
    shot: Dict[str, Any],
    output_path: Path,
    captured_urls: List[str],
    max_attempts: int = 3,
) -> bool:
    """
    Gestiona el ciclo completo de un plano con reintentos, cambio automático a
    fallback_prompt si hay bloqueo de políticas y recarga limpia ante cuelgues.
    """
    shot_id = shot["id"]
    primary_prompt = shot["prompt"]
    fallback_prompt = shot.get("fallback_prompt", primary_prompt)

    for attempt in range(1, max_attempts + 1):
        use_prompt = primary_prompt if attempt == 1 else fallback_prompt
        mode_label = "PRINCIPAL" if attempt == 1 else f"FALLBACK ANTI-BLOQUEO (Intento {attempt}/{max_attempts})"
        log(f"=== Generando {shot_id} [{mode_label}] ===")

        # Contar tiles listos antes de enviar
        before_states = await get_tile_states(page)
        ready_indices_before = {t["idx"] for t in before_states if t["isReady"]}
        captured_urls.clear()

        ok_submit = await submit_prompt_to_flow(page, use_prompt)
        if not ok_submit:
            log(f"Fallo al inyectar el prompt de {shot_id}. Recargando página para limpiar estado...")
            try:
                await page.reload(wait_until="domcontentloaded", timeout=35000)
                await asyncio.sleep(5)
                await ensure_inside_flow_project(page)
            except Exception:
                pass
            continue

        # Monitorear el progreso de generación (máximo 240s por clip)
        start_t = time.time()
        target_ready_idx: Optional[int] = None
        policy_failed = False

        while time.time() - start_t < 240:
            await asyncio.sleep(5)
            await auto_approve_if_prompted(page)
            states = await get_tile_states(page)

            # Verificar si hay un nuevo tile listo (en Flow el nuevo suele insertarse en idx 0)
            new_ready = [
                t for t in states
                if t["isReady"] and (t["idx"] == 0 or len(states) > len(before_states) or t["idx"] not in ready_indices_before)
            ]
            # Pero asegurémonos de que si idx 0 ya estaba antes y el conteo no cambió, esperemos a que termine de generar
            generating_tiles = [t for t in states if t["isGenerating"]]
            error_tiles = [t for t in states[:2] if t["isError"]]

            if error_tiles and not generating_tiles:
                log(f"⚠️ Detectado error/bloqueo en tile de Flow: {error_tiles[0]['preview']}")
                policy_failed = True
                break

            if len(states) > len(before_states):
                # Se añadió un nuevo tile; esperamos a que el primer tile nuevo esté isReady
                if states[0]["isReady"]:
                    target_ready_idx = 0
                    break

            elapsed = int(time.time() - start_t)
            if generating_tiles:
                if elapsed % 15 == 0:
                    log(f"   {shot_id} renderizando en Google Flow ({elapsed}s)... {generating_tiles[0]['preview'][:60]}")
            elif elapsed > 25 and states and states[0]["isReady"] and len(states) >= len(before_states):
                # Si ya pasaron >25s, no hay ningún tile generando y el tile 0 está listo
                target_ready_idx = 0
                break

        if policy_failed or target_ready_idx is None:
            log(f"No se obtuvo clip válido en intento {attempt} para {shot_id}. Aplicando auto-curación...")
            try:
                await page.reload(wait_until="domcontentloaded", timeout=35000)
                await asyncio.sleep(5)
                await ensure_inside_flow_project(page)
            except Exception:
                pass
            continue

        # Descargar el tile completado
        if await download_completed_tile(page, target_ready_idx, output_path, captured_urls):
            return True

    return False


async def run_flow_generator(delivery_dir: Path, max_shots: int = 13) -> bool:
    meta_file = delivery_dir / "metadata.json"
    if not meta_file.exists():
        raise FileNotFoundError(f"No se encontró {meta_file}")

    meta = json.loads(meta_file.read_text(encoding="utf-8"))
    shots: List[Dict[str, Any]] = meta.get("shots", [])[:max_shots]
    if not shots:
        raise RuntimeError("metadata.json no contiene la lista de planos ('shots'). Ejecuta primero pipeline_autonomo.py.")

    shots_dir = delivery_dir / "shots"
    shots_dir.mkdir(parents=True, exist_ok=True)

    # Comprobar qué planos faltan por generar (Checkpointing)
    pending_shots = []
    flow_shots = [s for s in shots if s.get("render_mode") != "infographic"]
    infographic_count = len(shots) - len(flow_shots)

    for s in shots:
        if s.get("render_mode") == "infographic":
            log(f"⚡ [MODO HÍBRIDO] Omitiendo {s['id']} en Google Flow (se sintetiza en FFmpeg Vector HUD sin costo de créditos).")
            continue
        out_mp4 = shots_dir / f"{s['id']}.mp4"
        if verify_mp4(out_mp4):
            log(f"✓ {s['id']}.mp4 ya existe y es válido (DECODE_OK). Saltando...")
        else:
            pending_shots.append(s)

    if not pending_shots:
        log(f"🎉 Todos los planos cinematográficos ({len(flow_shots)}/{len(flow_shots)}) ya están listos (+ {infographic_count} infográficos FFmpeg).")
        return True

    if not PROFILE_DIR.exists():
        log(f"[ERROR] No existe el perfil {PROFILE_DIR}. Inicia sesión primero.")
        return False

    clean_stale_chrome_locks(PROFILE_DIR)

    log(f"Iniciando navegador autónomo con perfil {PROFILE_DIR} ({len(pending_shots)} planos pendientes)...")
    captured_urls: List[str] = []

    async with async_playwright() as p:
        context: BrowserContext = await p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            channel="chrome",
            headless=True,
            accept_downloads=True,
            viewport={"width": 1440, "height": 900},
            args=[
                "--disable-gpu",
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled",
            ],
        )

        page = context.pages[0] if context.pages else await context.new_page()

        # Interceptar URLs de vídeo de Google Flow como respaldo automático
        def on_response(response):
            url = response.url
            if ("flow-content" in url or "video" in url or ".mp4" in url) and response.status == 200:
                ct = response.headers.get("content-type", "")
                if "video" in ct or "mp4" in url:
                    captured_urls.append(url)

        page.on("response", on_response)

        try:
            log(f"Abriendo Google Flow ({FLOW_URL})...")
            await page.goto(FLOW_URL, wait_until="domcontentloaded", timeout=40000)
            await asyncio.sleep(5)

            if "accounts.google.com" in page.url or "sign in" in (await page.title()).lower():
                log("[ERROR CRÍTICO] La sesión de Google expiró. Vuelve a iniciar sesión en ~/flow-profile.")
                await context.close()
                return False

            if not await ensure_inside_flow_project(page):
                log("[ERROR] No se pudo acceder al editor de proyectos de Flow.")
                await page.screenshot(path=str(delivery_dir / "flow_error_debug.png"))
                await context.close()
                return False

            await configure_vertical_9_16(page)

            for s in pending_shots:
                out_mp4 = shots_dir / f"{s['id']}.mp4"
                success = await generate_single_shot(page, s, out_mp4, captured_urls)
                if not success:
                    log(f"⚠️ No se pudo obtener {s['id']} tras múltiples intentos. Guardando captura de diagnóstico...")
                    await page.screenshot(path=str(delivery_dir / f"debug_{s['id']}.png"))
                else:
                    log(f"✅ {s['id']} completado y verificado.")

        finally:
            await context.close()

    completed_flow = sum(1 for s in flow_shots if verify_mp4(shots_dir / f"{s['id']}.mp4"))
    log(f"Resumen de lote Flow Híbrido: {completed_flow}/{len(flow_shots)} planos cinematográficos listos (+ {infographic_count} infográficos FFmpeg).")
    return completed_flow == len(flow_shots)


def main():
    parser = argparse.ArgumentParser(description="Inyector autónomo de Google Flow para TikTok Radar")
    parser.add_argument("--dir", type=str, default=None, help="Ruta a la carpeta de entrega (por defecto la más reciente)")
    parser.add_argument("--max-shots", type=int, default=13, help="Número máximo de planos a procesar")
    args = parser.parse_args()

    delivery_dir = get_latest_delivery_dir(args.dir)
    ok = asyncio.run(run_flow_generator(delivery_dir, max_shots=args.max_shots))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
