// Exporta un deck de resultados-proveedores a PDF — un slide por página,
// horizontal 508×285.75 mm (el tamaño que ya declara @page en styles.css).
//
// El deck es un flujo vertical de .slide (1920×1080) con page-break-after en
// cada uno y reglas @media print que ocultan el modal y fijan @page. Por eso
// basta cargar y page.pdf() con preferCSSPageSize.
//
// Uso (desde la raíz del repo, donde está node_modules con @playwright/test):
//   node .claude/skills/resultados-proveedores/scripts/export_pdf.mjs <input.html> <output.pdf>

import { chromium } from '@playwright/test';
import path from 'node:path';

const [, , inArg, outArg] = process.argv;
if (!inArg || !outArg) {
  console.error('Uso: node export_pdf.mjs <input.html> <output.pdf>');
  process.exit(1);
}
const src = 'file://' + path.resolve(inArg);
const out = path.resolve(outArg);

const browser = await chromium.launch();
const page = await browser.newPage();
const errs = [];
page.on('pageerror', e => errs.push(e.message));
await page.goto(src, { waitUntil: 'load' });
await page.waitForTimeout(300);
// page.pdf usa media 'print' por defecto → aplica @media print (oculta modal, @page).
await page.pdf({ path: out, preferCSSPageSize: true, printBackground: true });
await browser.close();

if (errs.length) console.error('PAGEERRORS: ' + errs.join(' | '));
console.log('PDF generado: ' + out);
