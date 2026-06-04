// Verificación del deck: abre el HTML, recorre todos los slides, captura PNG de cada uno
// y reporta errores de consola/pageerror. Comprueba escalado en 3 viewports.
//
// Uso: node .claude/skills/tareas-deck/scripts/verify.mjs <input.html> <outdir>
import { chromium } from '@playwright/test';
import path from 'node:path';
import fs from 'node:fs';

const [, , inArg, outArg] = process.argv;
if (!inArg) { console.error('Uso: node verify.mjs <input.html> [outdir]'); process.exit(1); }
const src = 'file://' + path.resolve(inArg);
const outdir = path.resolve(outArg || '/tmp/tareas-deck-verify');
fs.mkdirSync(outdir, { recursive: true });

const browser = await chromium.launch();
const errs = [];
const logs = [];
const page = await browser.newPage({ viewport: { width: 1280, height: 720 } });
page.on('pageerror', e => errs.push('PAGEERROR: ' + e.message));
page.on('console', m => { if (m.type() === 'error') logs.push('CONSOLE: ' + m.text()); });

await page.goto(src, { waitUntil: 'load' });
const N = await page.evaluate(() => document.querySelectorAll('.slide').length);
console.log('Slides detectados: ' + N);

for (let k = 0; k < N; k++) {
  await page.evaluate(i => document.querySelectorAll('.slide').forEach((s, j) => s.classList.toggle('active', j === i)), k);
  await page.waitForTimeout(120);
  // ¿hay overflow de contenido fuera del stage?
  const overflow = await page.evaluate(() => {
    const a = document.querySelector('.slide.active');
    if (!a) return null;
    return { sh: a.scrollHeight, ch: a.clientHeight, sw: a.scrollWidth, cw: a.clientWidth };
  });
  const warn = overflow && (overflow.sh > overflow.ch + 2 || overflow.sw > overflow.cw + 2) ? '  ⚠ posible overflow' : '';
  console.log(`slide ${k + 1}/${N}${warn}` + (overflow ? `  (${overflow.sw}x${overflow.sh} en ${overflow.cw}x${overflow.ch})` : ''));
  await page.screenshot({ path: path.join(outdir, `slide-${String(k + 1).padStart(2, '0')}.png`) });
}

// escalado en otros viewports
for (const vp of [{ w: 844, h: 390, n: 'movil-horizontal' }, { w: 390, h: 844, n: 'movil-vertical' }]) {
  await page.setViewportSize({ width: vp.w, height: vp.h });
  await page.evaluate(() => document.querySelectorAll('.slide').forEach((s, j) => s.classList.toggle('active', j === 0)));
  await page.waitForTimeout(150);
  await page.screenshot({ path: path.join(outdir, `viewport-${vp.n}.png`) });
}

await browser.close();
console.log('\nErrores de consola: ' + logs.length);
logs.forEach(l => console.log('  ' + l));
console.log('Pageerrors: ' + errs.length);
errs.forEach(e => console.log('  ' + e));
console.log('\nCapturas en: ' + outdir);
process.exit(errs.length ? 2 : 0);
