// render.mjs — Renderiza el Programa Semanal Estratégico (HTML + PDF carta
// apaisada, 1 página por actor) a partir de un plan.json.
//
// Uso:  node render.mjs <plan.json> <directorio-salida>
//
// El plan.json lo escribe Claude tras interpretar los datos de Supabase
// (ver SKILL.md). Esquema:
// {
//   "semana": "Semana del lunes 15 al viernes 19 de junio de 2026",
//   "generado": "11 de junio de 2026",
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
if (!planPath || !outDir) {
  console.error('Uso: node render.mjs <plan.json> <directorio-salida>');
  process.exit(1);
}
const plan = JSON.parse(readFileSync(planPath, 'utf8'));
mkdirSync(outDir, { recursive: true });

const TIPOS = {
  coordinar:  { label: 'Coordinar',  color: '#1d4ed8', bg: '#dbeafe' },
  recorrido:  { label: 'Recorrido',  color: '#92400e', bg: '#fef3c7' },
  verificar:  { label: 'Verificar',  color: '#9a3412', bg: '#ffedd5' },
  actualizar: { label: 'Actualizar', color: '#374151', bg: '#e5e7eb' },
};

const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

function card(it) {
  const f = plan.frentes[it.frente] || { nombre: it.frente, color: '#6b7280' };
  const t = TIPOS[it.tipo] || TIPOS.coordinar;
  return `
  <div class="card" style="--c:${f.color}">
    <div class="card-top">
      <span class="tipo" style="color:${t.color};background:${t.bg}">${t.label}</span>
      <span class="card-tag">${esc(f.nombre)}</span>
    </div>
    <div class="card-title">${esc(it.titulo)}</div>
    <div class="card-note">${esc(it.detalle)}</div>
    ${it.escalacion ? `<div class="card-esc">${esc(it.escalacion)}</div>` : ''}
  </div>`;
}

function pagina(a) {
  const total = a.dias.reduce((n, d) => n + d.items.length, 0);
  return `<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8">
<title>Programa Semanal — ${esc(a.nombre)}</title>
<style>
  * { margin:0; padding:0; box-sizing:border-box; }
  @page { size: letter landscape; margin: 0; }
  body { font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif; background:#f4f5f7; color:#1f2937;
         width: 11in; height: 8.5in; padding: .42in .5in; display:flex; flex-direction:column; }
  .hdr { display:flex; justify-content:space-between; align-items:flex-end; border-bottom:3px solid #111827; padding-bottom:10px; }
  .hdr h1 { font-size:21px; letter-spacing:.4px; text-transform:uppercase; }
  .hdr .sub { color:#6b7280; font-size:12px; margin-top:3px; }
  .actor { text-align:right; }
  .actor .nom { font-size:19px; font-weight:700; }
  .actor .rol { font-size:11.5px; color:#6b7280; text-transform:uppercase; letter-spacing:1px; }
  .leyenda { display:flex; align-items:center; gap:14px; margin:9px 0; font-size:10.5px; color:#6b7280; }
  .leyenda .tipo { font-size:9.5px; }
  .cal { flex:1; display:grid; grid-template-columns:repeat(${a.dias.length},1fr); gap:9px; min-height:0; }
  .dia { background:#fff; border:1px solid #e5e7eb; border-radius:10px; padding:7px; display:flex; flex-direction:column; gap:6px; }
  .dia-h { padding-bottom:6px; border-bottom:1px solid #e5e7eb; }
  .dia-h .d { font-size:12px; font-weight:700; text-transform:uppercase; letter-spacing:.6px; color:#374151; }
  .dia-h .tema { font-size:10px; color:#6b7280; font-style:italic; margin-top:1px; }
  .card { background:#fff; border:1px solid #e5e7eb; border-left:4px solid var(--c); border-radius:7px; padding:6px 7px; }
  .card-top { display:flex; justify-content:space-between; align-items:center; gap:6px; margin-bottom:3px; }
  .tipo { font-size:8.5px; font-weight:800; text-transform:uppercase; letter-spacing:.7px; padding:2px 7px; border-radius:99px; }
  .card-tag { font-size:8.5px; font-weight:700; text-transform:uppercase; letter-spacing:.6px; color:var(--c); }
  .card-title { font-size:12px; font-weight:700; line-height:1.25; }
  .card-note { font-size:10.5px; color:#4b5563; line-height:1.35; margin-top:3px; }
  .card-esc { font-size:10px; color:#b91c1c; font-weight:600; line-height:1.3; margin-top:4px;
              padding:3px 6px; background:#fef2f2; border-radius:5px; }
  .ftr { margin-top:9px; padding-top:7px; border-top:1px solid #d1d5db; display:flex; justify-content:space-between;
         font-size:9.5px; color:#9ca3af; }
</style></head>
<body>
  <div class="hdr">
    <div>
      <h1>Programa Semanal · Tareas Estratégicas</h1>
      <div class="sub">${esc(plan.desarrollo)} — ${esc(plan.semana)} · ${total} acciones</div>
    </div>
    <div class="actor"><div class="nom">${esc(a.nombre)}</div><div class="rol">${esc(a.rol)}</div></div>
  </div>
  <div class="leyenda">
    ${Object.values(TIPOS).map(t => `<span class="tipo" style="color:${t.color};background:${t.bg}">${t.label}</span>`).join('\n    ')}
    <span>El lunes se asegura con proveedores lo comprometido en la semana; el día del compromiso se verifica en sitio; lo incumplido se escala el mismo día.</span>
  </div>
  <div class="cal">
    ${a.dias.map(d => `<div class="dia">
        <div class="dia-h"><div class="d">${esc(d.label)}</div><div class="tema">${esc(d.tema)}</div></div>
        ${d.items.map(card).join('')}
      </div>`).join('')}
  </div>
  <div class="ftr">
    <span>Frentes: ${Object.values(plan.frentes).map(f => esc(f.nombre)).join(' · ')}</span>
    <span>Domus Desarrollos · generado el ${esc(plan.generado)} (datos en vivo)</span>
  </div>
</body></html>`;
}

const browser = await chromium.launch();
const page = await browser.newPage();
for (const a of plan.actores) {
  const html = pagina(a);
  writeFileSync(join(resolve(outDir), `${a.archivo}.html`), html);
  await page.setContent(html, { waitUntil: 'networkidle' });
  // Si el contenido excede la hoja, escalar para garantizar 1 página
  await page.evaluate(() => {
    const s = Math.min(1, document.body.clientHeight / document.body.scrollHeight);
    if (s < 1) document.body.style.zoom = s * 0.99;
  });
  await page.pdf({ path: join(resolve(outDir), `${a.archivo}.pdf`), width: '11in', height: '8.5in', printBackground: true });
  console.log('OK', a.archivo);
}
await browser.close();
