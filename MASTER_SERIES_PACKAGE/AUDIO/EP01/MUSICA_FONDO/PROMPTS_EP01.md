# EP01 · Prompts de producción musical

**Preparados, no ejecutados.** Destino: herramienta de composición instrumental o compositor. No enviar estos prompts a la API TTS de personajes. Las instrucciones de tiempos son objetivos; la conformidad final se obtiene editando contra imagen.

## M01 · Memoria bajo llave — cue principal

```text
Compón una pieza instrumental original para una escena de thriller sobrenatural íntimo. En un archivo silencioso, una madre oculta una llave mientras su hija intenta comprender por qué un abrigo vacío parece respirar. La emoción central es un secreto reconocido y reprimido: tensión sobria, humana y frágil, sin convertir a la madre en una villana caricaturesca.

Duración objetivo de entrega: 12 segundos. Los primeros 9 segundos deben formar un arco utilizable; los 3 restantes son margen de cola para edición. Empieza con una entrada suave, nunca con un impacto. En los primeros 4 segundos, deja mucho espacio para una frase hablada. Entre los segundos locales 4 y 7, aumenta lentamente la presión mediante densidad y una disonancia estrecha, no mediante un salto de volumen. Entre 7 y 9, disuelve la textura sin resolver el acorde. Ningún evento musical nuevo después del segundo 9; solo cola si resulta necesaria.

Usa una paleta muy pequeña: cuerda grave frotada delicadamente, armónicos opacos y una textura tonal granulada casi inmóvil. Debe conservar presencia en altavoz pequeño sin apoyarse solo en subgraves. Sin melodía protagonista, sin compás marcado, sin percusión, sin ostinato rítmico. Mantén el centro espectral despejado para voces femeninas y evita resonancias agudas penetrantes.

La música expresa sospecha, no un hecho sobrenatural nuevo. No incluyas respiraciones, palabras, murmullos, coros, pasos, agua, llave, golpes ni arrastre metálico: esos sonidos pertenecen a pistas narrativas separadas. Sin sonido de archivo ni ambiente grabado en esta pista musical.

Entrega solo la música, con dinámica natural y margen de mezcla. No imites una banda sonora existente ni a un compositor concreto. Evita fanfarrias, golpes de tráiler, subidas de terror, latidos, reloj, melodía sentimental y final triunfal. La impresión final debe ser una pregunta que queda suspendida, no un anuncio de susto.
```

**Nota de montaje:** alinear el arco local 0–9 s con 12,500–21,500 s de V2. Usar los márgenes para conseguir una retirada natural; ninguna cola puede invadir 21,500 s. La entrada de Mara a 22,000 debe quedar aislada de música.

## M02 · Nombre suspendido — recurso opcional

```text
Crea una textura musical instrumental original muy breve, coherente con una cuerda frotada delicada y armónicos opacos de thriller íntimo. No es un golpe de transición ni un efecto de terror: es un único armónico ambiguo que aparece con suavidad, permanece apenas un instante y desaparece sin resolver.

Duración de entrega objetivo: 4 segundos, con un gesto principal de aproximadamente 1,5 segundos desde el inicio y el resto reservado como margen de cola. No agregues una segunda nota, melodía, pulso o nuevo ataque después del gesto. Volumen contenido, sin crescendo enfático. Debe poder retirarse por completo antes de una frase hablada que revela un nombre.

Solo música: sin voces, respiraciones, coros, susurros, impactos, ruido ambiental, agua o metal golpeado. Mantén la textura pequeña, humana y discreta; evita sentimentalismo, épica y resolución armónica. No imites obras ni artistas específicos. Entrega con margen de nivel, sin masterización agresiva.
```

**Nota de montaje:** usar únicamente si sostiene la espera sin anticipar la emoción. Ventana máxima 31,000–32,500 s, incluida toda cola. Si no funciona dentro de esa ventana, omitir M02; no desplazar “Es Mara” para acomodar la música.

## Plantilla de única corrección

Tras escuchar y comparar con imagen, describir un defecto concreto; no regenerar por preferencias vagas. Conservar el prompt original y añadir:

```text
Conserva la paleta y la intención del cue [M01/M02]. Corrige únicamente este problema observado: [describir defecto y momento]. La versión anterior [tapaba el diálogo / introducía una voz / tenía un ataque demasiado fuerte / no dejaba una salida limpia]. En esta corrección, [indicación concreta]. Mantén el arco, las exclusiones y el margen de mezcla del encargo original. No añadas nuevos instrumentos para compensar.
```

Máximo dos intentos por cue, incluida esa corrección. Registrar lo que realmente se obtuvo y sus concesiones. Un archivo generado no equivale a una pieza revisada o aceptada.
