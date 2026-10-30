# EP01 · Dirección musical y diseño de tensión

**Estado:** brief y prompts preparados; música no generada, no escuchada y no incorporada al render. Alcance exclusivo: EP01. Base de trabajo: `FINAL/EP01_AJUSTADO_V2.mp4`, 35,25 s a 24 fps. No usar los tiempos del montaje antiguo de 51 s.

## Encargo creativo

Construir una tensión íntima que dirija la atención hacia la llave y prepare la aparición de Mara. La música debe sugerir que Alba reconoce un peligro antes de que Inés lo comprenda. La revelación pertenece a la voz y al abrigo: la partitura debe retirarse para que ambos ocupen el primer plano.

La calidad buscada es la de una mezcla dramática cuidada: intención por escena, economía de recursos, continuidad tímbrica y espacio para los actores. No se pide una imitación de una película, compositor o banda sonora concreta. La mejora de retención es una hipótesis editorial, no un resultado garantizado.

## Documentos de producción

- [Mapa de entradas y salidas](CUES_EP01.md): tiempos absolutos de V2, función narrativa y silencios obligatorios.
- [Prompts de composición](PROMPTS_EP01.md): instrucciones completas para compositor o herramienta musical, con exclusiones y entregables.
- Plan activo: [EP01_EDIT_PLAN](../../../EPISODES/EP01/EP01_EDIT_PLAN.md).
- Identidad: [Biblia de la serie](../../../02_SERIES_BIBLE.md), apartado Identidad.

## Identidad sonora

Paleta reducida: cuerda grave frotada con poco cuerpo, armónicos opacos y una textura tonal granulada tenue. Registro medio-grave audible en móvil; no depender de subgraves. Movimiento orgánico, sin compás insistente ni melodía cantable. Una disonancia estrecha puede abrirse gradualmente sin resolver.

Emoción: sospecha contenida, memoria reprimida y fragilidad. Evitar épica, sentimentalismo, horror estridente y el cliché de “susto”. El volumen no sustituye el desarrollo dramático.

Separar funciones: MUSIC expresa tensión; ROOM mantiene el archivo; FOLEY acompaña tela y movimientos; SFX corresponde al agua. La música no debe añadir respiraciones, susurros ni golpes que puedan confundirse con pruebas de la historia. Los dos golpes y el arrastre de compuerta se reservan para su aparición narrativa, no se anticipan como adornos en EP01.

## Entrega e integración futuras

1. Producir primero M01. Máximo dos intentos por cue: primera versión y una corrección si falla; revisar antes de corregir. Este documento no inicia ninguna generación.
2. M02 es un recurso opcional de montaje, no un requisito para completar el episodio. Prioridad: aprobar la función de M01; prescindir de M02 si vuelve obvio el suspense o distrae del nombre de Mara.
3. Guardar fuentes como `EP01_M01_T1.wav` / `EP01_M01_T2.wav`, con prompt efectivo, herramienta, fecha, duración, procedencia y condiciones de uso. No dar por licenciada una salida sin comprobar esas condiciones.
4. Entrega preferida: WAV PCM 24 bits, 48 kHz, sin normalización comercial, sin limitador agresivo y con colas recuperables. Estéreo compatible con mono. Convertir el formato si la herramienta entrega otro; convertir no recupera calidad ausente.
5. Montar un stem `EP01_MUSIC_V3.wav` de **35,25 s exactos**, con silencio fuera de los cues. Si cambia el corte, actualizar primero el mapa y la duración. No se ha creado este WAV todavía.
6. Remezclar desde los stems de `AJUSTE_V2/`; no sumar música al máster ya limitado. DIALOGUE permanece delante. Mantener la música claramente por debajo de la voz, con automatización de volumen y, solo si hace falta, atenuación dinámica suave durante frases. Evitar bombeo.
7. Punto de partida del máster: alrededor de -16 LUFS y techo ≤ -1 dBTP, verificando también el AAC exportado. Son objetivos de este proyecto, no una especificación universal de plataformas. Comprobar la lectura del diálogo en mono, móvil y auriculares.
8. Exportación propuesta con música: `FINAL/EP01_AJUSTADO_V3_MUSICA.mp4`. Conservar V2 para comparar. Ese nombre designa una entrega futura, no un archivo existente ni oficial.

## Criterios de revisión

Comparar V2 y la propuesta musical a volumen percibido equivalente. Revisar si la atención se dirige a la llave, si la retirada musical deja espacio a Mara, si todas las palabras se entienden y si los silencios conservan la tensión. Rechazar música que parezca una nueva voz, tape consonantes o altere el significado de una acción.

Evaluar primero la escucha y la función dramática. Si posteriormente hay datos de publicación, comparar retención por segundo y finalización sin atribuir automáticamente los cambios a la música. No oficializar ni borrar versiones por una evaluación técnica favorable.
