// Resolución de dependencias del entorno. Es lo primero que corre cualquier
// script de la skill, porque los tres bloqueos habituales no dan un error
// legible si los descubres a mitad de una grabación:
//
//   1. `playwright-core` puede no estar instalado en el repo consumidor.
//   2. El Chromium del entorno remoto vive en /opt/pw-browsers y `playwright
//      install` está PROHIBIDO ahí.
//   3. `ffmpeg` NO viene en los contenedores de Claude Code on the web.
//
// Todo se resuelve por detección: en una máquina que ya los tenga, esto no
// instala nada.

import fs from 'node:fs';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
import { createRequire } from 'node:module';

const require_ = createRequire(import.meta.url);
/** Carpeta de trabajo donde se dejan las dependencias que haya que instalar. */
export const DEPS_DIR = path.resolve(process.env.PN_DEPS_DIR || '.patch-notes-deps');

function npmInstall(pkgs) {
  fs.mkdirSync(DEPS_DIR, { recursive: true });
  // El package.json es obligatorio, no cosmético: sin él (o con --no-save) npm
  // trata cada install como el conjunto COMPLETO de dependencias y poda las
  // anteriores. Instalar ffmpeg-static y luego playwright-core borraba ffmpeg
  // — "added 1 package, and removed 21 packages" — y el render moría después,
  // lejos de la causa. Con package.json y guardando, los installs se suman.
  const pj = path.join(DEPS_DIR, 'package.json');
  if (!fs.existsSync(pj)) {
    fs.writeFileSync(pj, JSON.stringify(
      { name: 'patch-notes-deps', private: true, version: '1.0.0' }, null, 2));
  }
  execFileSync('npm', ['install', ...pkgs, '--prefix', DEPS_DIR],
    { stdio: 'inherit', timeout: 300_000 });
}

/** Primera ruta existente, o null. */
const firstExisting = (...ps) => ps.find(p => p && fs.existsSync(p)) || null;

/**
 * Devuelve el módulo `chromium` de Playwright, instalando `playwright-core`
 * sólo si no hay ninguno a mano.
 */
export async function getChromium() {
  const local = firstExisting(
    path.join(DEPS_DIR, 'node_modules/playwright-core/index.mjs'),
    path.resolve('node_modules/playwright-core/index.mjs'),
    path.resolve('node_modules/playwright/index.mjs'),
  );
  if (local) return (await import('file://' + local)).chromium;
  try { return require_('playwright-core').chromium; } catch { /* no está */ }
  console.error('· instalando playwright-core…');
  npmInstall(['playwright-core']);
  return (await import('file://' + path.join(DEPS_DIR, 'node_modules/playwright-core/index.mjs'))).chromium;
}

/**
 * Ruta al binario de Chromium. En el entorno remoto de Claude Code hay uno
 * preinstalado y `playwright install` está prohibido: se usa ese. Si no,
 * `undefined` deja que Playwright elija el suyo.
 */
export function chromiumPath() {
  return process.env.PLAYWRIGHT_CHROMIUM
    || firstExisting('/opt/pw-browsers/chromium')
    || undefined;
}

/** Rutas a ffmpeg y ffprobe, instalando los estáticos si el sistema no los trae. */
export function getFfmpeg() {
  const onPath = bin => {
    try { execFileSync('which', [bin], { stdio: 'pipe' }); return bin; } catch { return null; }
  };
  const sysFf = onPath('ffmpeg'), sysProbe = onPath('ffprobe');
  if (sysFf && sysProbe) return { ffmpeg: sysFf, ffprobe: sysProbe };

  const staticFf = () => firstExisting(path.join(DEPS_DIR, 'node_modules/ffmpeg-static/ffmpeg'));
  const staticProbe = () => firstExisting(
    path.join(DEPS_DIR, 'node_modules/ffprobe-static/bin/linux/x64/ffprobe'),
    path.join(DEPS_DIR, 'node_modules/ffprobe-static/bin/darwin/x64/ffprobe'),
    path.join(DEPS_DIR, 'node_modules/ffprobe-static/bin/darwin/arm64/ffprobe'),
  );
  if (!staticFf() || !staticProbe()) {
    console.error('· ffmpeg no está en el sistema: instalando ffmpeg-static (~80 MB)…');
    npmInstall(['ffmpeg-static', 'ffprobe-static']);
  }
  const ffmpeg = sysFf || staticFf(), ffprobe = sysProbe || staticProbe();
  if (!ffmpeg || !ffprobe) throw new Error('no se pudo resolver ffmpeg/ffprobe');
  return { ffmpeg, ffprobe };
}

/** `--clave=valor` de la línea de comandos. */
export function arg(name, def) {
  const hit = process.argv.find(a => a.startsWith(`--${name}=`));
  return hit ? hit.slice(name.length + 3) : def;
}
export const flag = name => process.argv.includes(`--${name}`);
