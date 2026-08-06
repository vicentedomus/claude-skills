# Capturar la UI real en cualquier repo

El único trozo verdaderamente específico de cada proyecto. Todo lo demás
(animar, grabar, publicar) es igual en todos.

## Cómo arrancar la app, por orden

### 1 · Harness de tests E2E — la mejor vía con diferencia

Muchos repos con Playwright tienen fixtures que montan una pantalla real con
datos de prueba, sin login ni base de datos de producción:

```bash
ls tests/fixtures/*harness*.html e2e/fixtures/* 2>/dev/null
grep -rl "mount\|render" tests/fixtures/ | head
```

Ventajas: es la UI real, es reproducible, no toca producción y no hay que
inventarse credenciales. Si existe, úsalo.

Mira además un spec que ya lo use: te dice qué globals hay que llamar para
llegar al estado que quieres, y suele traer un doble del backend listo.

```js
// Ejemplo real (QuestKeep): el harness expone globals del creador y monta
// la hoja de personaje con un PJ construido de verdad.
await page.evaluate(() => window.ccOpen());
await page.waitForFunction(() => window.srd5eReady && window.srd5eReady());
const id = await page.evaluate(() => {
  ccSelectClass('Fighter'); ccSetLevel(3); /* … */
  return ccFinish().then(() => window.mountSheet(window.__lastSaved));
});
```

### 2 · Dev server

```bash
npm run dev   # o: npm start, vite, next dev…
# si el proyecto se construye antes:
npm run build && npx serve . --listen 3000
```

Si hace falta login, busca el usuario de pruebas por convención del repo
(`tests/`, `.env.example`, `README`). **Nunca metas credenciales en el HTML ni
en el vídeo.**

### 3 · Deploy — último recurso

Son datos reales. Revisa cada captura antes de publicarla: nombres, correos,
saldos, cualquier cosa que no debería salir. Si aparece algo, cambia de vía en
vez de tapar el pixel.

## Elegir los estados que hay que capturar

Uno por plano del guion. Sirve de guía: por cada afirmación del vídeo, un estado
que la demuestre.

Cuando un panel **cambia de estado** (una lista que crece, un contador que
sube), captura cada paso **con el mismo `clip`** y encadénalos con fundidos
cruzados. Así se ve crecer sin animar tú nada.

```js
const CLIP = { x: 992, y: 539, width: 444, height: 285 };   // el MISMO para los tres
await shoot(page, 'caps/log1.png', CLIP);
await accion1(page);
await shoot(page, 'caps/log2.png', CLIP);
```

Con paneles anclados abajo que crecen hacia arriba, esto encaja solo. Con
paneles anclados arriba, mide el `clip` con el estado MÁS GRANDE y reutilízalo.

## Resolución

En el cuadro se ve una franja de `1920 / (BASE × zoom)` px CSS. Para que llegue
nítida hacen falta ~`BASE × zoom` píxeles por px CSS:

| Zoom máximo del guion | `deviceScaleFactor` |
|---|---|
| ≤ 1.5× (planos generales) | 2 |
| 2–2.5× | 3 |
| 3× o más (zoom a un detalle) | 4 |

`dsfPara(zoom)` en `scripts/capture.mjs` lo calcula. Práctica que funciona:
**cuadros completos a 3×, recortes con zoom fuerte a 4×** — sale nítido sin
inflar el archivo.

## Datos idénticos entre pasadas

Si capturas a dos resoluciones (dos contextos de navegador), **fija los datos en
la primera pasada y reutilízalos**. Si cada pasada genera los suyos, los números
cambian entre planos y el vídeo se contradice: el zoom enseña un total y el
plano general, otro.

```js
// Pasada 1: elige y devuelve las entradas
const entradas = await page.evaluate(elegirEntradas);
// Pasada 2 (otra resolución): publica EXACTAMENTE esas
await page.evaluate(es => es.forEach(e => window.__store.publish(e)), entradas);
```

## Datos bonitos sin mentir

Para un ejemplo hay que elegir valores legibles. Lo legítimo es **usar el motor
real y quedarte con una muestra buena** — no fabricar el resultado a mano:

```js
// Se tira de verdad, en bucle, hasta que salga un caso que se lea bien.
for (let i = 0; i < 300 && !elegida; i++) {
  const e = tirarDeVerdad();
  if (esBuenEjemplo(e)) elegida = e;
}
```

Sigue siendo una salida real del producto. Lo que NO vale es escribir el
resultado a mano y presentarlo como si el sistema lo hubiera producido.

## Medir los rectángulos

Los objetivos de cámara salen de la app, no de mirar la captura a ojo:

```js
const R = await measure(page, {
  panel:  '.rolllog-panel',
  fila:   ['.rolllog-line', 'ADV'],      // desambigua por texto
  opcion: ['.menu-item', 'Ventaja'],
});
// → { panel:{x,y,w,h}, … } en px CSS: se pegan tal cual en el mapa R de la animación
```

Coordenadas CSS, no píxeles de imagen. Subir el `deviceScaleFactor` no mueve
ninguna.

## Móvil

- Viewport 393×852, `isMobile` y `hasTouch` activados (`withApp` lo hace solo
  cuando el ancho es menor de 500).
- **El gesto es otro.** Donde en escritorio hay clic derecho, en móvil hay
  mantener pulsado. Ejercítalo de verdad:

```js
await el.dispatchEvent('touchstart');
await page.waitForTimeout(600);          // por encima del umbral de long-press del repo
await el.dispatchEvent('touchend');
```

- Muchas apps montan **componentes distintos** en móvil. Comprueba que estás
  capturando el de verdad y no el de escritorio estrechado.

## Comprobaciones antes de dar la captura por buena

- [ ] cero `pageerror` (`withApp` aborta solo si hay)
- [ ] la pantalla está completa: nada de esqueletos ni spinners a medio cargar
- [ ] sin datos personales reales
- [ ] los estados del mismo panel comparten `clip`
- [ ] los datos coinciden entre pasadas
- [ ] la resolución aguanta el zoom máximo del guion
