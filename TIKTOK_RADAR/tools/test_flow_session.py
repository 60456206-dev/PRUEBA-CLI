#!/usr/bin/env python3
"""
TIKTOK RADAR · Verificador Multi-Cuenta de Sesión de Google Flow en Servidor AWS
Comprueba que uno o todos los perfiles configurados (~/flow-profile, ~/flow-profiles/*)
tengan sesión de Google activa y que Flow cargue correctamente en segundo plano.
"""

import argparse
import asyncio
import sys
from pathlib import Path

from playwright.async_api import async_playwright

sys.path.insert(0, str(Path(__file__).resolve().parent))
from flow_generator import (  # noqa: E402
    clean_stale_chrome_locks,
    mark_profile_state,
    resolve_flow_profiles,
)


async def verify_single_profile(profile_dir: Path) -> bool:
    print(f"\n1. Verificando perfil de usuario en: {profile_dir}...", flush=True)
    if not profile_dir.exists():
        print(f"[ERROR] No se encontró el directorio {profile_dir}. Inicia sesión primero.")
        return False

    clean_stale_chrome_locks(profile_dir)
    print("2. Iniciando Chrome con la sesión persistente...", flush=True)
    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir=str(profile_dir),
            channel="chrome",
            headless=True,
            args=[
                "--disable-gpu",
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled",
            ],
        )

        page = context.pages[0] if context.pages else await context.new_page()
        print("3. Cargando Google Flow...", flush=True)
        try:
            await page.goto("https://labs.google/fx/es/tools/flow", wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(4)
            current_url = page.url
            title = await page.title()
            print(f"   URL: {current_url}")
            print(f"   Título: {title}")

            shot_name = "flow_verificado.png" if profile_dir.name == "flow-profile" else f"flow_verificado_{profile_dir.name}.png"
            screenshot_path = Path.home() / shot_name
            await page.screenshot(path=str(screenshot_path))
            print(f"   Captura guardada en: {screenshot_path}")

            if "sign in" in title.lower() or "accounts.google.com" in current_url:
                print(f"⚠️ AVISO [{profile_dir.name}]: Sesión expirada o sin login.")
                mark_profile_state(profile_dir, "session_expired", cooldown_hours=24.0)
                return False

            print(f"🎉 ¡SESIÓN ACTIVA [{profile_dir.name}]! Lista para generar en Flow.")
            mark_profile_state(profile_dir, "ok", cooldown_hours=0.0)
            return True
        except Exception as e:
            print(f"[Error al conectar con Flow ({profile_dir.name})]: {e}")
            return False
        finally:
            await context.close()


async def main() -> int:
    parser = argparse.ArgumentParser(description="Verificador de sesiones Google Flow")
    parser.add_argument("--profile", type=str, default=None, help="Ruta específica de perfil Chrome")
    parser.add_argument("--all", action="store_true", help="Verificar todos los perfiles configurados")
    args = parser.parse_args()

    if args.profile:
        targets = [Path(args.profile).expanduser()]
    elif args.all:
        targets = resolve_flow_profiles()
    else:
        targets = resolve_flow_profiles()[:1]

    results = []
    for prof in targets:
        ok = await verify_single_profile(prof)
        results.append((prof.name, ok))

    ok_count = sum(1 for _, ok in results if ok)
    print(f"\nResumen sesiones Flow activas: {ok_count}/{len(results)} -> {results}")
    return 0 if ok_count > 0 else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
