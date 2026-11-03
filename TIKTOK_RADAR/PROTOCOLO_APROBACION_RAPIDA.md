# TikTok Radar · Protocolo de Aprobación Rápida

Sistema estandarizado para consultar decisiones críticas al usuario en un solo bloque estructurado, evitando micro-preguntas o interrupciones innecesarias.

---

## 1. Reglas de Consulta al Usuario

1. **Solo preguntas de impacto real:** No consultar detalles menores de edición, parámetros internos de ffmpeg o ajustes de código que el agente pueda resolver técnicamente. Solo se consulta cuando hay decisiones de:
   - Plataforma o herramienta de vídeo IA a utilizar (Flow, Kling, Wan, etc.).
   - Motor de voz / locución (APIs de pago vs gratuitas).
   - Selección o descarte del titular/tema de la jornada.
2. **Formato con Opción Recomendada:** Cada decisión siempre presenta en primer lugar la opción técnica óptima marcada con `(Recomendado)`.
3. **Respuesta en un solo clic o palabra:** El usuario puede responder simplemente:
   - *«Adelante con lo recomendado»* (aprueba todo el bloque).
   - O indicar las opciones elegidas (ejemplo: *«1A, 2B, 3A»*).

---

## 2. Plantilla de Hoja de Decisión (Ficha Batch)

```markdown
### 📋 Ficha de Decisiones Clave · TikTok Radar

1. **[Tema / Decisión 1]**:
   - [A] (Recomendada) [Descripción de la opción óptima]
   - [B] [Alternativa secundaria]

2. **[Tema / Decisión 2]**:
   - [A] (Recomendada) [Descripción de la opción óptima]
   - [B] [Alternativa secundaria]

*Puedes responder con «Adelante con lo recomendado» para aprobar todo en bloque.*
```
