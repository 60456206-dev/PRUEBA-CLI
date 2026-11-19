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
import re
import shutil
import subprocess
import sys
import time
import urllib.request
from collections import Counter
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

try:
    from playwright.async_api import async_playwright, Page, BrowserContext
except ImportError:
    async_playwright = None  # type: ignore
    Page = Any  # type: ignore
    BrowserContext = Any  # type: ignore

def _load_flow_config() -> Dict[str, Any]:
    """Carga el bloque google_flow de config_produccion.json de forma segura."""
    cfg_path = ROOT_DIR / "config_produccion.json"
    if not cfg_path.exists():
        return {}
    try:
        return json.loads(cfg_path.read_text(encoding="utf-8")).get("google_flow", {}) or {}
    except Exception:
        return {}


def _resolve_flow_profile_dir() -> Path:
    env_dir = os.getenv("FLOW_PROFILE_DIR")
    if env_dir:
        return Path(os.path.expanduser(env_dir))
    primary = Path(os.path.expanduser("~/flow-profile"))
    legacy = Path(os.path.expanduser("~/flow-chrome-profile"))
    if not primary.exists() and legacy.exists():
        return legacy
    return primary


def resolve_flow_profiles() -> List[Path]:
    """
    Devuelve la lista ordenada y deduplicada de perfiles Chrome de Google Flow.
    Prioridad: FLOW_PROFILE_DIRS > FLOW_PROFILE_DIR > ~/flow-profile + ~/flow-profiles/* + config.
    """
    raw_candidates: List[str] = []
    env_dirs = os.getenv("FLOW_PROFILE_DIRS", "").strip()
    if env_dirs:
        sep = "," if ("," in env_dirs and ":" not in env_dirs) else ":"
        raw_candidates.extend(x.strip() for x in env_dirs.split(sep) if x.strip())
    elif os.getenv("FLOW_PROFILE_DIR", "").strip():
        raw_candidates.append(os.getenv("FLOW_PROFILE_DIR", "").strip())
    else:
        gcfg = _load_flow_config()
        primary = Path(os.path.expanduser(str(gcfg.get("perfil_principal", "~/flow-profile"))))
        if primary.exists():
            raw_candidates.append(str(primary))
        profiles_dir = Path(os.path.expanduser(str(gcfg.get("carpeta_perfiles", "~/flow-profiles"))))
        if profiles_dir.exists() and profiles_dir.is_dir():
            for child in sorted(profiles_dir.iterdir()):
                if child.is_dir() and not child.name.startswith("."):
                    raw_candidates.append(str(child))
        for extra in gcfg.get("perfiles_extra", []) or []:
            p_extra = Path(os.path.expanduser(str(extra)))
            if p_extra.exists():
                raw_candidates.append(str(p_extra))
        if not raw_candidates:
            raw_candidates.append(str(_resolve_flow_profile_dir()))

    deduped: List[Path] = []
    seen = set()
    for item in raw_candidates:
        p = Path(os.path.expanduser(item))
        key = str(p.resolve())
        if key not in seen:
            seen.add(key)
            deduped.append(p)
    return deduped


def get_flow_state_file() -> Path:
    return Path(os.path.expanduser(os.getenv("FLOW_STATE_FILE", "~/.flow_profiles_state.json")))


def load_flow_profile_state(state_file: Optional[Path] = None) -> Dict[str, Any]:
    sf = state_file or get_flow_state_file()
    if not sf.exists():
        return {}
    try:
        data = json.loads(sf.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def save_flow_profile_state(state: Dict[str, Any], state_file: Optional[Path] = None) -> None:
    sf = state_file or get_flow_state_file()
    sf.parent.mkdir(parents=True, exist_ok=True)
    sf.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")


def mark_profile_state(
    profile_dir: Path,
    reason: str,
    cooldown_hours: float = 0.0,
    state_file: Optional[Path] = None,
    now: Optional[float] = None,
) -> Dict[str, Any]:
    """Registra éxito, cuota agotada o sesión expirada para un perfil de Flow."""
    ts = time.time() if now is None else float(now)
    state = load_flow_profile_state(state_file)
    key = str(profile_dir.resolve())
    entry = dict(state.get(key, {}))
    entry["profile_name"] = profile_dir.name
    entry["reason"] = reason
    entry["updated_at"] = ts
    if reason == "ok":
        entry["cooldown_until"] = 0.0
        entry["last_ok_at"] = ts
    elif reason == "session_expired":
        entry["cooldown_until"] = ts + max(float(cooldown_hours), 24.0) * 3600.0
        entry["last_error_at"] = ts
    else:
        entry["cooldown_until"] = ts + max(0.0, float(cooldown_hours)) * 3600.0
        entry["last_error_at"] = ts
    state[key] = entry
    save_flow_profile_state(state, state_file)
    return entry


def select_available_profiles(
    profiles: List[Path],
    state: Optional[Dict[str, Any]] = None,
    now: Optional[float] = None,
    ignore_cooldown: bool = False,
) -> List[Path]:
    """Filtra perfiles en cooldown activo o expirados manteniendo el orden secuencial."""
    ts = time.time() if now is None else float(now)
    st = state if state is not None else load_flow_profile_state()
    if ignore_cooldown:
        return [p for p in profiles if p.exists()]

    available: List[Path] = []
    for p in profiles:
        if not p.exists():
            continue
        info = st.get(str(p.resolve()), {})
        cd = float(info.get("cooldown_until", 0.0) or 0.0)
        reason = str(info.get("reason", "ok"))
        if cd > ts:
            mins = max(1, int((cd - ts) // 60))
            log(f"⏭️ Omitiendo perfil '{p.name}' (en cooldown por '{reason}', restan ~{mins} min).")
            continue
        if reason == "session_expired":
            log(f"⏭️ Omitiendo perfil '{p.name}' (sesión expirada; re-autenticar con ~/iniciar_flow_perfil.sh {p.name}).")
            continue
        available.append(p)
    return available


def reset_active_session_state() -> None:
    """Reinicia el estado global del modelo activo antes de abrir otra cuenta Flow."""
    global ACTIVE_VIDEO_MODEL, QUOTA_EXHAUSTED_ALL_MODELS
    ACTIVE_VIDEO_MODEL = "Omni 1.1 Flash"
    QUOTA_EXHAUSTED_ALL_MODELS = False


ROOT_DIR = Path(__file__).resolve().parent.parent
ENTREGAS_DIR = ROOT_DIR / "entregas"
PROFILE_DIR = _resolve_flow_profile_dir()
FLOW_URL = "https://labs.google/fx/es/tools/flow"
ACTIVE_VIDEO_MODEL = "Omni 1.1 Flash"
QUOTA_EXHAUSTED_ALL_MODELS = False


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

            # Prioridad 1: Botón Start Creating / Comenzar
            # Prioridad 2: Enlace a un proyecto existente (/project/)
            # Prioridad 3: Botón Nuevo Proyecto
            clicked = await page.evaluate("""() => {
                for (const b of document.querySelectorAll('button')) {
                    const txt = (b.innerText || '').trim().toLowerCase();
                    if (txt === 'start creating' || txt === 'comenzar' || txt === 'crear con flow') {
                        b.click();
                        return 'start_creating';
                    }
                }
                for (const a of document.querySelectorAll('a[href*="/project/"]')) {
                    a.click();
                    return 'existing_project';
                }
                const buttons = Array.from(document.querySelectorAll('button, a'));
                for (const b of buttons) {
                    const t = (b.innerText || b.getAttribute('aria-label') || '').toLowerCase();
                    if (
                        t.includes('nuevo proyecto') ||
                        t.includes('proyecto nuevo') ||
                        t.includes('new project') ||
                        t.includes('crear con flow') ||
                        t.includes('create with flow')
                    ) {
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
    """Inspecciona todos los tiles [role='group'] en el DOM de Flow con firma única."""
    try:
        return await page.evaluate("""() => {
            return Array.from(document.querySelectorAll('[role="group"]')).map((el, idx) => {
                const txt = (el.innerText || '').trim();
                const lower = txt.toLowerCase();
                const tag = (el.tagName || '').toLowerCase();
                const ariaLabel = (el.getAttribute('aria-label') || '').trim();
                const isGridTile = tag === 'flow-grid-tile-container' || !ariaLabel.toLowerCase().includes('galería de opciones');
                const isGenerating = /\\b\\d{1,3}\\s*%/.test(txt) || lower.includes('generando') || lower.includes('generating') || lower.includes('cola');
                const isReady = !isGenerating && txt.includes('play_circle');
                const isError = lower.includes('error') || lower.includes('infringir') || lower.includes('policy') ||
                                lower.includes('bloqueado') || lower.includes('no se pudo') || lower.includes('failed');
                const videoEl = el.querySelector('video');
                const videoSrc = videoEl ? (videoEl.src || videoEl.currentSrc || '') : '';
                const imgs = Array.from(el.querySelectorAll('img'));
                const imgSrc = imgs.map(i => (i.currentSrc || i.src || '').trim()).filter(Boolean).join('|');
                const imgAlt = imgs.map(i => (i.alt || '').trim()).filter(Boolean).join('|').substring(0, 180);
                return {
                    idx,
                    isGridTile,
                    isGenerating,
                    isReady,
                    isError,
                    videoSrc,
                    imgSrc,
                    ariaLabel,
                    imgAlt,
                    preview: txt.replace(/\\n+/g, ' ').substring(0, 120)
                };
            });
        }""")
    except Exception:
        return []


def _tile_signature(tile: Dict[str, Any]) -> Tuple[str, str, str, str, str]:
    """Construye una firma estable para distinguir tiles completados aunque `innerText` sea idéntico."""
    return (
        str(tile.get("videoSrc") or ""),
        str(tile.get("imgSrc") or ""),
        str(tile.get("ariaLabel") or ""),
        str(tile.get("imgAlt") or ""),
        str(tile.get("preview") or ""),
    )


def _select_new_or_changed_tiles(
    before_states: List[Dict[str, Any]],
    current_states: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Devuelve los tiles nuevos o modificados comparando multiplicidad de firmas
    desde el final (tiles más antiguos) hacia el inicio (tiles recién agregados en Flow).
    """
    remaining_before = Counter(_tile_signature(s) for s in before_states)
    out: List[Dict[str, Any]] = []
    for tile in reversed(current_states):
        sig = _tile_signature(tile)
        if remaining_before[sig] > 0:
            remaining_before[sig] -= 1
        else:
            out.append(tile)
    out.reverse()
    return out


def classify_flow_body_status(body_text: str) -> Optional[str]:
    """Detecta en el texto visible de Flow límites de cuota, falta de créditos o actividad inusual."""
    lower = (body_text or "").lower()
    if any(
        phrase in lower
        for phrase in (
            "quota limit",
            "daily quota",
            "reached your daily",
            "alternative like veo",
            "switch to another model, such as veo",
            "límite de cuota",
            "limite de cuota",
            "cuota diaria",
            "límite diario",
            "limite diario",
            "daily limit",
            "out of credits",
            "sin créditos",
            "sin creditos",
            "insufficient credits",
            "créditos insuficientes",
            "creditos insuficientes",
            "puntos insuficientes",
            "sin puntos",
            "credits remaining",
            "top up credits",
            "wait for credits to refresh",
            "recargar tus créditos",
            "recargar tus puntos",
            "espera a que se restablezcan",
        )
    ):
        return "quota_limit"
    if re.search(r"(requires|necesita|requiere)\s+\d+\s+(credits|créditos|puntos)", lower) and (
        "remaining" in lower or "tienes" in lower or "currently have" in lower
    ):
        return "quota_limit"
    if "actividad inusual" in lower:
        return "unusual_activity"
    return None


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


def generate_story_style_anchor(
    delivery_dir: Path,
    title: str,
    genre: str,
    style_prefix: str = "",
) -> Optional[Path]:
    """
    Obtiene o genera una única imagen ancla editorial 9:16 por noticia (FLOW_STYLE_ANCHOR.jpg)
    para mantener coherencia de paleta, textura e iluminación entre los planos de Google Flow.
    """
    anchor_path = delivery_dir / "FLOW_STYLE_ANCHOR.jpg"
    if anchor_path.exists() and anchor_path.stat().st_size > 25_000:
        return anchor_path

    portada_ai = delivery_dir / "PORTADA_AI_BASE.jpg"
    if portada_ai.exists() and portada_ai.stat().st_size > 25_000:
        shutil.copy2(portada_ai, anchor_path)
        return anchor_path

    try:
        from generador_portada import _try_gemini_image_cover
        clean_t = re.sub(r"[^\w\s\-:]", " ", title or "").strip()[:110]
        base_style = style_prefix or (
            "Vertical 9:16, tactile 2.5D editorial documentary illustration and chiaroscuro diorama aesthetic, "
            "warm directional tungsten rim light against deep carbon slate shadows, subtle archival paper fiber patina, "
            "no text overlays, no watermarks"
        )
        prompt = f"{base_style}. Style and color anchor visual depicting: {clean_t} ({genre})."
        img_bytes = _try_gemini_image_cover(prompt)
        if img_bytes:
            anchor_path.write_bytes(img_bytes)
            meta_file = delivery_dir / "metadata.json"
            if meta_file.exists():
                try:
                    m = json.loads(meta_file.read_text(encoding="utf-8"))
                    m["style_anchor_image"] = anchor_path.name
                    meta_file.write_text(json.dumps(m, indent=2, ensure_ascii=False), encoding="utf-8")
                except Exception:
                    pass
            log(f"🎨 Ancla de estilo Flow generada y guardada: {anchor_path.name}")
            return anchor_path
    except Exception as e:
        log(f"Nota generando ancla visual de Flow (se continúa con consistencia por prompt): {e}")

    return None


async def attach_reference_image_to_flow(page: Page, anchor_path: Optional[Path]) -> bool:
    """Adjunta la imagen ancla al compositor de Google Flow si el DOM expone carga de archivos."""
    if not anchor_path or not anchor_path.exists() or anchor_path.stat().st_size < 10_000:
        return False
    try:
        file_input = page.locator('input[type="file"]').first
        if await file_input.count() > 0:
            await file_input.set_input_files(str(anchor_path))
            await asyncio.sleep(1.2)
            log(f"📎 Referencia de estilo adjuntada en Flow: {anchor_path.name}")
            return True
    except Exception as e:
        log(f"Nota adjuntando imagen ancla en Flow (fallback seguro): {e}")
    return False


async def submit_prompt_to_flow(
    page: Page,
    prompt_text: str,
    anchor_image: Optional[Path] = None,
    visual_continuity_hint: str = "",
) -> bool:
    """Rellena el prompt forzando modo Vídeo (Omni 1.1 Flash), adjunta ancla opcional, pulsa Iniciar generación y aprueba."""
    await dismiss_stray_popups(page)
    if anchor_image is not None:
        await attach_reference_image_to_flow(page, anchor_image)

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

    global ACTIVE_VIDEO_MODEL
    # Prefijo explícito según modelo activo (Omni 1.1 Flash o fallback a Veo 3.1 - Lite si hay límite de cuota)
    if ACTIVE_VIDEO_MODEL == "Veo 3.1 - Lite":
        video_directive = "Generate a video directly using Veo 3.1 - Lite (text-to-video, do NOT generate images): "
    else:
        video_directive = "Generate a video directly using Omni 1.1 Flash (text-to-video, do NOT generate images with Nano Banana): "

    full_prompt = prompt_text if ("Omni 1.1 Flash" in prompt_text or "Veo 3.1" in prompt_text) else (video_directive + prompt_text)
    if visual_continuity_hint and visual_continuity_hint.lower() not in full_prompt.lower():
        full_prompt = f"{full_prompt}. Maintain strict visual continuity: {visual_continuity_hint}"

    try:
        await box.click(force=True, timeout=5000)
        await asyncio.sleep(0.3)
        await box.fill(full_prompt)
        await asyncio.sleep(0.5)

        # Disparar eventos nativos para que el botón de generación de Angular se active sin demoras
        await box.evaluate("""el => {
            el.dispatchEvent(new Event('input', { bubbles: true }));
            el.dispatchEvent(new Event('change', { bubbles: true }));
        }""")
        await asyncio.sleep(0.5)

        gen_btn = page.locator(
            'button.generate-icon-button, '
            'button[type="submit"], '
            'button[aria-label="Iniciar generación"], '
            'button[aria-label*="generación"], '
            'button[aria-label*="Generate"], '
            'button[aria-label*="Enviar"]'
        ).first

        # Si el botón sigue deshabilitado en Angular, forzar disparo de eventos input y change
        try:
            if await gen_btn.count() > 0:
                is_disabled = await gen_btn.evaluate("el => el.disabled || el.classList.contains('mat-mdc-button-disabled')")
                if is_disabled:
                    await box.evaluate("""el => {
                        el.dispatchEvent(new Event('input', { bubbles: true }));
                        el.dispatchEvent(new Event('change', { bubbles: true }));
                    }""")
                    await asyncio.sleep(0.5)
        except Exception:
            pass

        if await gen_btn.count() > 0 and not await gen_btn.evaluate("el => el.disabled"):
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

        res_target = None
        for res_label in ("720p", "1080p"):
            cand = page.locator('[role="menuitem"]').filter(has_text=res_label).first
            if await cand.count() > 0 and await cand.is_visible():
                res_target = cand
                break

        if res_target is None:
            raise RuntimeError("No apareció opción de resolución 720p/1080p en el menú de descarga.")

        async with page.expect_download(timeout=45000) as dl_info:
            await res_target.click()

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


def select_prompt_for_attempt(shot: Dict[str, Any], attempt: int, use_fallback: bool) -> Tuple[str, bool]:
    """
    Elige el prompt de generación para este intento y normaliza la conmutación automática a
    `fallback_prompt` tras un fallo previo o a partir del intento >= 2.
    """
    primary = (shot.get("prompt") or "").strip()
    fallback = (shot.get("fallback_prompt") or "").strip()
    action = (shot.get("action") or "").strip()

    should_fallback = bool(use_fallback or attempt >= 3)
    if should_fallback and fallback and fallback != primary:
        return fallback, True
    if should_fallback and action:
        return f"Vertical 9:16, cinematic scientific documentary visual, dramatic studio chiaroscuro lighting, {action}", True
    return primary or fallback, False


def _pick_ready_tile_idx(
    new_or_changed: List[Dict[str, Any]],
    all_states: List[Dict[str, Any]],
) -> Optional[int]:
    """Selecciona el índice del tile nuevo listo para descarga, priorizando grid tiles nativos."""
    ready = [
        t for t in new_or_changed
        if t.get("isReady") and not t.get("isGenerating") and not t.get("isError")
    ]
    if not ready:
        return None
    grid_ready = [t for t in ready if t.get("isGridTile", True)]
    if grid_ready:
        return int(grid_ready[0]["idx"])
    if not any(s.get("isGridTile", True) for s in all_states):
        return int(ready[0]["idx"])
    return None


async def generate_single_shot(
    page: Page,
    shot: Dict[str, Any],
    output_path: Path,
    captured_urls: List[str],
    max_attempts: int = 3,
    anchor_image: Optional[Path] = None,
    visual_continuity_hint: str = "",
) -> bool:
    """
    Gestiona el ciclo completo de un plano con reintentos, conservación del prompt
    principal al cambiar por límite de cuota y cambio a fallback_prompt ante bloqueo o reintento.
    """
    global ACTIVE_VIDEO_MODEL, QUOTA_EXHAUSTED_ALL_MODELS
    if QUOTA_EXHAUSTED_ALL_MODELS:
        return False

    shot_id = shot["id"]
    use_fallback_prompt = False

    for attempt in range(1, max_attempts + 1):
        use_prompt, is_fallback_mode = select_prompt_for_attempt(shot, attempt, use_fallback_prompt)
        mode_label = f"FALLBACK ANTI-BLOQUEO (Intento {attempt}/{max_attempts})" if is_fallback_mode else f"PRINCIPAL [{ACTIVE_VIDEO_MODEL}] (Intento {attempt}/{max_attempts})"
        log(f"=== Generando {shot_id} [{mode_label}] ===")

        # Capturar firmas previas de tiles antes de enviar para identificar el tile NUEVO exacto
        before_states = await get_tile_states(page)
        before_count = len(before_states)
        captured_urls.clear()

        ok_submit = await submit_prompt_to_flow(
            page,
            use_prompt,
            anchor_image=anchor_image,
            visual_continuity_hint=visual_continuity_hint,
        )
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
        switched_by_quota = False
        has_started_generating = False
        last_progress_log = -12
        last_progress_preview = ""
        last_progress_change_t = start_t

        while time.time() - start_t < 240:
            await asyncio.sleep(4)
            await auto_approve_if_prompted(page)
            states = await get_tile_states(page)

            new_or_changed = _select_new_or_changed_tiles(before_states, states)
            generating_tiles = [t for t in states if t["isGenerating"]]
            error_tiles = [t for t in new_or_changed if t["isError"]]

            # Detección proactiva de cuota agotada, falta de créditos o actividad inusual
            body_text = await page.evaluate("() => (document.body ? document.body.innerText : '')")
            chat_status = classify_flow_body_status(body_text)

            if chat_status == 'quota_limit':
                if ACTIVE_VIDEO_MODEL != "Veo 3.1 - Lite":
                    log("⚠️ Límite de cuota o créditos en Omni 1.1 Flash. Cambiando a Veo 3.1 - Lite (conservando prompt principal)...")
                    ACTIVE_VIDEO_MODEL = "Veo 3.1 - Lite"
                    switched_by_quota = True
                    break
                else:
                    log("❌ Cuota o créditos agotados también en Veo 3.1 - Lite. Abortando generación Flow restante.")
                    QUOTA_EXHAUSTED_ALL_MODELS = True
                    return False
            elif chat_status == 'unusual_activity':
                log("⚠️ Advertencia de actividad inusual detectada en Flow. Pulsando Reintentar...")
                await page.evaluate("""() => {
                    for (const b of document.querySelectorAll('button')) {
                        if ((b.innerText||'').toLowerCase().includes('reintentar')) b.click();
                    }
                }""")
                await asyncio.sleep(5)

            if error_tiles and not generating_tiles:
                log(f"⚠️ Detectado error/bloqueo en tile nuevo de Flow para {shot_id}: {error_tiles[0]['preview']}")
                policy_failed = True
                break

            if generating_tiles or len(states) > before_count or new_or_changed:
                has_started_generating = True

            # Identificar el tile NUEVO/ACTUALIZADO que ya terminó de renderizar
            ready_idx = _pick_ready_tile_idx(new_or_changed, states)
            if ready_idx is not None:
                target_ready_idx = ready_idx
                break

            now_t = time.time()
            elapsed = int(now_t - start_t)
            if generating_tiles:
                cur_preview = generating_tiles[0]["preview"][:60]
                if cur_preview != last_progress_preview:
                    last_progress_preview = cur_preview
                    last_progress_change_t = now_t
                if elapsed - last_progress_log >= 12:
                    last_progress_log = elapsed
                    log(f"   {shot_id} renderizando en Google Flow ({elapsed}s)... {cur_preview}")
                if now_t - last_progress_change_t >= 120:
                    log(f"⚠️ {shot_id}: Progreso estancado >120s en Flow ({cur_preview}). Reintentando...")
                    policy_failed = True
                    break
            elif not has_started_generating and elapsed > 45:
                log(f"⚠️ {shot_id}: No se detectó inicio de renderizado en Flow tras {elapsed}s.")
                policy_failed = True
                break

        if switched_by_quota:
            try:
                await page.reload(wait_until="domcontentloaded", timeout=35000)
                await asyncio.sleep(4)
                await ensure_inside_flow_project(page)
            except Exception:
                pass
            continue

        if policy_failed or target_ready_idx is None:
            use_fallback_prompt = True
            log(f"No se obtuvo clip válido en intento {attempt} para {shot_id}. Cambiando a fallback_prompt...")
            try:
                await page.reload(wait_until="domcontentloaded", timeout=35000)
                await asyncio.sleep(5)
                await ensure_inside_flow_project(page)
            except Exception:
                pass
            continue

        # Descargar el tile completado exacto
        if await download_completed_tile(page, target_ready_idx, output_path, captured_urls):
            return True
        use_fallback_prompt = True

    return False


async def _run_single_profile_session(
    profile_dir: Optional[Path],
    cdp_url: Optional[str],
    pending_shots: List[Dict[str, Any]],
    shots_dir: Path,
    delivery_dir: Path,
    chrome_exec: Optional[str],
) -> Tuple[str, int]:
    """
    Ejecuta generación secuencial de `pending_shots` usando un perfil Chrome o sesión CDP.
    Devuelve (status, generated_count) donde status es:
    'completed' | 'partial' | 'quota_exhausted' | 'session_expired' | 'error'.
    """
    reset_active_session_state()
    captured_urls: List[str] = []
    generated_count = 0
    label = f"CDP {cdp_url}" if cdp_url else f"perfil '{profile_dir.name if profile_dir else ''}'"

    if profile_dir is not None and not cdp_url:
        clean_stale_chrome_locks(profile_dir)
    log(f"Iniciando sesión Flow con {label} ({len(pending_shots)} planos pendientes)...")

    async with async_playwright() as p:
        cdp_browser = None
        if cdp_url:
            try:
                cdp_browser = await p.chromium.connect_over_cdp(cdp_url)
                log(f"Conectado a sesión Chrome CDP existente en {cdp_url}.")
            except Exception:
                return "error", 0

        created_cdp_page = False
        if cdp_browser is not None:
            context = cdp_browser.contexts[0] if cdp_browser.contexts else await cdp_browser.new_context(accept_downloads=True)
        else:
            if profile_dir is None or not profile_dir.exists():
                return "error", 0
            launch_kwargs: Dict[str, Any] = {
                "user_data_dir": str(profile_dir),
                "headless": True,
                "accept_downloads": True,
                "viewport": {"width": 1440, "height": 900},
                "args": [
                    "--disable-gpu",
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-blink-features=AutomationControlled",
                ],
            }
            if chrome_exec == "/usr/bin/google-chrome":
                launch_kwargs["channel"] = "chrome"
            elif chrome_exec:
                launch_kwargs["executable_path"] = chrome_exec
            context = await p.chromium.launch_persistent_context(**launch_kwargs)

        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            window.chrome = {
                runtime: {},
                loadTimes: function() {},
                csi: function() {},
                app: {}
            };
        """)

        if cdp_browser is not None:
            page = await context.new_page()
            created_cdp_page = True
        else:
            page = context.pages[0] if context.pages else await context.new_page()

        def on_response(response):
            url = response.url
            if ("flow-content" in url or "video" in url or ".mp4" in url) and response.status == 200:
                ct = response.headers.get("content-type", "")
                if "video" in ct or "mp4" in url:
                    captured_urls.append(url)

        page.on("response", on_response)

        try:
            log(f"Abriendo Google Flow ({FLOW_URL}) con {label}...")
            await page.goto(FLOW_URL, wait_until="domcontentloaded", timeout=40000)
            await asyncio.sleep(5)

            if "accounts.google.com" in page.url or "sign in" in (await page.title()).lower():
                log(f"[ERROR CRÍTICO] La sesión de Google expiró en {label}.")
                return "session_expired", generated_count

            if not await ensure_inside_flow_project(page):
                log(f"[ERROR] No se pudo acceder al editor de proyectos de Flow en {label}.")
                await page.screenshot(path=str(delivery_dir / "flow_error_debug.png"))
                return "error", generated_count

            await configure_vertical_9_16(page)

            try:
                new_sess_btn = page.locator('button[aria-label*="Iniciar sesión nueva"], button[aria-label*="New session"]').first
                if await new_sess_btn.count() > 0 and await new_sess_btn.is_visible():
                    await new_sess_btn.click()
                    await asyncio.sleep(2.5)
                    log("Sesión limpia iniciada en Google Flow (hilo reseteado sin tiles previos).")
            except Exception as e:
                log(f"Nota al limpiar hilo de Flow: {e}")

            anchor_cand = delivery_dir / "FLOW_STYLE_ANCHOR.jpg"
            anchor_img = anchor_cand if (anchor_cand.exists() and anchor_cand.stat().st_size > 10_000) else None
            continuity_hint = ""
            meta_p = delivery_dir / "metadata.json"
            if meta_p.exists():
                try:
                    m_data = json.loads(meta_p.read_text(encoding="utf-8"))
                    continuity_hint = str(m_data.get("visual_bible") or "")
                except Exception:
                    continuity_hint = ""

            for s in pending_shots:
                out_mp4 = shots_dir / f"{s['id']}.mp4"
                if verify_mp4(out_mp4):
                    continue
                success = await generate_single_shot(
                    page,
                    s,
                    out_mp4,
                    captured_urls,
                    anchor_image=anchor_img,
                    visual_continuity_hint=continuity_hint,
                )
                if success and verify_mp4(out_mp4):
                    generated_count += 1
                    log(f"✅ {s['id']} completado y verificado con {label}.")
                    continue
                if QUOTA_EXHAUSTED_ALL_MODELS:
                    log(f"⚠️ Cuota agotada en {label}; preparando rotación automática a siguiente cuenta...")
                    return "quota_exhausted", generated_count
                log(f"⚠️ No se pudo obtener {s['id']} en {label}. Guardando captura de diagnóstico...")
                await page.screenshot(path=str(delivery_dir / f"debug_{s['id']}.png"))

            remaining = sum(1 for s in pending_shots if not verify_mp4(shots_dir / f"{s['id']}.mp4"))
            return ("completed" if remaining == 0 else "partial"), generated_count
        finally:
            if cdp_browser is not None:
                if created_cdp_page:
                    try:
                        await page.close()
                    except Exception:
                        pass
            else:
                try:
                    await context.close()
                except Exception:
                    pass


async def run_flow_generator(
    delivery_dir: Path,
    max_shots: int = 13,
    ignore_cooldown: Optional[bool] = None,
) -> bool:
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
    flow_shots = [s for s in shots if s.get("render_mode") not in ("infographic", "remotion")]
    infographic_count = len(shots) - len(flow_shots)
    pending_shots = []

    for s in shots:
        if s.get("render_mode") in ("infographic", "remotion"):
            log(f"⚡ [MODO HÍBRIDO] Omitiendo {s['id']} en Google Flow (se sintetiza en Remotion / Vector HUD sin costo de créditos).")
            continue
        out_mp4 = shots_dir / f"{s['id']}.mp4"
        if verify_mp4(out_mp4):
            log(f"✓ {s['id']}.mp4 ya existe y es válido (DECODE_OK). Saltando...")
        else:
            pending_shots.append(s)

    if not pending_shots:
        log(f"🎉 Todos los planos cinematográficos ({len(flow_shots)}/{len(flow_shots)}) ya están listos (+ {infographic_count} infográficos).")
        return True

    generate_story_style_anchor(
        delivery_dir=delivery_dir,
        title=str(meta.get("title") or ""),
        genre=str(meta.get("genre") or "G1"),
    )

    if async_playwright is None:
        log("[ERROR CRÍTICO] Falta instalar 'playwright' (pip install playwright) para automatizar Google Flow.")
        return False

    chrome_exec = None
    for cand in ("/usr/bin/google-chrome", "/usr/bin/chromium", "/usr/bin/chromium-browser"):
        if os.path.exists(cand):
            chrome_exec = cand
            break

    cdp_url = os.getenv("FLOW_CDP_URL", "http://127.0.0.1:9222")
    cdp_available = False
    try:
        def _probe_cdp() -> bool:
            with urllib.request.urlopen(f"{cdp_url}/json/version", timeout=1.5) as resp:
                return resp.status == 200
        cdp_available = await asyncio.to_thread(_probe_cdp)
    except Exception:
        cdp_available = False

    if cdp_available:
        status, _ = await _run_single_profile_session(
            profile_dir=None,
            cdp_url=cdp_url,
            pending_shots=pending_shots,
            shots_dir=shots_dir,
            delivery_dir=delivery_dir,
            chrome_exec=chrome_exec,
        )
        pending_shots = [s for s in flow_shots if not verify_mp4(shots_dir / f"{s['id']}.mp4")]
        if not pending_shots or status == "completed":
            log(f"Resumen de lote Flow Híbrido (CDP): {len(flow_shots)}/{len(flow_shots)} planos listos.")
            return True

    gcfg = _load_flow_config()
    rotacion_activa = bool(gcfg.get("rotacion_secuencial", True))
    cooldown_horas = float(gcfg.get("cooldown_cuota_horas", 12))
    skip_cd = ignore_cooldown if ignore_cooldown is not None else (os.getenv("FLOW_IGNORE_COOLDOWN") == "1")

    all_profiles = resolve_flow_profiles()
    available_profiles = select_available_profiles(all_profiles, ignore_cooldown=skip_cd)
    if not rotacion_activa and available_profiles:
        available_profiles = available_profiles[:1]

    if not available_profiles:
        log(
            "[ERROR] No hay perfiles Flow disponibles (todos faltan, expiraron o siguen en cooldown). "
            "Usa `bash ~/iniciar_flow_perfil.sh --listar` o `--reset-cooldown`."
        )
        return False

    log(f"🔄 Rotación secuencial Flow lista: {len(available_profiles)} perfil(es) disponible(s) -> {[p.name for p in available_profiles]}")

    for idx, profile_dir in enumerate(available_profiles):
        pending_shots = [s for s in flow_shots if not verify_mp4(shots_dir / f"{s['id']}.mp4")]
        if not pending_shots:
            break

        status, generated_here = await _run_single_profile_session(
            profile_dir=profile_dir,
            cdp_url=None,
            pending_shots=pending_shots,
            shots_dir=shots_dir,
            delivery_dir=delivery_dir,
            chrome_exec=chrome_exec,
        )

        if status == "quota_exhausted":
            mark_profile_state(profile_dir, "quota_exhausted", cooldown_hours=cooldown_horas)
        elif status == "session_expired":
            mark_profile_state(profile_dir, "session_expired", cooldown_hours=24.0)
        elif status in ("completed", "partial") and generated_here > 0:
            mark_profile_state(profile_dir, "ok", cooldown_hours=0.0)

        pending_shots = [s for s in flow_shots if not verify_mp4(shots_dir / f"{s['id']}.mp4")]
        if not pending_shots:
            break

        if idx + 1 < len(available_profiles):
            log(f"⏳ Pausa breve de 3s antes de rotar al siguiente perfil ({available_profiles[idx + 1].name})...")
            await asyncio.sleep(3)

    completed_flow = sum(1 for s in flow_shots if verify_mp4(shots_dir / f"{s['id']}.mp4"))
    log(f"Resumen de lote Flow Híbrido: {completed_flow}/{len(flow_shots)} planos cinematográficos listos (+ {infographic_count} infográficos Remotion/HUD).")
    return completed_flow == len(flow_shots)


def main():
    parser = argparse.ArgumentParser(description="Inyector autónomo de Google Flow para TikTok Radar")
    parser.add_argument("--dir", type=str, default=None, help="Ruta a la carpeta de entrega (por defecto la más reciente)")
    parser.add_argument("--max-shots", type=int, default=13, help="Número máximo de planos a procesar")
    parser.add_argument("--ignore-cooldown", action="store_true", help="Intentar incluso perfiles en cooldown de cuota")
    args = parser.parse_args()

    delivery_dir = get_latest_delivery_dir(args.dir)
    ok = asyncio.run(run_flow_generator(delivery_dir, max_shots=args.max_shots, ignore_cooldown=args.ignore_cooldown))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
