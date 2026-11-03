# TikTok Radar · Noticiero 3D de Alto Impacto

Sistema de producción ágil de micro-noticieros animados en formato vertical (9:16, **61–65 segundos monetizables**), combinando investigación de actualidad en fuentes oficiales y medios de referencia (como Xataka, BBC Mundo, Reuters) con recreaciones en **animación 3D estilizada** (sin hiperrealismo) y locución periodística profesional.

> [!IMPORTANT]
> **Monetización en TikTok (Creator Rewards Program):**
> Para monetizar en TikTok, la plataforma exige **estrictamente más de 60 segundos de duración (> 1 minuto)**. Los vídeos de menos de 60 segundos no monetizan en dicho programa. Nuestro estándar operativo se fija exactamente en **61 a 65 segundos**: supera el umbral de monetización de forma segura, pero sin estirarse de más para evitar caídas de retención y mantener el dinamismo sin aburrir al espectador.

> [!NOTE]
> **Independencia Total de MASTER_SERIES_PACKAGE:**
> Este proyecto opera de forma 100% aislada dentro del directorio `TIKTOK_RADAR/`. No comparte personajes, referencias, audios ni archivos con `MASTER_SERIES_PACKAGE`.

---

## 1. Principios del Enfoque Editorial y Técnico

1. **Duración Monetizable (61 a 65 s):** 
   - Diseñado milimétricamente para superar los 60 segundos del *TikTok Creator Rewards Program*.
   - Ritmo ágil con 12 a 15 micro-planos dinámicos y narrativa de 130 a 145 palabras para que el minuto pase volando y no aburra en ningún momento.
2. **Fuentes Contrastadas:**
   - **Fuentes Oficiales:** Reportes gubernamentales, autoridades de aviación (FAA/NTSB), juzgados y comunicados corporativos directos.
   - **Medios Reconocidos:** Portales especializados como **Xataka** (tecnología, ciencia y ciberseguridad), BBC Mundo y El País.
   - **Distinción Editorial:** Separar siempre hechos confirmados de reportes preliminares o hipótesis en investigación.
3. **Estilo Visual: Animación 3D Estilizada (Cero Hiperrealismo):**
   - Rechazo explícito del *uncanny valley* (cero fotos de humanos reales mal generados por IA con expresiones de plástico o manos deformes).
   - Estética inspirada en cinemáticas de animación moderna (*Arcane*, *Spider-Verse*, cinemáticas 3D de alta gama de Unreal Engine/Octane).
   - **Modo Recreación:** Para sucesos dramáticos (ej. cabina de avión, centro de mando, laboratorio), escenificando tensión, sudor y gesticulación de personajes estilizados.
   - **Modo Infográfico 3D:** Para noticias de ciberseguridad, software o ciencia abstracta, utilizando modelos 3D, mapas cinemáticos, racks de servidores y documentos holográficos en movimiento.
4. **Voz y Locución Periodística:**
   - Locutor sobrio, articulado, con dicción urgente y micropausas de suspenso calculadas (130–145 palabras/min).
5. **Tiempo por Plano (4 a 5 segundos de generación):**
   - **Generación en IA:** Clips de **4 a 5 segundos** por plano. Esto reduce el tiempo de render a una fracción, evita morfeos y asegura una tasa de éxito >95%.
   - **Montaje en Edición:** Cada plano se recorta entre **2,5 y 4,0 segundos**, cambiando el ángulo de cámara frecuentemente para mantener los ojos del espectador pegados a la pantalla.
6. **Meta de Velocidad (< 1 hora):**
   - Desde que se detecta la noticia hasta tener el vídeo vertical exportado y listo para publicar debe transcurrir menos de 60 minutos.

---

## 2. Estructura de Directorios

```text
TIKTOK_RADAR/
├── README.md                                  # Este documento
├── 01_ARQUITECTURA_NOTICIERO_3D.md            # Arquitectura técnica y benchmarking de repositorios
├── tools/
│   └── news_radar.py                          # Escáner en tiempo real de Xataka, BBC y RSS oficiales
├── prompts/
│   └── FORMULA_MAESTRA_PROMPTS.md             # Guía de prompts de animación 3D y locución
├── templates/                                 # Plantillas de guiones y subtítulos kinetic
└── entregas/
    └── CASO_EJEMPLO_ACCIDENTE_FLORIDA.md      # Caso prototipo completo (accidente aéreo)
```

---

## 3. Comandos Útiles

* **Escanear noticias en tiempo real:**
  ```bash
  python3 TIKTOK_RADAR/tools/news_radar.py
  ```
