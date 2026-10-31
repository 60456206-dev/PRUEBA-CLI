# Montaje y Postproducción Profesional V3 · Epidemic Sound Edition (`EP01` a `EP06`) · 2026-10-31

Generado conectando directamente con el servidor oficial **Epidemic Sound MCP API (`https://www.epidemicsound.com/a/mcp-service/mcp`)** mediante la suscripción de paga (`EPIDEMIC_SOUND`), reemplazando por completo los sonidos sintéticos por **activos reales de estudio en WAV** (tanto música por stems como efectos de sonido y foley) y aplicando un rediseño integral de **gancho para redes sociales (0–2,5 s)**, **encuadre dinámico a 24 fps** y **subtítulos ASS nativos en zona segura**.

---

## 1. Resumen Técnico de Másters `AJUSTADO_V3` (`1080×1920`, 24 fps, AAC 192 kbps)

| Episodio | Archivo Máster V3 | Subtítulos ASS / SRT | Hoja de Contacto | Duración (V2 → V3) | Sonoridad Integrada | True Peak | Estado |
| :--- | :--- | :--- | :--- | :---: | :---: | :---: | :---: |
| **EP01** | `FINAL/EP01_AJUSTADO_V3.mp4` | `EP01_AJUSTADO_V3.{ass,srt}` | `EP01_AJUSTADO_V3_CONTACT.png` | 35,25 s → **28,75 s** | `-15,4 LUFS` | `-1,05 dBTP` | `DECODE_OK` |
| **EP02** | `FINAL/EP02_AJUSTADO_V3.mp4` | `EP02_AJUSTADO_V3.{ass,srt}` | `EP02_AJUSTADO_V3_CONTACT.png` | 40,00 s → **36,50 s** | `-16,0 LUFS` | `-1,19 dBTP` | `DECODE_OK` |
| **EP03** | `FINAL/EP03_AJUSTADO_V3.mp4` | `EP03_AJUSTADO_V3.{ass,srt}` | `EP03_AJUSTADO_V3_CONTACT.png` | 38,25 s → **33,75 s** | `-15,6 LUFS` | `-1,09 dBTP` | `DECODE_OK` |
| **EP04** | `FINAL/EP04_AJUSTADO_V3.mp4` | `EP04_AJUSTADO_V3.{ass,srt}` | `EP04_AJUSTADO_V3_CONTACT.png` | 40,50 s → **36,00 s** | `-15,3 LUFS` | `-1,14 dBTP` | `DECODE_OK` |
| **EP05** | `FINAL/EP05_AJUSTADO_V3.mp4` | `EP05_AJUSTADO_V3.{ass,srt}` | `EP05_AJUSTADO_V3_CONTACT.png` | 37,50 s → **33,75 s** | `-15,9 LUFS` | `-1,05 dBTP` | `DECODE_OK` |
| **EP06** | `FINAL/EP06_AJUSTADO_V3.mp4` | `EP06_AJUSTADO_V3.{ass,srt}` | `EP06_AJUSTADO_V3_CONTACT.png` | 45,00 s → **41,75 s** | `-15,4 LUFS` | `-1,10 dBTP` | `DECODE_OK` |

---

## 2. Catálogo Real WAV Descargado de Epidemic Sound (`AUDIO/EPIDEMIC_SOUND/`)

Documentado en `MASTER_SERIES_PACKAGE/AUDIO/EPIDEMIC_SOUND/catalog_manifest.json`:

### A. Pistas Musicales por Stems (`WAV` 48 kHz)
- **`ORO_INSTRUMENTS.wav` & `ORO_BASS.wav`** — *Oro* (**Hanna Ekström & Anna Dager**): cuerdas graves frotadas (chelo/violín) de thriller íntimo.
- **`CREEPING_ANXIETY_INSTRUMENTS.wav` & `CREEPING_ANXIETY_BASS.wav`** — *Creeping Anxiety* (**Anna Dager & Hanna Ekström**): tensión psicológica en cuerdas y subgrave.
- **`DONT_TURN_AROUND_INSTRUMENTS.wav`** — *Don't Turn Around* (**Belladonna Strings**): armónicos opacos en suspensión.
- **`SHIFTING_GROUND_INSTRUMENTS.wav` & `SHIFTING_GROUND_BASS.wav`** — *Shifting Ground* (**Luba Hilman**): drone oscuro sin percusión.
- **`DARK_PUZZLE_INSTRUMENTS.wav`** — *Dark Puzzle* (**Anna Dager & Hanna Ekström**): fricción armónica de investigación.
- **`DISTURBING_EVIDENCE_INSTRUMENTS.wav`** — *Disturbing Evidence* (**Stefan Ekström**): tensión contenida para revelaciones documentales.

### B. Efectos de Sonido y Foley de Estudio (`WAV` 48 kHz)
- **`ROOM_BASEMENT.wav`**: ambiente real de sótano/archivo de hormigón con resonancia grave continua.
- **`FOLEY_COAT_THICK.wav` & `FOLEY_COAT_FLAP.wav`**: movimiento real de abrigo pesado de lana gruesa.
- **`SFX_WATER_DROP_SINGLE.wav` & `SFX_WATER_DROP_CLOTH.wav`**: impacto macro de gota de agua sobre tela húmeda.
- **`FOLEY_KEYS_HAND.wav`**: manipulación y roce metálico de llave antigua de hierro en palma y sobre mesa.
- **`SFX_FLOODGATE_HIT.wav`, `SFX_FLOODGATE_BOOM.wav` & `SFX_FLOODGATE_SCRAPE.wav`**: dos golpes metálicos reverberantes + arrastre pesado de compuerta para `EP02_SH05` y su reproducción filtrada por altavoz en `EP02_SH06`.
- **`SFX_RECORDER_BUTTONS.wav`**: clic mecánico real de grabadora portátil (Sun Ace Portable BOT 450).
- **`FOLEY_PAPER_TURN.wav`**: roce de pliego de papel grueso para las tomas del informe de evacuación.
- **`SFX_RISER_LOW.wav`, `SFX_RUMBLE_RISING.wav` & `SFX_DARK_BOOM.wav`**: *risers* y pulsos subgraves cinematográficos para el gancho de 0–2,5 s y los cierres en *cliffhanger*.
- **`SFX_UI_CONFIRM.wav`**: confirmación sutil para «Informe enviado» en `EP06_SH05`.

---

## 3. Mejoras de Gancho, Encuadre y Estilo para Redes Sociales

1. **Gancho Inmediato en 0,0–2,5 s (Retención en TikTok / Reels / Shorts)**:
   - Se eliminaron las esperas mudas de apertura (en `EP01` la primera frase pasa de `6,00 s` a `3,00 s`; en `EP03` de `4,05 s` a `2,85 s`; en `EP04` de `4,20 s` a `2,80 s`).
   - Cada episodio abre en `t = 0,00 s` con un pulso subgrave + *riser* de Epidemic Sound, acción acústica diegética inmediata (respiración de Mara en la lana, gota sobre sal, llave de hierro sobre el plano, apertura de palma, pliego del acta o clic de grabadora) y un micro-rótulo editorial superior (`ARCHIVO NORTE · EPISODIO X`) que se desvanece suavemente a los `2,45 s`.
2. **Encuadre Dinámico Subpíxel (`zoompan` 24 fps con supermuestreo `1620×2880 → 1080×1920`)**:
   - Todos los planos cuentan con movimiento óptico orgánico (*push-in* en primeros planos dramáticos, *macro-in* en gota/llave/grabadora y *pull-back* en revelaciones generales), más etalonaje de thriller (`contrast=1.045, saturation=1.04, vignette=PI/6, unsharp` adaptativo).
3. **Subtítulos ASS Nativos (`PlayRes: 1080×1920`) con 0 % de Solapamiento en Firmas**:
   - Corregido el solapamiento que ocurría en `V2` sobre `"Conformidad: Inés Vidal"` y la firma manuscrita *«Inés Vidal»* en `EP04_SH08` y `EP05_SH01`. En `V3`, el encuadre `doc_frame` desplaza ligeramente el documento hacia el tercio medio-superior y el estilo `DocSafe` posiciona el subtítulo en la madera oscura inferior debajo del borde del papel/móvil, dejando el 100 % del documento y la firma completamente despejados.
