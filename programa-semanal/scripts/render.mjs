// render.mjs — Renderiza el Programa Semanal Estratégico (HTML + PDF carta
// apaisada, 1 página por actor) a partir de un plan.json.
//
// Diseño Swiss/industrial (print-first): grid con reglas finas, esquinas duras,
// el color del frente es codificación de dato (chip pequeño), y el naranja de
// seguridad queda reservado a las escalaciones. Tipografía Barlow Condensed
// (títulos/encabezados, condensada para columnas angostas) + Inter (cuerpo).
//
// Uso:  node render.mjs <plan.json> <directorio-salida>
//
// El plan.json lo escribe Claude tras interpretar los datos de Supabase
// (ver SKILL.md). Esquema:
// {
//   "semana": "Semana del lunes 15 al viernes 19 de junio de 2026",
//   "generado": "15 de junio de 2026",
//   "desarrollo": "Gran Bosco",
//   "frentes": { "<clave>": { "nombre": "Avalúo de casas", "color": "#2563eb" }, ... },
//   "actores": [
//     {
//       "archivo": "fernando-vera-jun15-19",
//       "nombre": "Fernando Vera", "rol": "Supervisor",
//       "dias": [
//         { "label": "Lunes 15", "tema": "Asegurar la semana",
//           "items": [
//             { "tipo": "coordinar|recorrido|verificar|actualizar",
//               "frente": "<clave de frentes>",
//               "titulo": "Llamar a Carlos (Dotec) — zanjeo Calle 1",
//               "detalle": "Confirmar que ...",
//               "escalacion": "Si no lo garantiza: avisar a Daniel hoy." } ] } ] } ]
// }
//
// Requiere playwright con chromium instalado (npx playwright install chromium).
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { resolve, join } from 'node:path';
import { chromium } from 'playwright';

const [, , planPath, outDir] = process.argv;
if (!planPath || !outDir) { console.error('Uso: node render.mjs <plan.json> <directorio-salida>'); process.exit(1); }
const plan = JSON.parse(readFileSync(planPath, 'utf8'));
mkdirSync(outDir, { recursive: true });

const TIPOS = { coordinar: 'Coordinar', recorrido: 'Recorrido', verificar: 'Verificar', actualizar: 'Actualizar' };
const SAFETY = '#c2410c';
const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

function card(it) {
  const f = plan.frentes[it.frente] || { nombre: it.frente, color: '#525252' };
  const tipo = TIPOS[it.tipo] || it.tipo;
  return `
  <article class="card">
    <header class="c-head">
      <span class="c-frente"><span class="dot" style="background:${f.color}"></span>${esc(f.nombre)}</span>
      <span class="c-tipo">${esc(tipo)}</span>
    </header>
    <h3 class="c-title">${esc(it.titulo)}</h3>
    <p class="c-note">${esc(it.detalle)}</p>
    ${it.escalacion ? `<p class="c-esc"><span class="esc-mark">&#9650;</span>${esc(it.escalacion)}</p>` : ''}
  </article>`;
}

function pagina(a) {
  const total = a.dias.reduce((n, d) => n + d.items.length, 0);
  return `<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8">
<title>Programa Semanal — ${esc(a.nombre)}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;600;700;800&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<style>
  * { margin:0; padding:0; box-sizing:border-box; }
  @page { size: letter landscape; margin: 0; }
  :root { --ink:#171717; --line:#d4d4d4; --muted:#525252; --note:#404040; --safety:${SAFETY}; }
  body { font-family:'Inter',sans-serif; color:var(--ink); background:#fff;
         width:11in; height:8.5in; padding:.4in .45in; display:flex; flex-direction:column; overflow:hidden; }
  .cond { font-family:'Barlow Condensed',sans-serif; }

  .hdr { display:flex; justify-content:space-between; align-items:flex-end;
         border-bottom:3px solid var(--ink); padding-bottom:9px; }
  .hdr .eyebrow { font-size:10px; font-weight:600; letter-spacing:.22em; text-transform:uppercase; color:var(--muted); }
  .hdr .actor { font-family:'Barlow Condensed',sans-serif; font-weight:800; font-size:38px;
                line-height:.95; text-transform:uppercase; letter-spacing:.01em; margin-top:2px; }
  .hdr .rol { font-size:11px; font-weight:600; letter-spacing:.16em; text-transform:uppercase; color:var(--muted); margin-top:3px; }
  .hdr .right { text-align:right; }
  .hdr .right .wk-l { font-size:9.5px; font-weight:600; letter-spacing:.2em; text-transform:uppercase; color:var(--muted); }
  .hdr .right .wk { font-family:'Barlow Condensed',sans-serif; font-weight:700; font-size:20px; text-transform:uppercase; line-height:1; margin-top:2px; }
  .hdr .right .meta { font-size:10.5px; color:var(--muted); margin-top:4px; }
  .hdr .right .meta b { color:var(--ink); }

  .legend { display:flex; align-items:center; gap:18px; padding:7px 0; border-bottom:1px solid var(--line);
            font-size:9px; color:var(--muted); flex-wrap:wrap; }
  .legend .frentes { display:flex; gap:12px; flex-wrap:wrap; }
  .legend .fr { display:inline-flex; align-items:center; gap:5px; font-weight:600; letter-spacing:.04em; }
  .legend .dot { width:8px; height:8px; border-radius:0; display:inline-block; }
  .legend .rule { margin-left:auto; font-style:italic; }

  .cal { flex:1; display:grid; grid-template-columns:repeat(${a.dias.length},1fr); gap:7px; min-height:0; margin-top:8px; }
  .day { display:flex; flex-direction:column; gap:6px; min-height:0; }
  .day-h { border-bottom:2px solid var(--ink); padding-bottom:5px; }
  .day-h .top { display:flex; justify-content:space-between; align-items:baseline; }
  .day-h .d { font-family:'Barlow Condensed',sans-serif; font-weight:700; font-size:17px; text-transform:uppercase; letter-spacing:.02em; line-height:1; }
  .day-h .n { font-size:9px; font-weight:600; color:var(--muted); }
  .day-h .tema { font-size:9px; color:var(--muted); font-style:italic; margin-top:3px; line-height:1.2; }

  .card { border:1px solid var(--line); border-top:3px solid var(--ink); padding:6px 7px 7px; }
  .c-head { display:flex; justify-content:space-between; align-items:center; gap:6px; margin-bottom:3px; }
  .c-frente { display:inline-flex; align-items:center; gap:4px; font-size:8px; font-weight:700;
              letter-spacing:.06em; text-transform:uppercase; color:var(--ink); }
  .c-frente .dot { width:8px; height:8px; display:inline-block; }
  .c-tipo { font-size:8px; font-weight:700; letter-spacing:.13em; text-transform:uppercase; color:var(--muted); }
  .c-title { font-family:'Barlow Condensed',sans-serif; font-weight:600; font-size:13.5px; line-height:1.08; }
  .c-note { font-size:9.5px; color:var(--note); line-height:1.32; margin-top:3px; }
  .c-esc { font-size:9px; color:var(--safety); font-weight:600; line-height:1.28; margin-top:5px;
           padding-left:7px; border-left:2px solid var(--safety); display:flex; gap:4px; }
  .c-esc .esc-mark { font-size:7px; line-height:1.6; }

  .ftr { margin-top:8px; padding-top:6px; border-top:1px solid var(--line);
         display:flex; justify-content:space-between; font-size:8.5px; color:#737373; letter-spacing:.02em; }
</style></head>
<body>
  <div class="hdr">
    <div>
      <div class="eyebrow">Programa Semanal · ${esc(plan.desarrollo)}</div>
      <div class="actor">${esc(a.nombre)}</div>
      <div class="rol">${esc(a.rol)}</div>
    </div>
    <div class="right">
      <div class="wk-l">Semana</div>
      <div class="wk">${esc(plan.semana.replace(/^Semana del\s*/i, ''))}</div>
      <div class="meta"><b>${total}</b> acciones de coordinación</div>
    </div>
  </div>

  <div class="legend">
    <div class="frentes">
      ${Object.values(plan.frentes).map(f => `<span class="fr"><span class="dot" style="background:${f.color}"></span>${esc(f.nombre)}</span>`).join('\n      ')}
    </div>
    <span class="rule">Asegurar el lunes · verificar el día del compromiso · escalar el mismo día</span>
  </div>

  <div class="cal">
    ${a.dias.map(d => `<section class="day">
        <div class="day-h">
          <div class="top"><span class="d cond">${esc(d.label)}</span><span class="n">${d.items.length}</span></div>
          <div class="tema">${esc(d.tema)}</div>
        </div>
        ${d.items.map(card).join('')}
      </section>`).join('')}
  </div>

  <div class="ftr">
    <span>Domus Desarrollos — datos en vivo de Supabase</span>
    <span>Generado el ${esc(plan.generado)}</span>
  </div>
</body></html>`;
}

const browser = await chromium.launch();
const page = await browser.newPage();
for (const a of plan.actores) {
  const html = pagina(a);
  writeFileSync(join(resolve(outDir), `${a.archivo}.html`), html);
  await page.setContent(html, { waitUntil: 'networkidle' });
  // Medir DESPUÉS de que la fuente web cargó: si no, subestima la altura y el
  // contenido del día más cargado se desborda sobre el pie. Encoger para 1 página.
  await page.evaluate(async () => { await document.fonts.ready; });
  await page.evaluate(() => {
    document.body.style.zoom = '';
    const s = Math.min(1, document.body.clientHeight / document.body.scrollHeight);
    if (s < 1) document.body.style.zoom = String(s * 0.98);
  });
  await page.pdf({ path: join(resolve(outDir), `${a.archivo}.pdf`), width: '11in', height: '8.5in', printBackground: true });
  console.log('OK', a.archivo);
}
await browser.close();
