---
name: patch-notes-animadas
description: >-
  Convierte PRs mergeados en "patch notes" animadas para enseñárselas a usuarios
  no técnicos: un MP4 corto (WhatsApp/Telegram) y/o un artifact con URL
  permanente, construidos sobre CAPTURAS DE LA UI REAL de la app. Repo-agnóstica:
  detecta la paleta del proyecto y descubre cómo arrancarlo. Actívala cuando el
  usuario diga "patch notes", "notas de versión", "novedades", "explícale esto a
  los jugadores/usuarios", "vídeo de lo nuevo", "anuncia este PR", "release
  notes", "changelog animado" o pida enseñar un cambio a gente que no lee
  código. NO la uses para un changelog de texto, un resumen de PR, ni para
  prototipos de UI que aún no existen (eso es huashu-design a secas).
---

# Patch notes animadas

Coge PRs ya mergeados y saca un vídeo corto que un jugador —o un cliente, o tu
madre— entienda sin abrir GitHub.

**Requiere la skill [`huashu-design`](../huashu-design/) al lado.** Ella pone la
gramática de movimiento (`references/animation-best-practices.md` y sobre todo
`references/animation-pitfalls.md`); esta pone el flujo, la captura de UI real y
el empaquetado. Si no está sincronizada, dilo y sigue con lo que hay aquí, pero
avisa de que el movimiento va sin su manual.

## La regla que sostiene todo lo demás

> **La UI que aparece en pantalla es la UI real del producto, capturada con
> Playwright. Nunca redibujada en CSS/SVG.**

Es el protocolo de assets de huashu (§1.a) y no es un capricho estético: un
mockup dibujado produce "una animación genérica de producto" que podría ser de
cualquier app. Lo que hace creíble unas patch notes es que el usuario reconoce
su propia pantalla.

Si no consigues arrancar la app o llegar al estado que hace falta: **para y
pregunta**. No dibujes la pantalla "provisionalmente" — se queda.

## Flujo

Las 🛑 son compuertas: preguntas, **esperas de verdad**, y sólo entonces sigues.

### 1 · Reunir el material

Lee los PRs con las tools de GitHub (`mcp__github__pull_request_read`, método
`get`). Te interesa el **cuerpo**, no el diff: ahí está el "qué gana el usuario".
Descarta lo que no se ve (infra, CI, refactors, ETL) — eso no son patch notes.

Agrupa en un release coherente. Tres o cuatro cambios que se tocan cuentan mejor
que seis inconexos.

### 2 · 🛑 Preguntas (una sola tanda)

Pregunta **todo junto**, y espera:

| Pregunta | Por qué cambia el trabajo |
|---|---|
| **¿Móvil o desktop?** | Define el viewport de captura (393×852 vs 1440×900), el formato (9:16 vs 16:9) **y el guion**: en móvil el gesto es mantener pulsado, en escritorio es clic derecho. No es un recorte, es otro vídeo. |
| **¿Duración?** | 15 s = un solo cambio. 30 s = tres, con arco completo (lo normal). 60 s = se abandona a la mitad. |
| **¿Audio?** | huashu trae 37 SFX y 6 pistas en `huashu-design/assets/`. Con audio parece producto; mudo, mucha gente ve el móvil en silencio igual. |
| **¿Entregable?** | MP4 (circula, no se corrige) · artifact (URL permanente, republicable, no se manda por WhatsApp) · ambos (recomendado: mismo HTML). |

### 3 · Marca del repo

Saca la paleta del proyecto, **no la inventes**:

1. Custom properties del CSS: `grep -h -- '--[a-z-]*:' style.css src/**/*.css | head -60`,
   buscando el bloque `:root`.
2. `tailwind.config.*` → `theme.extend.colors`.
3. Tokens en JSON/TS (`tokens.*`, `theme.*`).
4. Si no hay nada, **pregunta**. Un color inventado hace que el vídeo no
   parezca del producto, que es justo lo contrario de lo que buscas.

Anota además el nombre del producto y el look (dark-only, light-only o ambos).

**Tipografías: siempre stacks del sistema.** El CSP de los artifacts bloquea
Google Fonts y cualquier CDN, y una `@import` que falla lo hace **en silencio**.
Si el repo usa fuentes de CDN, elige stacks del sistema con proporciones
parecidas y déjalo escrito en un comentario.

### 4 · 🛑 Guion, antes de tocar código

Escribe el reparto Slow-Fast-Boom-Stop plano a plano: qué se ve, qué dice el
pie, adónde va la cámara. **Enséñalo y espera.** Corregir aquí cuesta minutos;
después de animar, horas.

Cada plano contesta las cuatro preguntas de huashu: papel narrativo, distancia
del espectador (un móvil: el texto se lee grande), temperatura y capacidad.

Del guion salen dos listas que necesitas ya: **qué estados** de la app hay que
capturar y **qué rectángulos** hay que medir.

### 5 · 🛑 Capturar la UI real

Cómo arrancar la app, por orden de preferencia:

1. **Harness de tests E2E** (`tests/fixtures/*harness*.html`). Lo mejor con
   diferencia: monta la UI real con datos de prueba, sin login ni base de datos
   de producción, y es reproducible.
2. **Dev server** (`npm run dev` / `npm start`) + login de test si hace falta.
3. **Deploy** — último recurso: son datos reales, cuidado con lo que sale.

Detalle y recetas en [`references/capture.md`](references/capture.md).
Los ayudantes están en `scripts/capture.mjs` (`withApp`, `shoot`, `measure`).

Tres reglas que ahorran una vuelta entera:

- **Resolución según el zoom máximo del guion.** `dsfPara(zoom)`: a 3.5× de zoom
  una captura a 2× se ve blanda. Cuadros completos a 3×, recortes con zoom
  fuerte a 4×.
- **Mismo `clip` para todos los estados de un panel.** Si cada estado usa su
  propia caja, al encadenarlos el panel salta.
- **Datos idénticos entre pasadas.** Si capturas a dos resoluciones, fija los
  datos en la primera y reutilízalos: si no, los números cambian entre planos y
  el vídeo se contradice a sí mismo.

**Enseña las capturas y espera.** Son el material del que ya no te vas a mover.

### 6 · Animar

Parte de `assets/template.html`. El motor (tick, cámara, foco, easings) está
hecho; tú escribes `render(t)` y rellenas los placeholders. Lee
[`references/pitfalls.md`](references/pitfalls.md) **antes**, no después.

Lo que más se nota, por orden:

- `expoOut` por defecto, nunca `ease` ni `linear`.
- **Medio segundo de pausa antes de cada resultado clave.** Es la regla que más
  cuesta respetar y la que más separa un vídeo de producto de una demo.
- Foco = recortar la capa nítida + desenfocar y apagar la de atrás. Sólo bajar
  la opacidad deja el fondo nítido y no retrocede.
- Entradas escalonadas de 30 ms en listas y tarjetas.
- Cierre por colapso→expansión y **corte seco**. Un fundido a negro quita
  decisión al final.
- **Si un pie anuncia una elección, dibújala** con `pickRow()`. La captura trae
  su propio estado resaltado y te deja diciendo "eliges X" sobre una imagen que
  resalta Y.

### 7 · 🛑 Verificar mirando

```bash
node scripts/build.mjs  --template=anim.html --assets=assets.json --out=patch-notes.html
node scripts/render.mjs --html=patch-notes.html --duration=30 --out=patch-notes.mp4
node scripts/verify.mjs --video=patch-notes.mp4
```

`verify.mjs` deja `_verify/primero.png`, `_verify/ultimo.png` y
`_verify/contacto.png`. **Ábrelos.** Ninguno de estos fallos lanza un error:

- primer fotograma negro o a medio pintar (es la miniatura de WhatsApp)
- último fotograma que vuelve al principio (bucle al grabar)
- la barra de controles dentro del vídeo
- un número citado en el pie que queda fuera del cuadro
- un pie tapando justo lo que explica
- el texto diciendo una cosa y la captura enseñando otra

### 8 · Entregar

- **MP4** → `SendUserFile`. Por debajo de 16 MB va sin problema por WhatsApp.
- **Artifact** → el mismo HTML, con `favicon` y `description`. Sale privado; lo
  comparte el usuario. Republicar con el **mismo `file_path`** conserva la URL,
  así que un error se corrige sin invalidar el enlace ya enviado.

Di siempre qué quedó fuera y qué asumiste.

## Aspecto según el destino

| Destino | Lienzo | Escenario |
|---|---|---|
| Desktop → WhatsApp | 1920×1080 (16:9) | 1440×900 |
| Móvil → WhatsApp/Stories | 1080×1920 (9:16) | 393×852 |
| Desktop → sólo artifact | 1920×1080 | 1440×900 |

En 16:9 con UI de escritorio, el texto sólo se lee en un móvil si la cámara
**hace zoom sobre la zona que cambia**. Un plano general de una pantalla de
1440 px en un teléfono no se lee: no es un estilo, es un requisito.

## Entorno

- **`ffmpeg` no viene** en los contenedores de Claude Code on the web.
  `scripts/env.mjs` instala `ffmpeg-static` (~80 MB) la primera vez.
- **Chromium sí viene**, en `/opt/pw-browsers`. `playwright install` está
  prohibido; `env.mjs` apunta al preinstalado.
- Todo se resuelve por detección: donde ya existan, no instala nada.
- Los scripts dejan `.patch-notes-deps/` (dependencias) y `_verify/` (fotogramas)
  en el directorio de trabajo. Añádelos al `.gitignore` del repo consumidor: son
  artefactos regenerables, no fuente.

## Cuándo NO usar esta skill

- Changelog de texto o resumen de PR → escríbelo y ya.
- Prototipo de una UI que todavía no existe → `huashu-design` directamente (aquí
  no habría nada real que capturar).
- Cambios sin superficie visible (infra, CI, ETL) → no son patch notes.
