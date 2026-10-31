# Revisión y Montaje Profesional · EP02 a EP06 (AJUSTADO_V2) · 2026-10-31

Generado por instrucción del usuario aplicando el paquete completo de montaje profesional (`Picture Lock` + Voces TTS + Foley/Ambiente/SFX + Mezcla EBU R128 `-16 LUFS` + Subtítulos quemados + Ajuste de color/contraste y ritmo dinámico) sobre los episodios **EP02 a EP06**, homologado con `EP01_AJUSTADO_V2.mp4`. Sin música de fondo, según indicación expresa del usuario.

---

## 1. Archivos principales exportados en `MASTER_SERIES_PACKAGE/FINAL/`

| Episodio | Picture Lock (1080×1920, 24 fps, mudo) | Versión Ajustada V2 (1080×1920, 24 fps, AAC + Subtítulos) | Subtítulos SRT | Hoja de Contacto | Duración (Orig. → V2) | Sonoridad Integrada / True Peak |
| :--- | :--- | :--- | :--- | :--- | :---: | :---: |
| **EP01** | `EP01_PICTURE_LOCK.mp4` | `EP01_AJUSTADO_V2.mp4` | `EP01_AJUSTADO_V2.srt` | — | 51,0 s → **35,25 s** | `-16,0 LUFS` / `-2,25 dBTP` |
| **EP02** | `EP02_PICTURE_LOCK.mp4` | `EP02_AJUSTADO_V2.mp4` | `EP02_AJUSTADO_V2.srt` | `EP02_AJUSTADO_V2_CONTACT.png` | 52,0 s → **40,00 s** | `-17,2 LUFS` / `-2,33 dBTP` |
| **EP03** | `EP03_PICTURE_LOCK.mp4` | `EP03_AJUSTADO_V2.mp4` | `EP03_AJUSTADO_V2.srt` | `EP03_AJUSTADO_V2_CONTACT.png` | 53,0 s → **38,25 s** | `-16,7 LUFS` / `-2,25 dBTP` |
| **EP04** | `EP04_PICTURE_LOCK.mp4` | `EP04_AJUSTADO_V2.mp4` | `EP04_AJUSTADO_V2.srt` | `EP04_AJUSTADO_V2_CONTACT.png` | 55,0 s → **40,50 s** | `-16,6 LUFS` / `-2,26 dBTP` |
| **EP05** | `EP05_PICTURE_LOCK.mp4` | `EP05_AJUSTADO_V2.mp4` | `EP05_AJUSTADO_V2.srt` | `EP05_AJUSTADO_V2_CONTACT.png` | 53,0 s → **37,50 s** | `-17,2 LUFS` / `-2,29 dBTP` |
| **EP06** | `EP06_PICTURE_LOCK.mp4` | `EP06_AJUSTADO_V2.mp4` | `EP06_AJUSTADO_V2.srt` | `EP06_AJUSTADO_V2_CONTACT.png` | 54,0 s → **45,00 s** | `-16,9 LUFS` / `-2,34 dBTP` |

---

## 2. Mejoras editoriales y sonoras ejecutadas por episodio

- **EP02 («El duplicado», 40,00 s):**
  - Generadas las voces TTS de Inés (`Kore`), Alba (`Gacrux`) y Mara (`Vindemiatrix`).
  - Cumplida la regla de `EP02_SOUND_DESIGN.md`: en `SH06` (`L04`) se reutiliza exactamente la misma toma de `L03` y la misma muestra del motivo de compuerta (`SH05`: dos golpes metálicos y arrastre), procesadas con filtro de altavoz de grabadora (`320–3400 Hz`) para contrastar la emisión desde la tela frente a la reproducción digital.
- **EP03 («El registro», 38,25 s):**
  - En `SH04` se recortó el tramo `19,50–24,25 s` omitiendo el primer segundo y medio donde Inés tenía los labios entreabiertos.
  - En `SH06` se recortó el tramo `32,50–38,50 s`, **eliminando por completo la intrusión de manos de `0,3–1,4 s`** documentada en la tarjeta del plano y dejando únicamente el abrigo vacío e inmóvil durante la súplica de Mara.
- **EP04 («La otra hija», 40,50 s):**
  - En `SH01` se inicia en `1,25 s` directamente sobre la apertura limpia de la palma revelando la llave.
  - En `SH07` se cierra el plano en `45,00 s` (4,0 s locales), **eliminando el levantamiento final de mirada de Alba a partir de `5,25 s`** para mantener su vista baja hacia el informe antes del corte al acta firmada en `SH08`.
- **EP05 («La compuerta», 37,50 s):**
  - Ritmo compacto entre la lectura de la firma (`SH01`), la admisión de Inés (`SH02`), la tentación del recorte en el móvil (`SH03`), la última gota en Estado S3 (`SH05`), el mensaje colectivo de Mara (`SH06`) y la disolución final hacia Estado S4 (`SH08`).
- **EP06 («Los siete», 45,00 s):**
  - Se ajustaron las pausas internas de `L01` a `0,35 s` entre nombres para que los cuatro primeros nombres encajen con naturalidad dentro de `SH01`.
  - Para `L06` (`SH07`, playback «Y yo, Mara Vidal.») se extrajo directamente la cláusula final de `L02` (`SH02`) con procesado de altavoz de grabadora, garantizando continuidad diegética absoluta.
  - En `SH05` se seleccionó la ventana `28,75–33,00 s` para mostrar tanto el giro del spinner como la confirmación «Informe enviado» con checkmark verde.
- **Tipografía de subtítulos (`FontSize=14, MarginV=28`):**
  - Refinada a 1–2 líneas en el tercio inferior para que ninguna línea tape la firma manuscrita *«Inés Vidal»* en `EP04_SH08` / `EP05_SH01` ni la grabadora sobre la mesa.

---

## 3. Verificación técnica y recomendación

- Decodificación completa (`ffmpeg -v error -f null -`) superada sin ningún error (`DECODE_OK`) en los 6 `PICTURE_LOCK.mp4` y en los 6 `AJUSTADO_V2.mp4`.
- Stems individuales (`DIALOGUE`, `ROOM`, `FOLEY`, `SFX`), tomas crudas (`TAKES/`), tomas editadas (`EDITADOS/`) y manifiestos (`AJUSTE_V2/montaje.json`) archivados en `MASTER_SERIES_PACKAGE/AUDIO/EP02/` a `EP06/`.
- **Recomendación:** **CONSERVAR Y OFICIALIZAR** la colección `EP01_AJUSTADO_V2.mp4` a `EP06_AJUSTADO_V2.mp4` como montaje maestro de la Temporada 1 (sin música), quedando listos para escucha final del usuario o para una futura capa musical opcional si se desea añadir más adelante.
