---
name: huashu-max
description: >-
  Runbook del combo huashu-design + ui-ux-pro-max: huashu decide cómo se ve (dirección, assets
  reales de marca, anti-slop) y ui-ux-pro-max garantiza que funcione y se construya bien
  (accesibilidad, reglas por stack). Fases con checkpoint, de la idea al mockup o hasta código
  de producción. Solo con invocación explícita: "huashu max", "combo huashu". NO dispara en
  pedidos de diseño genéricos (esos van a cada skill por separado).
---

# huashu-max

> **Esta skill es NUESTRA (orquestación), no es core de ninguna de las dos.** No modifica
> `huashu-design` ni `ui-ux-pro-max`: las encadena por fases y fija quién manda cuando
> chocan. Actualizar cualquiera de las dos sigue siendo un overwrite mecánico de upstream.

**Requiere `huashu-design` y `ui-ux-pro-max` instaladas al lado** (carpetas hermanas de
esta). Todas las rutas de abajo son relativas a la raíz de esta skill: `../huashu-design/…`,
`../ui-ux-pro-max/…`. Resuélvelas según dónde esté instalada (top-level de este repo,
`.claude/skills/`, …); no hardcodees rutas absolutas.

## Cuándo usarla

Solo cuando el usuario la pide por nombre: **"huashu max"**, **"combo huashu"**,
*"usa huashu + ui-ux-pro-max"*.

**Cuándo NO:** un pedido de diseño a secas no la dispara. Prototipo, deck o animación sin
combo → `huashu-design` directo. Reglas de UX o de un stack sin dirección de diseño →
`ui-ux-pro-max` directo.

## Prerequisitos (verifícalos al arrancar)

1. **`../huashu-design/SKILL.md` existe.** Si falta, el combo no aplica → avísalo y detente.
2. **`../ui-ux-pro-max/scripts/search.py` existe y `python3` corre.** Si falta, sigue con
   huashu sola y avisa que la capa de accesibilidad y stack queda como checklist manual
   (la de §Fase 5 de abajo).

## Cómo cargar cada capa (presupuesto de contexto)

- **huashu-design: cárgala con Skill.** Es la que gobierna el proceso; necesitas su cuerpo.
  Sus `references/` se leen bajo demanda según su propia tabla de ruteo.
- **ui-ux-pro-max: NO la cargues con Skill.** Su valor está en los datos, no en la prosa.
  Úsala **solo ejecutando** `../ui-ux-pro-max/scripts/search.py`. Las reglas que el combo
  necesita de su SKILL.md ya están resumidas aquí abajo.

## Las tres capas y dónde engrana cada una

| Capa | Qué gobierna | Dónde actúa |
|---|---|---|
| **huashu-design** | dirección, assets de marca, anti-slop, proceso (junior pass, variantes, checkpoints), entregables visuales | fases 0–4 y crítica |
| **ui-ux-pro-max** | accesibilidad e interacción (CRITICAL), segunda opinión de estilo, reglas por stack | fase 2 (filtrada), 4b y 5 |
| **este runbook** | orden de fases, modo mostrar/construir, arbitraje de conflictos, overrides del combo | siempre |

## El flujo: fases con checkpoint

Conduce las fases **en orden** y **pausa en cada checkpoint** para que el usuario revise.
Solo encadena de corrido si lo pide explícitamente.

### Fase 0 · Verificar hechos — huashu (#0)

Si hay producto, marca o tecnología concreta: `WebSearch` **antes** de preguntar nada.
Existencia, estado de lanzamiento, versión y specs → `product-facts.md`.

### Fase 1 · Contexto — huashu (§1.a / Fallback)

- **Hay marca concreta** → protocolo de assets de huashu completo: logo (obligatorio),
  foto de producto (físico) o capturas de UI (digital), regla 5-10-2-8, y todo en
  `brand-spec.md`.
- **Pedido vago, sin contexto** → el modo asesor de dirección de huashu: 3 direcciones de
  **3 escuelas distintas**, con demos.
- **El usuario ya trae design system / Figma / capturas** → se parte de ahí.

🛑 **Checkpoint 1:** `brand-spec.md` o la dirección elegida, aprobados.

### Fase 2 · Segunda opinión — ui-ux-pro-max, filtrada por huashu

```bash
python3 ../ui-ux-pro-max/scripts/search.py "<producto> <industria> <keywords>" --design-system -f markdown
```

**Sin `--persist`**: no generes `design-system/MASTER.md`. La fuente de verdad única es
`brand-spec.md`.

Trata el resultado como **candidato, no como decisión**. Pásalo por el filtro antes de
integrar nada:

| Del resultado de ui-ux-pro-max… | Acción |
|---|---|
| Colores / tipografía cuando **ya hay** `brand-spec.md` con marca real | **Descarta.** La paleta por industria es un promedio; la marca manda |
| Morado agresivo / gradiente morado, `#0F172A` estilo GitHub dark, Inter/Roboto/Arial como display, emoji como ícono | **Descarta** (lista anti-slop de huashu), salvo que la marca los use de verdad |
| Patrón de página que no corresponde al tipo de entregable (p. ej. "Hero + Testimonials" para un dashboard) | **Descarta** |
| Anti-patrones de la industria, efectos de interacción, notas de accesibilidad | **Integra** a `brand-spec.md` (sección `禁区`, «zonas prohibidas», de la plantilla de huashu) |
| Pairings tipográficos o paletas cuando **no** hay marca | Úsalos como **una** de las 3 direcciones, nunca como la única |

Para profundizar en algo puntual: `--domain ux|typography|chart|landing "<keywords>"`.

### Fase 3 · Elegir modo

Pregunta (o infiere del pedido) **¿mostrar o construir?**

- **Mostrar** → la pieza es el entregable: deck, prototipo para validar, animación,
  infografía, demo.
- **Construir** → el destino es UI de producción en un repo y un stack reales.

### Fase 4a · Mostrar — pipeline de huashu

El flujo estándar de huashu tal cual: cuatro preguntas → junior pass → full pass con
variantes / Tweaks → exportación (PDF, PPTX, MP4 con SFX + BGM). Con dos agregados del
combo:

- Las reglas de accesibilidad no negociables (§Fase 5) aplican **también aquí**: contraste,
  tamaño legible a la distancia de visión, `prefers-reduced-motion` en HTML interactivo.
- Los overrides del combo (§Overrides) aplican siempre.

🛑 **Checkpoint 4a:** la pieza revisada en el navegador.

### Fase 4b · Construir — huashu → ui-ux-pro-max

huashu dice explícitamente que no sirve para apps de producción; el combo cubre ese hueco
con un **traspaso**, no anulando su exclusión:

1. **Mockup hi-fi con huashu** (como en 4a, sin exportación de video). Es **referencia
   visual**, no código a copiar: el React+Babel inline de huashu no es código de producción.
   🛑 **Checkpoint 4b-1:** mockup aprobado.
2. **Reglas del stack** con ui-ux-pro-max:
   ```bash
   python3 ../ui-ux-pro-max/scripts/search.py "<componentes/temas>" --stack <stack>
   ```
   Stacks: `html-tailwind` (default), `react`, `nextjs`, `astro`, `vue`, `nuxtjs`,
   `nuxt-ui`, `svelte`, `swiftui`, `react-native`, `flutter`, `shadcn`, `jetpack-compose`.
   Si el stack es React/Next, suma `--domain react` (performance).
3. **Implementa** siguiendo, en este orden de precedencia: el `CLAUDE.md` y las convenciones
   del repo destino → las reglas del stack → el mockup aprobado.
4. **Tokens:** los valores de `brand-spec.md` se mapean al sistema de theming del stack
   (p. ej. `theme.extend.colors.primary` en Tailwind → `bg-primary`). Así se cumple a la vez
   "usa clases del tema" (ui-ux-pro-max) y "nada de colores inventados en el momento" (huashu):
   la única fuente sigue siendo la spec.

🛑 **Checkpoint 4b-2:** implementación revisada.

### Fase 5 · Verificación doble — ambas

1. **huashu:** Playwright (`python3 ../huashu-design/scripts/verify.py <archivo> --viewports …`),
   consola sin errores, clics reales en prototipos, `ffprobe` si hay video con audio.
2. **ui-ux-pro-max — no negociable, en ambos modos:**
   - [ ] Contraste de texto ≥ 4.5:1 (en los dos modos si hay light/dark)
   - [ ] Focus visible en todo lo interactivo; orden de tab = orden visual
   - [ ] Targets táctiles ≥ 44×44px; `cursor-pointer` y feedback de hover en clicables
   - [ ] Hover sin layout shift; transiciones de 150–300 ms con transform/opacity
   - [ ] `prefers-reduced-motion` respetado
   - [ ] Imágenes con alt; inputs con label; el color no es el único indicador
   - [ ] (Construir) Responsive en 375 / 768 / 1024 / 1440, sin scroll horizontal en móvil

   Checklist completo: sección "Pre-Delivery Checklist" de `../ui-ux-pro-max/SKILL.md`
   (léela con Read solo si necesitas el detalle).

### Fase 6 · Crítica (opcional) — ambas

Si el usuario pide revisión o calificación: las 5 dimensiones de
`../huashu-design/references/critique-guide.md` **+ una 6.ª, Accesibilidad (0–10)**, basada
en la checklist de la Fase 5. Salida: Keep / Fix (⚠️ / ⚡ / 💡) / Quick Wins.

## Arbitraje cuando chocan

| Conflicto | Gana | Por qué |
|---|---|---|
| Colores y tipografía | **`brand-spec.md`** > paleta de huashu > paleta de ui-ux-pro-max | La marca real sobre el promedio por industria |
| Anti-patrones de estilo | **huashu** | Su objetivo es que la marca se reconozca |
| Accesibilidad e interacción | **ui-ux-pro-max, sin excepción** | CRITICAL incluso en un deck o un prototipo |
| Patrones de implementación por stack | **ui-ux-pro-max** (tras las convenciones del repo) | huashu no cubre producción |
| Proceso y ritmo (junior pass, variantes, checkpoints) | **huashu** | ui-ux-pro-max no tiene proceso propio |
| Fuente de verdad del design system | **un solo `brand-spec.md`** | Sin `--persist`, para no tener un `MASTER.md` que diverja |

## Overrides del combo (sobre huashu)

Estas reglas **reemplazan** lo que diga `huashu-design` mientras corre el combo:

1. **Sin marca de agua.** No agregues "Created by Huashu-Design" a las animaciones ni a
   ningún entregable. Solo si el usuario la pide explícitamente, usa la plantilla de huashu.
2. **Convenciones en español.** Textos y microcopy en español (respeta la variante del
   proyecto si la tiene). Comillas «» o “” (sigue lo que ya use el proyecto), **nunca 「」**.
   Signos de apertura ¿ ¡. Formatos de fecha y número del locale de la audiencia. Los
   subtítulos de las narraciones van con la misma regla de líneas cortas de huashu, en español.
3. **Voz en off:** el pipeline de TTS de huashu (Doubao) está pensado para chino. Si el
   entregable lleva narración, confirma con el usuario la voz y el proveedor en español
   antes de generar audio.

## Reglas

- **Gated por default**: pausa en cada checkpoint. Solo encadena si te lo piden.
- **No dupliques fuentes de verdad**: todo lo que se decida vive en `brand-spec.md`.
- **No edites las skills de abajo**: si algo de huashu o de ui-ux-pro-max no sirve, la
  excepción va en este runbook (§Overrides o §Arbitraje), no en su SKILL.md.
- **Respeta el `CLAUDE.md` del repo consumidor**: este runbook gobierna el *método*, no
  anula sus convenciones.
