#!/usr/bin/env python3
"""
TIKTOK RADAR · Verificador de Sesión de Google Flow en Servidor AWS
Comprueba que el perfil de usuario tenga la sesión de Google guardada
y que Flow cargue correctamente en segundo plano.
"""

import asyncio
import os
import subprocess
import sys
from pathlib import Path
from playwright.async_api import async_playwright

PROFILE_DIR = os.path.expanduser("~/flow-profile")


async def verify():
    print(f"1. Verificando perfil de usuario en: {PROFILE_DIR}...", flush=True)
    if not os.path.exists(PROFILE_DIR):
        print(f"[ERROR] No se encontró el directorio {PROFILE_DIR}. Asegúrate de haber iniciado sesión primero.")
        sys.exit(1)

    print("2. Iniciando Chrome con la sesión persistente...", flush=True)
    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir=PROFILE_DIR,
            channel="chrome",
            headless=True,
            args=[
                "--disable-gpu",
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled"
            ]
        )
        
        page = context.pages[0] if context.pages else await context.new_page()
        print("3. Cargando Google Flow...", flush=True)
        try:
            await page.goto("https://labs.google/flow", wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(4)
            current_url = page.url
            title = await page.title()
            print(f"\n✅ CONEXIÓN EXITOSA:")
            print(f"   URL: {current_url}")
            print(f"   Título de la página: {title}")

            # Tomar captura de verificación
            screenshot_path = Path.home() / "flow_verificado.png"
            await page.screenshot(path=str(screenshot_path))
            print(f"   Captura de pantalla de verificación guardada en: {screenshot_path}")

            if "sign in" in title.lower() or "accounts.google.com" in current_url:
                print("\n⚠️ AVISO: Parece que la sesión aún no está iniciada en Flow. Vuelve a iniciar sesión si te pide credenciales.")
            else:
                print("\n🎉 ¡SESIÓN CONFIRMADA Y ACTIVA! Tu servidor está listo para generar vídeos con Flow.")
        except Exception as e:
            print(f"[Error al conectar con Flow]: {e}")
        finally:
            await context.close()


if __name__ == "__main__":
    asyncio.run(verify())
