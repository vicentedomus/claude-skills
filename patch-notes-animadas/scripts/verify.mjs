#!/usr/bin/env node
// Verificación del MP4. No es opcional: los tres fallos más caros de este
// formato NO dan error — se ven, y sólo si miras.
//
//   node verify.mjs --video=patch-notes.mp4 [--n=12]
//
// Saca tres cosas y las deja en `_verify/`:
//   · primero.png  — debe ser el estado inicial COMPLETO. Ni negro ni a medio
//                    pintar: es la miniatura que enseña WhatsApp.
//   · ultimo.png   — debe ser el fotograma final sostenido. Si aparece el
//                    primer plano del vídeo, la animación hizo bucle al grabar.
//   · contacto.png — rejilla de N fotogramas: se lee el arco entero de un
//                    vistazo, y es donde saltan los planos que no encuadran.
//
// Míralas de verdad antes de entregar. Un `expect` no ve un texto cortado por
// el borde ni un pie que tapa lo que está explicando.

import fs from 'node:fs';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { getFfmpeg, arg } from './env.mjs';

const VIDEO = path.resolve(arg('video', 'patch-notes.mp4'));
const N = parseInt(arg('n', '12'), 10);
const DIR = path.resolve('_verify');
if (!fs.existsSync(VIDEO)) throw new Error(`no existe ${VIDEO}`);

const { ffmpeg, ffprobe } = getFfmpeg();
fs.rmSync(DIR, { recursive: true, force: true });
fs.mkdirSync(path.join(DIR, 'tiles'), { recursive: true });

const run = (bin, args) => {
  const r = spawnSync(bin, args, { encoding: 'utf8' });
  if (r.status !== 0) { console.error(r.stderr); throw new Error(`${path.basename(bin)} falló`); }
  return r.stdout;
};

const dur = parseFloat(run(ffprobe, ['-v', 'error', '-show_entries', 'format=duration',
  '-of', 'csv=p=0', VIDEO]).trim());
const meta = run(ffprobe, ['-v', 'error', '-show_entries',
  'stream=codec_name,width,height,r_frame_rate,nb_frames', '-of', 'default=nw=1', VIDEO]);
console.log(meta.trim());
console.log(`duración: ${dur.toFixed(3)} s`);

// Primer fotograma real (no el keyframe más cercano: -ss 0 exacto).
run(ffmpeg, ['-hide_banner', '-loglevel', 'error', '-i', VIDEO, '-frames:v', 1,
  '-update', '1', path.join(DIR, 'primero.png'), '-y']);
// Último: -sseof cuenta desde el final, que es lo fiable cerca del borde.
run(ffmpeg, ['-hide_banner', '-loglevel', 'error', '-sseof', '-0.15', '-i', VIDEO,
  '-frames:v', 1, '-update', '1', path.join(DIR, 'ultimo.png'), '-y']);

// Rejilla: N fotogramas repartidos, saltándose el borde final.
const ts = Array.from({ length: N }, (_, i) => (dur * 0.995 * i) / (N - 1));
ts.forEach((t, i) => run(ffmpeg, ['-hide_banner', '-loglevel', 'error',
  '-ss', t.toFixed(2), '-i', VIDEO, '-frames:v', 1, '-update', '1',
  path.join(DIR, 'tiles', String(i).padStart(3, '0') + '.png'), '-y']));

const cols = Math.ceil(Math.sqrt(N)), rows = Math.ceil(N / cols);
run(ffmpeg, ['-hide_banner', '-loglevel', 'error', '-i', path.join(DIR, 'tiles/%03d.png'),
  '-vf', `scale=520:293,tile=${cols}x${rows}:margin=6:padding=4:color=0x222222`,
  '-frames:v', '1', path.join(DIR, 'contacto.png'), '-y']);
fs.rmSync(path.join(DIR, 'tiles'), { recursive: true, force: true });

console.log(`\nfotogramas en ${DIR}: primero.png · ultimo.png · contacto.png`);
console.log(`marcas: ${ts.map(t => t.toFixed(1)).join('  ')}`);
console.log(`
Repasa MIRÁNDOLAS:
  [ ] primero.png es el estado inicial completo (ni negro ni a medias)
  [ ] ultimo.png es el final sostenido (no el arranque: eso sería bucle)
  [ ] no aparece la barra de controles en ningún fotograma
  [ ] ningún texto citado en un pie queda fuera del cuadro
  [ ] ningún pie tapa justo lo que está explicando
  [ ] lo que dice el texto coincide con lo que resalta la captura`);
