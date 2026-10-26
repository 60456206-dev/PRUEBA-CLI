# Engranajes · V3 frontal · propuesta actual

Abrir `VISTA_PREVIA.html` o `ENGRANAJES_INTRO_V3.svg`. Lienzo móvil 1080×1920, 9:16, autónomo y vectorial. Regenerar con `python3 ANIMACIONES_SVG/crear_svg_frontal.py`.

- Ruedas frontales de hielo azul y metal ámbar, giro opuesto. Diseño gráfico nuevo: no conserva el acabado fotográfico/cristal volumétrico del PNG. V1, V2 y referencia conservadas.
- Aceleración angular constante por ciclo: θ=360(t/4)² y −450(t/4)² grados, 0≤t≤4 s. A 2 s recorren 90° y −112,5°. Se reinicia la velocidad cada 4 s; no es aceleración ilimitada ni velocidad constante.
- Estelas estilizadas de vapor: rotación vinculada a cada rueda, desplazamiento y opacidad animados con turbulencia. No simulación física de hielo seco.
- Cámara con acercamiento suave del 4 % en bucle de 12 s. Preferencia de movimiento reducido: ruedas estáticas y sin estelas animadas.
- Revisadas capturas Chromium a 390×693 en 0/2 s: ambas ruedas completas, frontales, cambio de orientación y estelas visibles. Más gráfico y menos realista que V2; pendiente aceptación y prueba en teléfono físico.

---

# Engranajes · propuesta V2 · móvil

Abrir `VISTA_PREVIA.html` o directamente `ENGRANAJES_INTRO_V2.svg` en navegador. El SVG es autónomo, sin peticiones externas; PNG original integrado (no vectorización pura). Referencia original intacta.

- Lienzo 1080 × 1920 (9:16), fondo #000000. Composición original centrada con más aire vertical. V1 conservada.
- Cámara: zoom 1 → 1,04 → 1 y desplazamiento leve hacia arriba en 12 s. Cada trayecto acelera y desacelera con curva cúbica (.42, 0, .58, 1); bucle sin salto. Movimiento reducido desactiva también la cámara.
- Saturación SVG 1,38 y ajuste leve del negro; conserva cristal, ámbar y vapor original.
- Entrada de 0,25 s desde 65 % de opacidad; cámara de 12 s y giro de 4 s (3 veces más rápido). Giro de ida y vuelta: cristal ±9°, metal ±12°, sentidos opuestos. No giro continuo de 360° ni simulación mecánica 3D.
- Vapor mediante turbulencia/desplazamiento, máscaras protectoras y reflejos suaves.
- Preferencia de movimiento reducido: imagen estática. La vista previa permite pausar SMIL y reiniciar; la entrada CSS inicial termina independientemente de la pausa.
- Regenerar con `python3 ANIMACIONES_SVG/crear_svg.py` desde raíz. No requiere paquetes externos.

Revisión anterior V1: capturas Chromium en 0, 3, 6 y 12 s; inspección visual de posiciones extremas. Conserva detalles y composición; suavidad/ligera duplicación periférica al mover recortes sobre el fondo original. El vapor ante el centro de las ruedas se mueve junto a su capa. Es una propuesta pendiente de aceptación; no integrada aún en una aplicación. Rendimiento móvil y otros navegadores no comprobados.

Documentación técnica consultada:
- https://developer.mozilla.org/en-US/docs/Web/SVG/Reference/Element/feTurbulence
- https://developer.mozilla.org/en-US/docs/Web/SVG/Reference/Element/feDisplacementMap

Revisión V2: XML correcto y capturas Chromium a 390×693 en inicio y máximo acercamiento (0/6 s). Ruedas completas y más margen vertical negro; persisten bordes suaves/duplicados del giro por capas. Pendiente aceptación y prueba en teléfono físico.

Ajuste para atención de 2 s: recorrido visible de 18°/24° en sentidos opuestos durante los primeros 2 s. Se oculta la copia fija bajo las ruedas para evitar doble rueda. Revisados inicio y 2 s en Chromium móvil: movimiento mayor y ruedas completas, con huecos oscuros visibles en algunos dientes por el recorte del PNG; no es engranaje 3D reconstruido.
