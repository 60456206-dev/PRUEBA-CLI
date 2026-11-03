# TikTok Radar · Noticiero 3D de Alto Impacto

Sistema de producción ágil de micro-noticieros animados en formato vertical (9:16, 25–35 segundos), combinando investigación de actualidad en fuentes oficiales y medios de referencia (como Xataka, BBC Mundo, Reuters) con recreaciones en **animación 3D estilizada** (sin hiperrealismo) y locución periodística profesional.

> [!IMPORTANT]
> **Independencia Total de MASTER_SERIES_PACKAGE:**
> Este proyecto opera de forma 100% aislada dentro del directorio `TIKTOK_RADAR/`. No comparte personajes, referencias, audios ni archivos con `MASTER_SERIES_PACKAGE`.

---

## 1. Principios del Nuevo Enfoque (Noticiero 3D)

1. **Formato:** *News Explainer* vertical de 25 a 35 segundos. Responde a la necesidad del espectador de enterarse al grano, con datos claros, rigurosos y visuales cinematográficos.
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
   - **Montaje en Edición:** Cada plano se recorta entre **2,0 y 3,5 segundos**, manteniendo el ritmo ágil de TikTok/Reels.
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
