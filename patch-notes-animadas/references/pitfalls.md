# Errores de este formato

Complementa `huashu-design/references/animation-pitfalls.md`, que cubre la
animación en general. Aquí van los específicos de **patch notes = artifact +
MP4 sobre capturas reales**. Todos ocurrieron de verdad en el primer vídeo
(QuestKeep, PRs #344/#352/#342) y ninguno lanzó un error: se ven, o no te
enteras.

## 1 · El primer fotograma en negro es la miniatura de WhatsApp

**Qué pasó.** La animación abría con la pantalla apareciendo desde opacidad 0.
El fotograma 0 salía negro y WhatsApp lo usaba de portada: parecía un vídeo roto
antes de que nadie le diera al play.

**Regla.** El fotograma 0 es el estado inicial **completo**. Si quieres sensación
de aterrizaje, anima el desenfoque o la escala — **no la opacidad desde 0**.

Y con el desenfoque, poco: a 7 px el primer fotograma se leía como "foto movida".
2–3 px se sienten intencionados.

```js
// mal: frame 0 vacío
stage.style.opacity = E.expoOut(seg(t, .15, 1.1));
// bien: ya está ahí, sólo se asienta
stage.style.opacity = 1;
stage.style.filter = `blur(${(1 - E.expoOut(seg(t, 0, .9))) * 2.5}px)`;
```

Se comprueba en `_verify/primero.png`.

## 2 · El chrome se esconde desde el HTML, no desde el grabador

**Qué pasó.** El grabador inyectaba `#chrome{display:none}` con `addInitScript`
usando un listener de `DOMContentLoaded`. Llegó tarde: la barra de controles
salió en los primeros fotogramas del MP4.

**Regla.** El HTML se esconde **a sí mismo** leyendo `window.__recording`, que el
grabador pone con `addInitScript` antes de cualquier script de la página. Sin
carreras.

```js
if (window.__recording) $('chrome').style.display = 'none';
```

## 3 · El lienzo se ancla en la esquina; centrar con grid falla

**Qué pasó.** `#fit{display:grid;place-items:center}` con un `#canvas` de
1920×1080 dentro. **Un hijo más grande que su contenedor no queda centrado: se
alinea al inicio.** En el vídeo el lienzo mide exactamente 1920×1080, la escala
es 1 y no se nota. En el panel del artifact la escala baja a ~0.48 y todo el
contenido se va al cuadrante inferior derecho sobre un fondo negro.

Es el peor tipo de fallo: **el vídeo salía perfecto y el artifact estaba roto**,
del mismo archivo.

**Regla.** Con `aspect-ratio` fijo, ancla en la esquina y escala por el ancho.
Exacto, sin centrar y sin casos especiales:

```css
#fit{position:relative;width:100%;aspect-ratio:16/9;overflow:hidden}
#canvas{position:absolute;left:0;top:0;width:1920px;height:1080px;transform-origin:0 0}
```
```js
$('canvas').style.transform = `scale(${box.width / 1920})`;
```

**Prueba siempre el artifact a un ancho distinto del del vídeo.** Reproducir el
envoltorio en local es barato y pilla esto:

```js
const RESET = `<style>body{margin:0}img{max-width:100%}</style>`;
fs.writeFileSync('wrapped.html', `<!doctype html><html><head>${RESET}</head><body>
${fs.readFileSync('patch-notes.html','utf8')}</body></html>`);
// y ábrelo con Playwright a 930px, 1400px y 520px de ancho
```

## 4 · La captura trae su propio estado resaltado

**Qué pasó.** El pie decía «eliges **Ventaja**» mientras la captura del menú
resaltaba «Normal», que era su estado real cuando se capturó. El texto y la
imagen se contradecían en el plano más importante.

**Regla.** Si un pie anuncia una elección, **dibújala** sobre la captura con
`pickRow(rect, k)`. Los rectángulos de las filas salen de `measure()`.

Más en general: **cada afirmación del guion tiene que verse en el cuadro**. Si no
se puede enseñar, cambia la frase.

## 5 · `__seek` debe repintar `time`, no `0`

**Qué pasó.** La plantilla de tick de huashu llama `render(0)` en el primer
frame. Como `__seek` pone `lastTick = null` para reiniciar el reloj, el frame
siguiente entraba por esa rama y repintaba 0 — el salto se perdía. Rompía la
verificación por fotogramas y la corrección defensiva `__seek(0)` del grabador.

**Regla.** `render(time)` en la rama del primer frame. En el arranque `time` ya
es 0, así que no cambia nada; tras un seek, repinta lo correcto.

## 6 · El zoom recorta justo el dato que cita el pie

**Qué pasó.** El pie decía «un 3 que acabó en **26**» y el 26 quedaba fuera del
cuadro: la cámara estaba centrada en los dados, no en la línea entera.

**Regla.** Centra el zoom en el **centro del elemento completo** que estás
citando, no en el detalle, y deja margen. Se ve en la hoja de contactos.

## 7 · Cada data URI repetido son megabytes

Un placeholder se sustituye en **todas** sus apariciones. Repetir `__IMG_X__` en
tres sitios triplica el base64: en el prototipo eran 5.14 MB que bajaron a
3.44 MB declarando cada captura una vez en el mapa `IMG` y asignando los `src`
desde ahí.

Tope duro del artifact: **16 MB**. `build.mjs` avisa al 75% y falla al pasarse.

## 8 · Un vídeo no se corrige; un artifact sí

Una vez que el MP4 circula, no hay forma de arreglarlo: hay que mandar otro y
convivir con el viejo. El artifact republicado con el **mismo `file_path`**
conserva la URL.

Por eso el orden es: **verificar → enseñar → mandar**. Y por eso conviene
entregar los dos: el artifact es la copia corregible del mismo contenido.

## 9 · `ffmpeg` no está en el contenedor

No viene en Claude Code on the web. `scripts/env.mjs` instala `ffmpeg-static`
(~80 MB) la primera vez. Chromium **sí** está, en `/opt/pw-browsers`, y
`playwright install` está prohibido: hay que apuntar al preinstalado.

## Repaso antes de entregar

- [ ] `_verify/primero.png` es el estado inicial completo
- [ ] `_verify/ultimo.png` es el final sostenido, no el arranque
- [ ] sin barra de controles en ningún fotograma
- [ ] el artifact probado a un ancho distinto del del vídeo
- [ ] cada dato citado en un pie se ve en el cuadro
- [ ] texto e imagen dicen lo mismo
- [ ] MP4 por debajo de 16 MB
- [ ] cero `pageerror` en captura y en grabación
