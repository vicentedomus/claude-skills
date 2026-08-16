# La guía interactiva — contrato y caso resuelto

El artifact es **el entregable**, no un extra bonito. El DM lo abre del celular en la mesa y de ahí
dirige. Si tiene que ir a la app o al libro a media escena, la guía falló.

Carga **`huashu-design`** y **`artifact-design`** antes de escribir el HTML.

## Las tres reglas que se rompen solas

Las tres salieron de rechazos textuales del DM sobre una guía que parecía terminada.

### A · Cada momento trae su texto literal

> *«Lees el gancho, ¿cuál gancho?»*

Una caja **«Lee esto en voz alta»** con el párrafo completo, en cada momento de la espina. Nunca
un puntero a otro lado.

### B · Ninguna referencia queda colgando

> *«¿Qué es un vistani?» · «"De todo ese lore", ¿cuál lore?»*

Si la guía dice «ese lore», el lore está en la página. Si usa una palabra del setting, el glosario
la define **antes** de que aparezca.

**Auto-chequeo antes de publicar:** relee preguntándote, en cada sustantivo propio y cada
referencia deíctica («ese», «el gancho», «la tabla», «los cinco puntos»), *¿esto está resuelto en
esta página?* Cada «no» es un bug.

En *Book of the Raven* el chequeo encontró seis palabras que yo usaba sin definir nunca:
Candlekeep, vistani, wereraven, Scarlet Sash, Shadowfell y *charm of heroism*.

### C · Separar lo que sabe el DM de lo que sabe la mesa

Cajas marcadas **«Lo que tú sabes y ellos no»**. El DM necesita saber, en cada momento, qué
información es suya. Ejemplo: los cuervos del techo SON los habitantes, y no se dice.

---

## Contrato de secciones

| # | Sección | Contenido mínimo |
|---|---|---|
| 1 | Premisa | Qué creen los jugadores que van a hacer vs. qué es realmente |
| 2 | Glosario | Toda palabra de setting o reglas que la guía use después |
| 3 | Índice fijo | Rail lateral ≥1080px · barra pegajosa con chips en celular |
| 4 | El orden | Momentos numerados: texto literal + «Lo que haces» + tiempo |
| 5 | Elenco | Cada NPC: cómo se ve, cómo suena, qué hace, qué esconde |
| 6 | Locaciones | Plano clicable + índice; cada una con lectura y mecánica |
| 7 | Tablas operativas | Qué dispara qué · red de pistas · tablas del módulo |
| 8 | Encaje con la party | Lo que sale de cruzar el módulo con las hojas de los PJs |

**La sección 8 es la que justifica la skill.** No vive en ningún campo de la base: sale de leer el
módulo con las hojas de los PJs enfrente. En *Book of the Raven*: la Orcus Figurine apaga el Turn
Undead del clérigo **y su daño radiante es lo único de la party que puede destruirla**.

## Gazetteer: el plano es la interfaz

Para una aventura con locaciones numeradas, el corazón es un **plano clicable**:

- Imagen en **base64** (el CSP bloquea imágenes remotas). Un webp de 3000px ≈ 570 KB en base64;
  el límite del artifact son 16 MB.
- Un botón absoluto por locación, posicionado en **fracciones 0-1** del contenedor
  (`left: x*100%`), las mismas que los pines de `mapa_pines`.
- Código de color **idéntico al de la app**, o el DM tiene que traducir entre dos sistemas.
- Estimar coordenadas leyendo el plano funciona con precisión aceptable — pero **dilo**, no lo
  vendas como exacto.

## Índice fijo, responsivo

El mismo `<nav>` en dos formas. Un rail lateral en celular se come la pantalla, y el celular es
donde se usa en la mesa.

```css
/* Por defecto (celular): barra pegajosa arriba con chips deslizables */
.rail { position: sticky; top: 0; z-index: 60; }
.rail-links { display: flex; overflow-x: auto; }

/* Pantalla grande: rail fijo a la izquierda */
@media (min-width: 1080px) {
  body { padding-left: 212px; }
  .rail { position: fixed; left: 0; top: 0; bottom: 0; width: 212px; }
  .rail-links { flex-direction: column; }
}
```

**Scroll-spy: manda la ÚLTIMA sección visible**, no la primera. Con la primera, al bajar a una
sección la anterior sigue cruzando la banda de lectura y el índice marca mal.

```js
const ids = enlaces.map(a => a.dataset.sec).filter(id => visibles.has(id));
const activa = ids[ids.length - 1];
```

En celular, desliza el chip activo a la vista con `scrollIntoView({inline:"center"})`.

## Diseño

Hereda el design system del repo (`style.css`): `--bg #131313`, `--surface #1c1b1b`, oro
`#ffbf00`, tinta `#e5e2e1`.

**Nunca cargues fuentes de Google.** El CSP de los artifacts bloquea CDNs y el fallback es
silencioso: usa stacks del sistema (serif del sistema para títulos, sans para cuerpo, mono para
DCs y números).

Tema oscuro fijo es una decisión válida aquí — hereda la identidad del repo — pero **pinta el
`background` del `body` explícitamente**: un body transparente toma el fondo del host.

## Verificación antes de publicar

```bash
npx playwright ...  # con executablePath: '/opt/pw-browsers/chromium'
```

Comprueba en dos viewports (390×844 y 1400×950):

- [ ] Los pines del plano se pintan y cada uno abre su ficha
- [ ] El índice marca bien la sección en al menos 5 puntos del scroll
- [ ] El rail no se encima con el contenido en escritorio
- [ ] Cero errores de consola y cero peticiones fallidas
- [ ] La imagen del plano cargó de verdad (`naturalWidth > 0`, no solo presente en el DOM)
