#!/usr/bin/env node
// HTML animado → MP4 H.264. Es el script con más trampas del lote: cada línea
// del handshake con la página existe por un fallo concreto (ver
// `references/pitfalls.md`).
//
//   node render.mjs --html=patch-notes.html --duration=30 --out=video.mp4
//   node render.mjs --html=... --audio=pista.mp3        # opcional, si hay audio
//
// Contrato con el HTML (lo cumple `assets/template.html`):
//   · pone `window.__ready = true` en el PRIMER frame del tick, pareado con t=0
//   · lee `window.__recording` para NO hacer bucle
//   · expone `window.__seek(t)`
//   · esconde su propio chrome cuando `__recording` está puesto

import fs from 'node:fs';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { getChromium, chromiumPath, getFfmpeg, arg } from './env.mjs';

const HTML = path.resolve(arg('html', 'patch-notes.html'));
const DURATION = parseFloat(arg('duration', '30'));
const W = parseInt(arg('width', '1920'), 10);
const H = parseInt(arg('height', '1080'), 10);
const OUT = path.resolve(arg('out', 'patch-notes.mp4'));
const AUDIO = arg('audio', null);
const LIMITE_MB = 16;                      // lo que WhatsApp acepta con holgura

if (!fs.existsSync(HTML)) throw new Error(`no existe ${HTML}`);
const { ffmpeg, ffprobe } = getFfmpeg();
// El PID en el nombre evita que dos renders simultáneos compartan temporal y
// se borren el WebM el uno al otro.
const TMP = path.resolve(`.render-tmp-${process.pid}`);
fs.rmSync(TMP, { recursive: true, force: true });
fs.mkdirSync(TMP, { recursive: true });

const chromium = await getChromium();
const browser = await chromium.launch({ executablePath: chromiumPath() });

// ── Fase 1 · calentamiento SIN grabar ─────────────────────────────────────
// El WebM empieza a escribirse al crear el contexto. Si en ese contexto se
// carga la página por primera vez, los segundos de fuentes e imágenes quedan
// grabados. Un contexto desechable los deja ya cacheados.
{
  const ctx = await browser.newContext({ viewport: { width: W, height: H } });
  const page = await ctx.newPage();
  await page.goto('file://' + HTML);
  await page.waitForFunction(() => window.__ready === true, null, { timeout: 60_000 });
  await page.waitForTimeout(1200);
  await ctx.close();
}

// ── Fase 2 · grabación ────────────────────────────────────────────────────
const ctx = await browser.newContext({
  viewport: { width: W, height: H },
  recordVideo: { dir: TMP, size: { width: W, height: H } },
});
// Handshake: la página deja de hacer bucle y esconde su chrome. Va en
// addInitScript para llegar ANTES que cualquier script de la página — hacerlo
// después deja la barra de controles en los primeros fotogramas del MP4.
await ctx.addInitScript(() => { window.__recording = true; });

const page = await ctx.newPage();
const errores = [];
page.on('pageerror', e => errores.push(String(e)));

const t0 = Date.now();
await page.goto('file://' + HTML);
await page.waitForFunction(() => window.__ready === true, null, { timeout: 60_000 });
const offset = (Date.now() - t0) / 1000;     // lo grabado antes del t=0 de la animación
await page.evaluate(() => window.__seek && window.__seek(0));   // segunda defensa
console.log(`· arranque hasta __ready: ${offset.toFixed(2)} s`);

await page.waitForTimeout(DURATION * 1000 + 400);
await page.close();
await ctx.close();
await browser.close();

if (errores.length) {
  console.error('⚠ errores de página durante la grabación:');
  errores.slice(0, 5).forEach(e => console.error('  ·', e));
  throw new Error('render abortado: la animación lanzó errores');
}

const webm = fs.readdirSync(TMP).find(f => f.endsWith('.webm'));
if (!webm) throw new Error('Playwright no dejó ningún .webm');

// ── Fase 3 · WebM → MP4 ───────────────────────────────────────────────────
// `-ss` antes de `-i` recorta el arranque; `-t` corta en seco en DURATION para
// no arrastrar el margen de más. `high/4.0` + `yuv420p` es lo que abre en
// QuickTime, Safari y WhatsApp sin sorpresas.
const args = ['-hide_banner', '-loglevel', 'error',
  '-ss', String(offset), '-i', path.join(TMP, webm),
  ...(AUDIO ? ['-i', AUDIO] : []),
  '-t', String(DURATION),
  '-c:v', 'libx264', '-preset', 'slow', '-crf', '20',
  '-profile:v', 'high', '-level', '4.0', '-pix_fmt', 'yuv420p', '-r', '30',
  '-vf', `scale=${W}:${H}:flags=lanczos`,
  ...(AUDIO ? ['-c:a', 'aac', '-b:a', '160k', '-shortest'] : ['-an']),
  '-movflags', '+faststart', OUT, '-y'];

const r = spawnSync(ffmpeg, args, { encoding: 'utf8' });
// r.error = ni siquiera arrancó el binario (ruta muerta); r.stderr = falló al
// codificar. Distinguirlos importa: el primero manda a mirar el entorno.
if (r.error) throw new Error(`no se pudo ejecutar ffmpeg (${ffmpeg}): ${r.error.message}`);
if (r.status !== 0) { console.error(r.stderr); throw new Error('ffmpeg falló'); }
fs.rmSync(TMP, { recursive: true, force: true });

const probe = spawnSync(ffprobe, ['-v', 'error', '-show_entries',
  'format=duration', '-show_entries', 'stream=codec_name,width,height,nb_frames',
  '-of', 'default=nw=1', OUT], { encoding: 'utf8' }).stdout.trim();
const mb = fs.statSync(OUT).size / 1048576;
console.log(probe);
console.log(`${OUT} — ${mb.toFixed(2)} MB`);
if (mb > LIMITE_MB) {
  console.error(`⚠ ${mb.toFixed(1)} MB: por encima de lo que WhatsApp manda con ` +
    `holgura (${LIMITE_MB} MB). Sube el --crf (23-26) o acorta la duración.`);
}
console.log('· ahora toca verificar:  node verify.mjs --video=' + path.basename(OUT));
