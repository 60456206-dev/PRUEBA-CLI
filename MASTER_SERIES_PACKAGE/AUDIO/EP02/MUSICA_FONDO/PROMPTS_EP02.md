# EP02 · Prompts musicales de producción

**Preparados, no ejecutados.** Para compositor o herramienta de música instrumental; no usar el modelo TTS de personajes. La sincronización final se resuelve contra imagen en edición.

## M01 · Escuchar para conservar — principal

```text
Compón una pieza instrumental original para un thriller sobrenatural íntimo. Una mujer comprende que la voz de su hermana muerta no le responde; decide grabarla para conservar una prueba. La música debe acompañar el cambio de una esperanza que se apaga a una atención precisa, sin sentimentalismo ni anuncio de peligro inmediato.

Entrega objetivo: 10 segundos. Los primeros 7 segundos forman el arco utilizable y los últimos 3 sirven como margen de cola. Entrada suave desde casi silencio. Durante los primeros 2 segundos, una textura frágil; entre los segundos 2 y 5, estabiliza lentamente una disonancia estrecha, como una decisión que se afirma. Entre 5 y 7, retira toda la energía de forma natural. Después del segundo 7 no introduzcas nuevos eventos. No resuelvas el acorde.

Paleta pequeña: cuerda medio-grave frotada con delicadeza, armónicos opacos y una capa tonal granulada tenue. Sonido algo seco, cercano y contenido. Presencia en altavoz pequeño, sin depender de subgraves. Sin melodía cantable, ritmo regular ni percusión. Deja espacio espectral para voces femeninas y para un pequeño botón de grabadora que se añadirá en otra pista.

No generes palabras, susurros, respiraciones, coros ni voz humana. Tampoco golpes, arrastres metálicos, agua, clics, ruido de cinta, reloj o sonido ambiente: estos elementos pertenecen a la evidencia narrativa y se montan por separado. Evita impactos de tráiler, subida de terror, latidos, melodía triste y final triunfal.

La pieza debe sugerir concentración ante algo imposible, no una respuesta del fantasma. Composición original, sin imitar artistas ni bandas sonoras concretas. Entrega con dinámica natural, margen de mezcla y sin limitador agresivo.
```

**Conformado:** arco local 0–7 s → 9,500–16,500 s del episodio. Terminar toda cola antes de 16,500 s; el nuevo contacto con la sal se presenta desde 17 s sin música. No sincronizar un ataque musical con el botón de grabación.

## M02 · La discrepancia — opcional

```text
Crea una textura instrumental original breve para pasar de una comprobación acústica a un documento que la contradice. Debe expresar una duda precisa, no revelar una conspiración ni resolver una emoción.

Entrega objetivo: 4 segundos. Un único gesto suave de aproximadamente 1,25 segundos desde el comienzo, seguido solo de margen de cola. Armónico opaco, seco y tenue, coherente con cuerda frotada delicada. Sin ataque percusivo ni crescendo; aparición y desaparición naturales, sin nota conclusiva. No añadas un segundo gesto.

No incluyas voces, murmullos, respiraciones, coros, reloj, golpes, metal arrastrado, sonidos de grabadora o ambiente. Nada que pueda confundirse con una nueva evidencia. Sin melodía, compás marcado, sentimentalismo ni impacto final. Composición original, sin referencias a obras o artistas específicos. Conserva margen de mezcla y una salida limpia.
```

**Conformado:** ventana máxima 42,250–43,500 s, incluida toda cola. La lectura del informe desde 44 s tiene prioridad. Si el gesto no funciona sin invadir esa lectura, omitirlo y conservar ambiente.

## Corrección única por cue

Primero escuchar la toma y compararla con la escena. Mantener el prompt original y añadir solo una observación verificable:

```text
Conserva la intención y paleta del cue [M01/M02]. En la primera versión ocurrió [defecto concreto y momento]. Corrige [acción específica: retirar ataque, eliminar textura vocal, reducir densidad o facilitar salida]. No añadas instrumentos ni cambies el arco para compensar. Mantén todas las exclusiones y el margen de mezcla del encargo inicial.
```

Máximo dos intentos por cue: primera versión y una corrección. No confundir salida generada con música revisada o aceptada. Registrar resultados y concesiones.
