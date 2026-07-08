# Gotchas generales — entorno de ejecución

Estos gotchas son **generales del entorno**: aplican a *cualquier* repo que se
teste con esta skill detrás del proxy de Claude Code on the web (o en un CI/local
normal). No dependen del repo. Los gotchas **específicos de un repo** (rol
primario, modelo de permisos, selectores de modal, branch base, deps CDN
concretas…) **no van aquí** — viven en el propio repo consumidor, en
`tests/QA-NOTES.md` (ver el SKILL.md, "Sistema de gotchas en dos niveles").

Cada entrada está en formato **Síntoma → causa → fix** para que puedas
diagnosticar por el síntoma sin leerte todo.

---

## 1. Deps CDN fallan por certificado (proxy MITM)

**Síntoma:** el proyecto `setup-<role>` se queda colgado esperando el formulario
de login (`#login-form` *oculto*) o en un splash que nunca arranca; el timeout
parece "credenciales malas".

**Causa:** muchas apps cargan runtime deps desde CDNs vía `<script src>` (cliente
Supabase, jspdf, web fonts). Un proxy MITM re-firma TLS con una CA que el browser
rechaza, así que esos subrecursos fallan con `ERR_CERT_AUTHORITY_INVALID`, la app
nunca bootea y el setup cuelga. Un timeout de setup sobre un login oculto **casi
nunca** es credenciales — es fallo de cert en subrecursos.

**Confirmar:** carga la app una vez y revisa la consola por
`ERR_CERT_AUTHORITY_INVALID` / `<lib> is not defined`.

**Fix:** bypass de cert a nivel de browser. Busca el knob del repo en vez de
editar el config (p. ej. Domus Hub: `export PLAYWRIGHT_IGNORE_TLS=1`, que el
config mapea a `ignoreHTTPSErrors` + `--ignore-certificate-errors`). El helper
`assets/playwright.remote-env.ts` (gotcha 2) ya activa esto automáticamente
cuando detecta el proxy.

---

## 2. El browser no se rutea por el proxy CONNECT-only (TLS-ignore no basta)

**Síntoma:** consola muestra `ERR_CONNECTION_CLOSED` (no `ERR_CERT_*`) para hosts
CDN/backend (`*.jsdelivr.net`, tu `*.supabase.co`, etc.), `curl -s
"$HTTPS_PROXY/__agentproxy/status"` sí responde, pero la app se queda en el
splash. Persiste **incluso con** `--ignore-certificate-errors`.

**Causa:** el egress del entorno es **CONNECT-only vía `$HTTPS_PROXY`**, y
Chromium **no** usa ese proxy salvo que se lo digas explícitamente. `curl`
funciona (honra `HTTPS_PROXY`) pero el browser no.

**Lo que parece el fix y NO funciona en este Chromium:** `--proxy-server=...`
(el CONNECT nunca llega al proxy), `proxy.bypass` de Playwright (no excluye
localhost → el dev server local se proxea y muere con **405**, porque el proxy es
CONNECT-only y rechaza un GET plano), y un PAC en `data:` URL.

**Lo que SÍ funciona:** rutear el browser vía `--proxy-pac-url` apuntando a un PAC
en **`file://`** que manda *localhost DIRECT y todo lo demás por el proxy*, más
`--ignore-certificate-errors`.

**Fix:** copia `assets/playwright.remote-env.ts` al root del repo y cabléalo al
Playwright config. Está **gateado por detección** (no-op en local/CI) y además
apunta `executablePath` al Chromium preinstalado (gotcha 4):

```ts
import { ignoreTLS, remoteLaunchOptions } from './playwright.remote-env';
// ...
use: {
  ignoreHTTPSErrors: ignoreTLS,
  launchOptions: { ...(remoteLaunchOptions() || {}) },
},
```

Prefiere este helper a hackear flags a mano; es el mismo fix que necesita todo
repo detrás de este proxy. (Si el config es `.js`: conviértelo a `.ts` —
Playwright carga configs `.ts` y sus imports relativos nativamente— o transpila
el helper a `.js`.)

---

## 3. Un `webServer` de archivos estáticos no bootea una app con bundler

**Síntoma:** el screenshot de fallo muestra la app *renderizada completa* pero
tanto `#app.visible` como `#login-form` dan timeout, y la consola tiene 404s para
rutas tipo `/config.js` y/o un error de MIME de módulo (`.ts` → `video/mp2t`).

**Causa:** algunos configs (a menudo un *config móvil aparte*) levantan el server
con un estático — `npx serve .`, `http-server`, `python -m http.server`. Eso
sirve archivos crudos, pero una app con bundler (Vite/Next/webpack) necesita su
propio dev/preview server para (a) resolver imports bare/módulo, (b) servir el
`publicDir` en `/` (p. ej. `/config.js`), y (c) transpilar `.ts`/`.tsx` al vuelo.
Bajo un estático, los archivos referenciados dan 404 y los módulos se sirven con
MIME incorrecto (bloqueado por strict MIME checking) → el bundle nunca ejecuta y
el boot se estanca. Es mismatch estático-vs-bundler, no un bug de tu test.

**Fix:** no edites el config comiteado. Levanta tú el server real del bundler en
el puerto esperado y deja que el `reuseExistingServer: true` del config lo adopte.
Detecta el bundler de `package.json` / `vite.config.*` / `next.config.*` y corre
su preview de producción (lo más cercano a lo que ships); para Vite es
`npm run build && npm run preview`, luego `curl -sf localhost:3000/config.js` para
confirmar que los assets resuelven antes de correr la suite. Reporta el config
roto al usuario como tech debt preexistente a arreglar por separado (p. ej.
apuntar su `webServer.command` al preview del bundler en vez de `serve .`).

---

## 4. Chromium preinstalado con versión distinta a la que resuelve `@playwright/test`

**Síntoma:** `Executable doesn't exist at .../chrome-headless-shell-XXXX` (o
similar), aunque el browser "está instalado".

**Causa:** el entorno ship un Chromium en `/opt/pw-browsers/chromium` cuya build
!= la que `@playwright/test` resuelve, y el entorno **prohíbe** `playwright
install`. También pasa si instalas el browser *antes* de `npm ci` (los deps
pinnean la versión de Playwright y el browser instalado queda huérfano — **orden:
`npm ci` primero, `playwright install` después**).

**Fix:** apunta `executablePath` al Chromium preinstalado. El helper
`assets/playwright.remote-env.ts` (gotcha 2) ya lo hace: pinnea `executablePath` a
`/opt/pw-browsers/chromium` cuando existe. Un solo helper cubre gotchas 1, 2 y 4.
