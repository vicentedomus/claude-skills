// Ayudantes de captura de UI REAL. Es una librería, no un CLI: cómo se arranca
// la app y qué se hace clic es distinto en cada repo, así que ese trozo lo
// escribes tú (ver `references/capture.md`). Aquí vive sólo lo que se repite:
// abrir Chromium con el viewport correcto, medir cajas y disparar capturas con
// un recorte estable.
//
// Las coordenadas SIEMPRE son CSS (las del viewport que elegiste), no píxeles
// de la imagen. El `deviceScaleFactor` sube la resolución del PNG sin mover ni
// una coordenada — así los rectángulos que midas aquí sirven tal cual como
// objetivos de cámara en la animación.

import fs from 'node:fs';
import path from 'node:path';
import { getChromium, chromiumPath } from './env.mjs';

/** Viewports canónicos. La elección móvil/desktop la hace el usuario. */
export const VIEWPORTS = {
  desktop: { width: 1440, height: 900 },
  movil:   { width: 393,  height: 852 },   // iPhone 15 Pro en CSS px
};

/**
 * Abre la app, ejecuta `boot(page)` y te entrega la página lista para capturar.
 *
 * @param {object}   o
 * @param {string}   o.url          URL de arranque (dev server, harness E2E, deploy).
 * @param {object}   o.viewport     VIEWPORTS.desktop | VIEWPORTS.movil | {width,height}.
 * @param {number}   o.dsf          deviceScaleFactor. 3 para cuadros completos,
 *                                  4 para recortes con zoom fuerte. Ver abajo.
 * @param {function} o.boot         async (page) => any — login, navegación, sembrar datos.
 * @param {string[]} o.initScripts  código a inyectar ANTES de los scripts de la página.
 * @param {function} o.run          async (page, bootResult, api) => void — tus capturas.
 */
export async function withApp({ url, viewport = VIEWPORTS.desktop, dsf = 3,
                                boot, initScripts = [], run }) {
  const chromium = await getChromium();
  const browser = await chromium.launch({ executablePath: chromiumPath() });
  const context = await browser.newContext({
    viewport, deviceScaleFactor: dsf,
    isMobile: viewport.width < 500, hasTouch: viewport.width < 500,
  });
  const page = await context.newPage();

  // Los errores de página se acumulan y se comprueban al final: una captura
  // preciosa de una app que reventó por dentro no vale nada.
  const errors = [];
  page.on('pageerror', e => errors.push(String(e)));
  page.on('console', m => { if (m.type() === 'error') errors.push('console: ' + m.text()); });

  for (const s of initScripts) await page.addInitScript(s);
  await page.goto(url);
  const bootResult = boot ? await boot(page) : null;

  const api = { shoot: shoot.bind(null, page), measure: measure.bind(null, page), page };
  try {
    await run(page, bootResult, api);
  } finally {
    await context.close();
    await browser.close();
  }
  if (errors.length) {
    console.error('⚠ la app registró errores durante la captura:');
    errors.slice(0, 8).forEach(e => console.error('  ·', e));
    throw new Error(`captura abortada: ${errors.length} error(es) de página`);
  }
  return bootResult;
}

/**
 * Captura a disco. `clip` en coordenadas CSS; omítelo para el cuadro completo.
 *
 * REGLA: para capturar varios ESTADOS del mismo panel (p. ej. una lista que
 * crece), pásales a todos el MISMO `clip`. Si dejas que cada uno use su propia
 * caja, al encadenarlos en la animación el panel "salta" de sitio.
 */
export async function shoot(page, file, clip) {
  fs.mkdirSync(path.dirname(file), { recursive: true });
  await page.screenshot({ path: file, ...(clip ? { clip } : {}) });
  return file;
}

/**
 * Mide cajas de elementos y las devuelve redondeadas, listas para pegar en el
 * mapa `R` de la animación. `sel` es un objeto {nombre: selector} — o
 * {nombre: [selector, texto]} para desambiguar por contenido.
 */
export async function measure(page, sel) {
  const raw = await page.evaluate((entries) => {
    const out = {};
    for (const [name, q] of entries) {
      const [css, text] = Array.isArray(q) ? q : [q, null];
      const nodes = [...document.querySelectorAll(css)];
      const el = text ? nodes.find(n => n.textContent.includes(text)) : nodes[0];
      out[name] = el ? el.getBoundingClientRect().toJSON() : null;
    }
    return out;
  }, Object.entries(sel));
  const round = r => r && { x: Math.round(r.x), y: Math.round(r.y),
                            w: Math.round(r.width), h: Math.round(r.height) };
  const missing = Object.entries(raw).filter(([, v]) => !v).map(([k]) => k);
  if (missing.length) console.error('⚠ no se encontraron:', missing.join(', '));
  return Object.fromEntries(Object.entries(raw).map(([k, v]) => [k, round(v)]));
}

/**
 * Resolución recomendada según el zoom máximo del guion, para no descubrir en
 * el render que el plano estrella está blando.
 *
 * En el cuadro se ve una franja de `1920 / (base * zoom)` px CSS. Para que
 * llegue nítida a 1920 px de vídeo hacen falta `dsf ≈ base * zoom`.
 */
export function dsfPara(zoomMaximo, base = 1.2) {
  return Math.min(4, Math.max(2, Math.ceil(base * zoomMaximo)));
}
