// Exporta un deck HTML de una sola página (slides conmutados por .active) a PDF,
// una página horizontal 1280x720 por slide.
//
// Uso (desde la raíz del repo, donde está node_modules con @playwright/test):
//   node .claude/skills/garantias-deck/scripts/export_pdf.mjs <input.html> <output.pdf>
//
// Convierte el stage de slides apilados en un flujo vertical imprimible (un slide
// por página) y usa page.pdf(). No requiere dependencias extra más allá de Playwright.

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
await page.emulateMedia({ media: 'screen' }); // el deck usa estilos de pantalla, no print
await page.addStyleTag({ content: `
  #progress,.nav,#orient{display:none!important}
  html,body{height:auto!important;overflow:visible!important;background:#fff!important}
  body{display:block!important}
  #stage{position:static!important;transform:none!important;left:auto!important;top:auto!important;
    width:1280px!important;height:auto!important;box-shadow:none!important}
  .slide{position:relative!important;display:flex!important;inset:auto!important;
    width:1280px!important;height:720px!important;break-after:page;page-break-after:always;animation:none!important}
  .slide:last-child{break-after:auto;page-break-after:auto}
`});
await page.waitForTimeout(300);
await page.pdf({ path: out, width: '1280px', height: '720px', printBackground: true,
  margin: { top: 0, right: 0, bottom: 0, left: 0 } });
await browser.close();

if (errs.length) console.error('PAGEERRORS: ' + errs.join(' | '));
console.log('PDF generado: ' + out);
