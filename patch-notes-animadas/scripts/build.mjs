#!/usr/bin/env node
// Empotra las capturas en el HTML como data URI y deja UN solo archivo.
//
// Es obligatorio: el CSP de los artifacts bloquea cualquier host externo, así
// que una imagen enlazada no carga — y además un archivo suelto se rompe en
// cuanto se recicla el contenedor.
//
//   node build.mjs --template=anim.html --assets=assets.json --out=patch-notes.html
//
// `assets.json` mapea cada placeholder a su PNG:
//   { "__IMG_SHEET__": "caps/sheet.png", "__IMG_LOG1__": "caps/log1.png" }
//
// OJO con el peso: cada placeholder se sustituye en TODAS sus apariciones, así
// que si repites `__IMG_X__` en tres sitios del HTML, el base64 va tres veces.
// Declara cada captura UNA vez (en el mapa `IMG` del JS) y asigna los `src`
// desde ahí. En el prototipo eso bajó el archivo de 5.14 MB a 3.44 MB.

import fs from 'node:fs';
import path from 'node:path';
import { arg } from './env.mjs';

const TPL = arg('template', 'anim.html');
const MAP = arg('assets', 'assets.json');
const OUT = arg('out', 'patch-notes.html');
const LIMITE_MB = 16;                       // tope duro de un artifact publicado

const mime = f => ({ '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
                     '.webp': 'image/webp', '.svg': 'image/svg+xml' })[path.extname(f).toLowerCase()]
                  || 'application/octet-stream';

let html = fs.readFileSync(TPL, 'utf8');
const assets = JSON.parse(fs.readFileSync(MAP, 'utf8'));

for (const [token, file] of Object.entries(assets)) {
  if (!fs.existsSync(file)) throw new Error(`falta la captura ${file} (para ${token})`);
  const veces = html.split(token).length - 1;
  if (veces === 0) console.error(`⚠ ${token} no aparece en la plantilla`);
  if (veces > 1) console.error(`⚠ ${token} aparece ${veces} veces: el base64 se duplicará`);
  html = html.replaceAll(token, `data:${mime(file)};base64,` + fs.readFileSync(file).toString('base64'));
}

// Un placeholder sin sustituir sale como texto literal en la página publicada.
const sobrantes = html.match(/__[A-Z0-9_]+__/g);
if (sobrantes) throw new Error('placeholders sin sustituir: ' + [...new Set(sobrantes)].join(', '));

fs.writeFileSync(OUT, html);
const mb = fs.statSync(OUT).size / 1048576;
console.log(`${OUT} — ${mb.toFixed(2)} MB`);
if (mb > LIMITE_MB) {
  throw new Error(`pasa del límite de ${LIMITE_MB} MB de un artifact. Baja el ` +
    `deviceScaleFactor de las capturas o recorta a la región que de verdad se ve.`);
}
if (mb > LIMITE_MB * 0.75) console.error(`⚠ ${mb.toFixed(1)} MB: cerca del límite de ${LIMITE_MB} MB`);
