import { chromium } from '@playwright/test';
import path from 'node:path';
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
for (const f of process.argv.slice(2)) {
  const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
  await p.goto('file://' + path.resolve(f), { waitUntil: 'load' });
  await p.waitForTimeout(300);
  const bad = await p.evaluate(() => {
    const out = [];
    document.querySelectorAll('section.slide').forEach((s, i) => {
      if (s.scrollHeight > s.clientHeight + 2) out.push(`slide ${i + 1}: ${s.scrollHeight}px`);
    });
    document.querySelectorAll('.zona-card, .pendientes-page, .kpis-page').forEach(c => {
      if (c.scrollHeight > c.clientHeight + 2)
        out.push(`${c.className.split(' ')[0]} "${(c.querySelector('.zc-name')||{}).textContent||''}": ${c.scrollHeight}>${c.clientHeight}`);
    });
    return out;
  });
  console.log((bad.length ? '❌ ' : '✅ ') + path.basename(f) + (bad.length ? ' → ' + bad.join(' | ') : ''));
  await p.close();
}
await b.close();
