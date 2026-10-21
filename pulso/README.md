# PULSO

Juego de ritmo para música local. Analiza los ataques del audio y crea una partida de cuatro carriles con teclado y controles táctiles. Incluye una pista electrónica original, sintetizada en el navegador.

## Abrir en local

Desde esta carpeta, ejecuta `npm start` y abre `http://localhost:4173`. Solo hace falta Python 3; no hay paquetes que instalar. También puedes ejecutar `python3 -m http.server 4173 --directory dist`.

## Jugar

1. Arrastra una canción o pulsa **Explorar archivos**. También puedes probar **Neon Afterhours**.
2. Elige Suave, Normal o Intenso y empieza la sesión.
3. Pulsa **D, F, J, K** o los botones táctiles cuando las notas alcancen la línea.
4. Usa **Espacio** para pausar o continuar. Los récords se guardan por canción y dificultad en este navegador.

El ajuste de sincronización permite desplazar las notas ±250 ms. Un valor positivo retrasa la llegada de las notas respecto al audio. Las preferencias de volumen y sincronización se conservan localmente.

## Audio y privacidad

Los archivos se decodifican con Web Audio y se procesan en el dispositivo: la aplicación no sube canciones ni realiza solicitudes de red para analizarlas. Acepta los formatos que pueda decodificar tu navegador, habitualmente MP3, WAV, OGG, M4A y FLAC. Límite: 100 MB, entre 4 segundos y 12 minutos. Un archivo silencioso o sin suficientes ataques muestra un mensaje para elegir otro.

El detector usa cambios de energía en bandas de frecuencia. Las notas siguen los ataques medidos; el BPM mostrado es una estimación. Las canciones con percusión clara suelen dar mejores mapas. El contenido musical, Bluetooth y la latencia del dispositivo pueden requerir ajustar la sincronización.

## Comprobar

`npm test` verifica el detector con silencio, pulsos conocidos, ritmos variables, estéreo en contrafase, las dificultades y la demo. `npm run check` comprueba la sintaxis JavaScript. No se requiere compilación: `dist/` contiene la aplicación completa.
