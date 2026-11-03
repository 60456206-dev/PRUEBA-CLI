# TikTok Radar · Fórmulas Maestras de Prompts (Animación 3D Estilizada y Locución)

Guía técnica y de ingeniería de prompts para generar el formato **Noticiero Ágil / Explainer 3D** en TikTok Radar.

---

## 1. La Regla de Oro: Duración y Velocidad por Plano

### ¿Por qué NO generar planos de 10 segundos en la IA?
1. **Riesgo de Morfeo y Deformación:** Los modelos de vídeo generativo (Kling 1.5, Wan 2.1, Google Flow, Minimax) mantienen consistencia física durante los primeros 3 a 5 segundos. A partir del segundo 5 o 6, el movimiento suele deformarse (manos que se funden, objetos que mutan o rostros que se distorsionan).
2. **Tiempo de Generación y Colas:** Un plano de 10 segundos tarda el triple de tiempo en procesarse en la GPU que uno de 5 segundos. En un flujo donde el objetivo es publicar en **menos de 1 hora**, no podemos permitirnos esperas de 20 minutos por clip ni reprocesar fallos largos.
3. **Retención de Audiencia en TikTok:** En redes verticales, mantener un mismo encuadre estático por 10 segundos destruye el *watch time*. El cerebro del espectador moderno exige un nuevo estímulo visual cada **2 a 3.5 segundos** (corte seco, cambio de ángulo o zoom in).

> [!TIP]
> **Estándar Técnico de TikTok Radar (Monetización >60 s):**
> - **Generación en IA:** Clips de **4 a 5 segundos** (máximo 6 segundos). Tasa de acierto >95%, renderizado ultrarrápido y movimiento limpio.
> - **Corte en Montaje Final:** Ventanas activas de **2,5 a 4,0 segundos** por plano, encadenando 12 a 15 planos cortos para alcanzar los **61 a 65 segundos** requeridos para monetizar en TikTok sin provocar fatiga visual.

---

## 2. Estilo Visual: Animación 3D Estilizada (Cero Hiperrealismo)

Para evitar el «efecto valle inquietante» (*uncanny valley*) de los humanos hiperrealistas de IA con piel plástica y expresiones muertas, TikTok Radar adopta la estética **Stylized 3D Cinematics** (inspirada en la dirección de arte de *Arcane*, *Spider-Verse*, *Love Death + Robots* y la animación cinematográfica moderna):

### Descriptores Clave Positivos:
* `modern stylized 3D animation, expressive character design with distinct facial acting`
* `tactile textures, soft subsurface scattering, subtle stylized skin detail without photo-realism`
* `dramatic cinematic volumetric lighting, atmospheric fog, rim lights, high contrast chiaroscuro`
* `octane render aesthetic, Unreal Engine 5 stylized cinematic, 9:16 vertical composition`

### Descriptores Negativos Obligatorios:
* `photorealistic, uncanny valley, real human photograph, glossy plastic skin, extra fingers, distorted face, anatomical glitches, flat lighting`

---

## 3. Fórmulas de Prompts Visuales

### Fórmula A: Recreación Dramática con Personajes (Ej. Tensión en Cabina de Piloto)
```text
Vertical 9:16, modern stylized 3D cinematic animation, Arcane and Pixar thriller aesthetic. Close-up inside an airplane cockpit at night. A stylized airline pilot with sweat on his brow and wide, focused eyes grips the control yoke with two firm hands. Red emergency dashboard warning lights flash and reflect off his face and the cockpit glass. Outside the windshield, dark turbulent clouds and rain streak by. Smooth physical character movement as he pulls back on the controls with controlled desperation, mouth set firmly, chest breathing rapidly. Volumetric rim lighting, rich cinematic shadows, high octane render style. No photorealism, no uncanny valley, completely animated.
```

### Fórmula B: Simulación de Sucesos y Eventos Físicos (Ej. Descenso de Aeronave / Radar)
```text
Vertical 9:16, dramatic 3D stylized simulation cinematic. Low-angle dynamic tracking shot of a sleek private twin-engine jet descending steeply through storm clouds over the Florida coastline at twilight. Glowing amber wingtip lights and navigation beacons cut through the mist. Rain streaks whipped by intense wind. Smooth steady camera tracking the descending aircraft trajectory with cinematic weight and physics. 3D altitude HUD telemetry lines faintly superimposed in deep green. Photorealistic lighting on stylized 3D geometry, high tension atmosphere.
```

### Fórmula C: Infografía 3D Cinemática y Noticias Abstractas (Sin Personajes)
Para noticias de ciberseguridad, inteligencia artificial, leyes o tecnología donde no aplican personas:
```text
Vertical 9:16, stylized 3D tech explainer animation. A high-tech server rack chamber bathed in dark cyan and emergency amber lighting. Stylized glowing fiber-optic cables pulse with data streams. A holographic 3D document floats in mid-air, with headlines dissolving into illuminated digital particles. Slow dramatic push-in camera movement, suspended dust motes catching volumetric god-rays, sleek minimalist 3D rendering. High visual retention, clean editorial aesthetic.
```

---

## 4. Dirección de Locución y Guión Periodístico

### Perfil del Narrador
* **Arquetipo:** Locutor periodístico de investigación / Breaking news con tono urgente, sobrio y magnético.
* **Cadencia:** 130 a 145 palabras por minuto (ritmo firme y dinámico, sin sonar atropellado ni aburrido).
* **Entonación:** Modulación enfática en los ganchos y datos clave, con micropausas dramáticas de 0.25 a 0.40 s antes de las revelaciones.

### Estructura del Guión Monetizable (61–65 Segundos / 130–145 Palabras)
1. **0–3 s (Gancho de Curiosidad):** Pregunta o afirmación disruptiva que activa la retención.
2. **3–14 s (Hecho Oficial):** Qué ocurrió con datos contrastados de agencias oficiales.
3. **14–38 s (La Recreación Dramática):** La tensión en cabina, las decisiones humanas y la simulación física del suceso.
4. **38–52 s (Datos Técnicos y Cajas Negras):** Lo que revelan los radares y registros de vuelo.
5. **52–63 s (Cierre y Pregunta de Debate):** Hipótesis abierta y llamado a la acción para comentarios.
