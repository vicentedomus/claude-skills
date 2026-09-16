---
name: oneshot
description: "Armar una one-shot de D&D lista para dirigir en QuestKeep, de dos maneras: adaptando una aventura publicada (módulo, capítulo de antología) o inventando una original con el compendio como musa. Activa cuando el usuario diga: prepara la one-shot, ármame una one-shot, vamos a correr <nombre de módulo>, adapta esta aventura, dirijo <módulo> el <día>, qué one-shot corremos, quiero una one-shot de <tema>, prepara Book of the Raven / Axeholm / Sunless Citadel, o pida una sesión única de principio a fin. NO es para preparar la siguiente sesión de una campaña larga — eso es halo-session-prep."
---

# One-shot: de cero a la mesa

Una sesión única tiene que meter **un arco entero** en unas horas. Esta skill lo arma por dos
carriles y entrega **un plan modular en la app** — el árbol de bloques que el DM tiene abierto
mientras dirige.

Anunciar al iniciar: **"Activando oneshot."** Responder siempre en **español mexicano simple**
(ver §Reglas duras).

**Campaña por defecto: `one-shots`.** Es donde escribe esta skill salvo que el DM diga otra cosa
(existe también `one-shots-leo`, que NO es la de por defecto).

## El entregable es el árbol, no una página

Decisión del DM (2026-09-13): **el plan modular ES la chuleta de mesa.** No un resumen de ella.

La razón es que el árbol está **vivo** y una página no: el bloque `encuentro` recalcula la
dificultad contra el party de hoy y se lanza a iniciativa con un clic, el bloque `mapa` abre el
plano, y las fichas de NPC y lugar se editan en su sitio. Un artifact dice «3 ghouls, dificultad
Alta» y se queda escrito aunque cambie el party.

El artifact **solo se publica si el DM lo pide** (para leer fuera de la compu o compartir).
Contrato en `references/artifact-guia.md`. No lo ofrezcas por default: son dos fuentes de verdad
y la segunda se desincroniza sola.

## Los dos carriles

El Paso 1 bifurca. Todo lo demás (P0, P2, P3, P5-P8) es común.

| | **Carril A** · módulo publicado | **Carril B** · original |
|---|---|---|
| De dónde sale | `data/books/` (61 libros, 15 one-shots OSW) | el compendio como musa + la premisa del DM |
| Nombres propios | **verbatim del módulo** | **reskin**: hueso oficial, carne del DM |
| Topónimos | son el contenido | se reskinean |
| Elenco | el del módulo, 0 NPCs nuevos | reskineado del compendio |
| Fuente de verdad | el texto del libro | la premisa del DM; el grafo solo sugiere |
| Rastro de origen | `cf_inspiracion` | `cf_inspiracion` + `monstruos.base` |

**Reskin no es «inspirarse».** Es el §8 del Lazy DM y el §8 de Flee, Mortals!: el statblock **no
se toca** — cambia el nombre, la especie, la cultura y la ficción. Si el DM pide «Strahd pero
xoloescuintle hombre-lobo porque es una one-shot mexicana», Strahd sigue siendo Strahd en números.
Método completo en `references/carril-b-original.md`.

> **La regla de «limar el setting» de `dnd-worldbuilder/references/npc.md` NO aplica al carril A.**
> El valor está justo en que sea Candlekeep y el Scarlet Sash. En el carril B sí aplica, porque
> ahí el setting es del DM.

---

## P0 · Marco — cuatro preguntas, siempre

**Antes de medir nada.** Las cuatro se preguntan aunque parezcan obvias: tres cambian números y la
cuarta cambia si la mesa es segura.

1. **¿Qué PJs juegan?** En `one-shots` hay 6 PJs partidos en dos niveles (3 y 8). El presupuesto
   sale distinto y el filtro heurístico se equivoca. Enséñale el party al DM y que lo confirme.
2. **¿Cuántas horas de mesa tienen?** Es el input de P2; sin él no hay cuántas escenas.
3. **¿Qué reglamento de encuentros?** `dnd2024` (el default de la app) o `fm`. Se guarda **por
   encuentro** en `encuentros.estrategia`, así que puede mezclarse.
4. **Líneas y velos.** Si no están registrados, se preguntan. No es apéndice.

```sql
select p.nombre, p.jugador, p.clase, p.subclase, p.nivel, p.raza, f.nombre as carpeta
from personajes p left join character_folders f on f.id = p.folder_id
where p.campaign_slug = 'one-shots' and p.es_pj = true
  and coalesce(f.nombre,'') !~* 'prueb|test' and p.nombre !~* '(prueb|test|^zz)'
order by p.nivel desc, p.nombre;
```

Con eso se crea el `session_plans` vacío (`bloques = '[]'::jsonb`, que es lo que lo marca como
modular) con su `nombre` y su `fecha_sesion`.

---

## P1 · Carril

Di cuál es y por qué. Si es **carril A**, además clasifica la fuente — es el paso que más caro
sale saltarse:

| Tipo | Cómo se reconoce | Cómo se dirige |
|---|---|---|
| **Gazetteer** | Locaciones numeradas (C1–C17), un plano, un elenco | **Se navega**: saltas al cuarto donde están |
| **Guion** | Escenas encadenadas, «después de esto los personajes…» | **Se avanza**: una escena lleva a la siguiente |
| **Mixto** | Un tramo lineal + una locación con llaves (lo más común) | Guion hasta la locación, gazetteer dentro |

**Imponer la forma equivocada destruye el producto aunque los datos estén perfectos** — y no se
nota revisando la base de datos, solo intentando dirigir la partida. Para un gazetteer la unidad
es **la sala**, no el acto: el árbol lleva un bloque `lugar` por estancia bajo la escena que las
contiene, y el índice lo deriva el motor (`inverseRelationsHTML`), no se mantiene a mano.

**Dilo en voz alta:** «Esta aventura es un gazetteer de N estancias, así que el árbol va a ser un
índice navegable, no una secuencia».

Y antes de prometer nada, comprueba que la app puede servir el libro:
`references/verificar-contenido.md`.

---

## P2 · El esqueleto ANTES que el contenido: el reloj y la cadena

Dos cosas, y las dos se escriben **vacías** antes de una sola línea de prosa. El reloj dice
**cuándo** pasa cada escena; la cadena dice **por qué**.

### 2a · El reloj

Con las horas de P0 la aritmética es fija. **No es criterio, es división.**

| Horas | Escenas | Clímax | Cuerpo |
|---|---|---|---|
| 3 h | 3-4 | 45 min | 2-3 escenas de ~40 min |
| **4 h** | **5** | **60 min** | 4 escenas de 45 min |
| 5 h | 6 | 60 min | 5 escenas de 45 min |
| 6 h+ | 6-7 | 60-75 min | + descanso; la fatiga cuesta más que el reloj |

Tres reglas del Lazy DM §2.9, y las tres se violan solas:

- **Una escena ≈ 45 minutos.** Es la unidad de planificación. Cuatro horas son cinco escenas, no
  doce.
- **Se planifica hacia atrás desde el clímax.** Reserva sus 45-60 minutos primero y reparte lo que
  sobra.
- **Se corta del medio, nunca del final.** *«It's far more important to run the climax of the
  adventure than the material in the middle.»* Por eso **cada escena intermedia nace con su
  costura de corte marcada en el título** — el DM tiene que saber, sin pensarlo, qué puede tirar
  cuando va tarde.

**Aquí se crea el esqueleto de bloques VACÍO**, con los minutos ya en los badges. El contenido
viene después. Un one-shot de 3 h con 5 escenas planeadas no se acaba, y lo que se sacrifica es
siempre el final.

Dos notas de mesa del mismo §2.9: si no hay personajes previos, pide que los construyan **alrededor
del tema** de la aventura o ten pregenerados; y confirma al empezar que todos se pueden quedar las
horas que dura.

### 2b · La cadena — qué hace que pase la escena siguiente

**Este es el paso que no existía, y su ausencia produjo seis roturas en la primera one-shot que
armó esta skill.** El reloj ordena las escenas por minuto; nada las ordenaba por **causa**. El
resultado fueron cuatro escenas perfectas y sueltas: la mesa llegaba a la escena 3 cargando una
losa que nadie le había dicho para qué servía.

**Cada escena, antes de tener contenido, declara tres líneas:**

```
QUÉ QUIEREN     — lo que la mesa persigue mientras está aquí. No «qué hay»: qué buscan.
QUÉ SE LLEVAN   — lo que sale de esta escena y la siguiente NECESITA.
QUÉ LA DISPARA  — qué de la escena anterior los puso aquí.
```

Y encima de las tres, la **costura de corte** de P2a, si la escena es intermedia.

**La prueba, y se hace en seco:** lee la cadena **sin el contenido**, solo las tres líneas de cada
escena en orden. El «qué se llevan» de una tiene que encajar con el «qué la dispara» de la
siguiente. Donde no encajen, hay una rotura — y se ve en diez segundos, mucho antes de escribir
prosa que luego hay que tirar.

Ejemplo de la cadena que sí funcionó, después de arreglarla:

| Escena | Qué quieren | Qué se llevan |
|---|---|---|
| Apertura | entender qué pasa y decidir si entran | el gancho común |
| A | ver el objetivo con sus ojos | **el problema planteado** |
| B | una forma de resolverlo que no sea suicidarse | **el plan + las dos piezas** |
| Clímax | ejecutarlo | — |

Ver el problema → encontrar la solución → ejecutarla. **Si tu cadena no tiene esa forma (o la de
un misterio, o la de una fuga), probablemente no tienes una cadena: tienes escenas.**

Tres roturas típicas, todas cometidas en la primera corrida:

- **El plan llega por telepatía.** La sesión entera cuelga de una idea (*quemar la puerta con una
  losa a la espalda*) y ningún NPC, pista ni escena se la dice a los jugadores. La tenías tú en la
  cabeza. **Pregúntate siempre: ¿quién les dice esto, y en qué minuto?**
- **El orden contradice la causa.** Necesitan la herramienta antes del asalto, pero la escena de
  conseguirla va después. Se ve al leer la cadena en seco; no se ve leyendo el reloj.
- **El villano aparece en el minuto 95.** Si el clímax es contra alguien, ese alguien tiene que
  haber sido **nombrado, oído o visto** antes. Es el *Slow Burn* de Flee, Mortals! §8, comprimido:
  en un one-shot bastan tres frases de aliados distintos durante una pelea previa.
- **La escena arranca porque los jugadores «tienen curiosidad».** «QUÉ LA DISPARA: quieren ver qué
  pasa» no es un disparador, es una esperanza. Un disparador es **alguien pidiendo algo concreto**,
  con una consecuencia si no lo hacen: *«suban y bájenme a decir si esa puerta se puede abrir hoy;
  si no se puede, paro la campana y todos nos vamos a morir de hambre con mucho orden»*. Eso
  además le da a la mesa un criterio para saber cuándo terminó la escena.
- **Un aliado habla en una escena a la que nunca llegó.** «En medio de la pelea, el cura les suelta
  que…» — ¿de dónde salió el cura? Los aliados que reparten información **entran al grupo en la
  apertura, con una razón para ir**, y hablan en los huecos (el camino, el respiro después del
  combate), no entre turnos de iniciativa. Si un NPC solo existe para decir una frase, dila tú por
  boca de otro que sí esté.
- **El plan pide un objeto y nadie sabe dónde está.** «Consiguen una losa y brea» no es una escena:
  es una elipsis. Cada pieza que la mesa necesita lleva escrito **quién sabe dónde está y por
  qué lo sabe** —la cantera la conoce la cantera; la brea, el que trae las antorchas—. Y si la
  pieza no es el reto de la sesión, **no le pongas prueba: dásela.**

---

## P3 · Presupuesto — el PRIMER chequeo, no el último

Antes de enamorarte de una aventura, mide si le cabe a la party. **No cites el presupuesto de
memoria: léelo del repo**, que es lo que la app va a pintar.

```bash
grep -n "XP_BUDGET" -A6 react/encuentros/data.ts      # dnd2024: XP por personaje (XDMG)
sed -n '1,80p' react/encuentros/estrategias/fm.ts     # fm: CR por personaje + CR cap
```

- **`dnd2024`** — es **por personaje**; multiplícalo por el nº de PJs. Nivel 3: Bajo 150 · Medio
  225 · **Alto 400** → una party de 2 tiene 300 / 450 / 800. La etiqueta la calcula
  `react/encuentros/logic.ts` (`xpBudget`, `difficulty`), y por encima de Alto pinta «Sobre High».
- **`fm`** — presupuesto en **CR**, y el **CR cap no se multiplica**: es techo *por criatura*.
  Máximo 3 criaturas no-minion por personaje. Un jefe `Solo` **no** se mide con el presupuesto:
  tiene su propia tabla. Nivel medio **redondeando hacia abajo**, no al más cercano. Detalle en
  `docs/flee-mortals-manual.md` §4.

**Lee el nivel declarado en el TEXTO de la locación, no del rango del libro.** *Axeholm* está en
un libro de nivel 1-6 y su primera línea dice *«balanced for characters of 5th level»*.

**Ojo con los módulos que escalan por tamaño de party** («one ghoul plus one additional ghoul for
each member of the party»): con 2 PJs dan números distintos a los que uno supone. En *Axeholm*,
forzar la puerta de A1 daba **9 ghouls = 1.800 XP**, 2,3× el presupuesto Alto de una party de 2.

Si no cabe, dilo y ofrece alternativas **antes** de invertir horas. Ese chequeo descartó Axeholm y
validó Book of the Raven en la misma conversación.

---

## P4 · Los tres pasos que el módulo nunca hace

La aventura publicada ya hizo cinco de los ocho pasos de Shea: locaciones, NPCs, monstruos, objetos
y escenas vienen resueltos. **Estos tres no puede hacerlos, y son los que deciden si la sesión se
siente de esta mesa.** En el carril B existen igual, solo que se inventan en vez de reescribirse.

### a · Review the characters

El módulo no conoce a tu mesa. Lee las fichas reales (`personajes.sheet_data`, `subclase`, `raza`,
`jugador`) y anota los tres o cuatro sitios donde el módulo y un PJ **se tocan**: un enemigo que su
trasfondo odia, una puerta que su clase abre sola, un NPC que podría conocerlo.

Esto no vive en ningún campo de la base — sale de leer el módulo con las hojas enfrente. En *Book
of the Raven*: la Orcus Figurine apaga el Turn Undead del clérigo **y su daño radiante es lo único
de la party que puede destruirla**.

> **No pidas `personajes.descripcion`: está vacía.** Lo poblado es `jugador`, `subclase`, `raza` y
> `sheet_data`.

### b · Strong start de ESTA mesa

El módulo trae **ganchos** («los aldeanos contratan a los aventureros para investigar…»), que es
otra cosa: un gancho explica por qué van, una apertura es el primer minuto de mesa. Escríbela tú,
con su texto literal para leer en voz alta.

### c · Los 10 secretos, abstraídos

El módulo escribe los secretos **pegados a una sala o a una boca**:

> ❌ *«Si los personajes registran el escritorio de C7, encuentran una carta que revela que el
> alcalde le debe dinero al gremio.»*

Eso es un **camino**, no un hecho. Si la mesa nunca entra a C7 —y no va a entrar, nadie entra a la
mitad de las salas— el secreto **no existe**. Abstraerlo es separar las dos cosas:

```
· El alcalde le debe dinero al gremio.            ← el HECHO (sobrevive a todo)
    semillas: la carta del escritorio en C7 · el tabernero lo suelta borracho
    (si no tocan ninguna: lo menciona el propio alcalde cuando lo presionen)
```

Ahora, cuando ignoren C7, **tachas la semilla y el hecho sigue en pie**, listo para colgarse de lo
que sí estén tocando.

### La tercera línea, que es la que justifica el secreto

**Un secreto sin «qué cambia» es trivia.** El formato del manual —hecho + semillas— dice qué es
verdad y cómo se descubre, pero **no dice para qué le sirve saberlo a la mesa**. Sin esa línea se
escriben hechos verdaderos e inertes, que es exactamente lo que pasó en la primera corrida: *«el
grano alcanza para dos años»* es un dato, no una palanca.

```
· El grano de adentro alcanza para dos años.
    semillas: los costales se ven por la tronera · un miliciano lo suelta al rendirse
    qué cambia: deja de ser un asalto y pasa a ser un asedio con reloj. Si NO entran hoy,
                el intendente aguanta los tres días que espera. Convierte «¿por qué la
                prisa?» en «no hay mañana».
```

**La prueba:** un secreto vale si al descubrirlo cambia **una de tres cosas** —

1. **Una decisión** de la mesa (*mata la opción de sitiar; hay que entrar hoy*).
2. **Una opción táctica** que antes no veían (*los de leva no quieren estar ahí: se pueden ir en
   vez de morir; son 10 de los enemigos del clímax*).
3. **Cómo tratan a alguien** (*el segundo al mando tiene a su hijo adentro: por ahí se negocia*).

Si no cambia ninguna, **no es secreto, es relleno** — bórralo y escribe otro. Los de reserva
también llevan su «qué cambia» listo, porque son las cartas que sueltas cuando la mesa se atora:
*«el pretil tiene un tramo caído»* vale justo porque **les quita la cobertura a los fusileros**.

**Diez hechos; semillas solo en los 3-5 que salen esta sesión.** Un hecho cuesta un renglón, un
hecho con caminos cuesta tres. Se llega a diez porque **los buenos son los últimos dos o tres** —
los primeros siete son obvios. Los que quedan sin semillas están en reserva y no cuestan nada.

El paréntesis final no es decoración: dice que **las semillas son ejemplos, no la lista**.

> Manda esto sobre `session-structure.md` de `halo-session-prep`, que sigue pidiendo 3-5 secretos
> con los caminos pre-escritos. Decisión del DM, 2026-09-12. Ver `docs/lazy-dm-manual.md` §2.4,
> que ya lleva la tercera línea.

### Dónde vive cada secreto: repartidos, no apilados

Escribirlos bien no basta: **una lista de diez al principio del plan no se lee en mesa.** El DM
está dirigiendo la escena A y los secretos están cuatro pantallas arriba, así que no salen. Eso
fue justo lo que pasó en la primera corrida — diez secretos impecables y ninguno colgado de nada.

La forma correcta son **dos sitios a la vez**:

1. **En cada escena, al final del bloque:** una sección corta
   `SECRETOS QUE PUEDEN SALIR AQUÍ`, con el número, una línea de qué es y **la semilla concreta
   de esta escena**. Nada más — el «qué cambia» no se repite.
2. **Al FINAL del plan, un bloque `texto` de referencia** con los diez completos (hecho +
   semillas + qué cambia + `DÓNDE`), y un `checklist` hijo de diez casillas para tachar los que
   salieron.

```
▸ 2 · ESCENA A            …texto de la escena…
                          SECRETOS QUE PUEDEN SALIR AQUÍ
                          · 3 · La leva no quiere estar ahí → disparan alto a propósito
                          · 6 · Hay otro camino → Chana lo suelta si PREGUNTAN
▸ 6 · LOS DIEZ SECRETOS   [texto]  badge «DM · referencia»   ← el almacén, al final
    └ Cuáles salieron     [checklist]  10 casillas
```

Un secreto puede aparecer en **dos** escenas con semillas distintas: eso es una virtud, no una
duplicación. Lo que no puede es aparecer en **ninguna** — si no supiste decir en qué bloque cae,
la que falla es la semilla, no el sitio.

**Y el «DÓNDE» se escribe en la ficha del secreto**, no solo en la escena: es lo que te deja
mover el secreto cuando la mesa se salta esa escena entera.

---

## P5 · El clímax

Es lo único que la gente se lleva. Si el reglamento del clímax es **`fm`**, el orden del
`docs/flee-mortals-manual.md` §2:

1. **La forma antes que los bichos** — una plantilla de roles (§3). Regla dura del libro: *«we
   recommend not using more than three unfamiliar stat blocks»*, y un combate donde todos comparten
   rol es un combate aburrido.
2. **Gastar** — sumar CR hasta el presupuesto, sin pasar el cap por criatura. Minions cuentan
   fraccionados.
3. **Villain actions** en arco *opener → control → ult* (§6), del campo `legendary` del statblock.
4. **Capa de entorno** — uno o dos rasgos a las criaturas locales, lair actions al jefe si el sitio
   es su guarida. Es lo que separa «tres ogros» de «tres ogros en una alcantarilla».

> ⚠️ **El selector de Entorno NO guarda nada** (PR #526). Vive en *Encuentros → Armar → reglamento
> «Flee, Mortals! · CR» → Entorno*, da los rasgos y lair actions verbatim **y ahí se acaba**: no los
> aplica a ninguna criatura ni se persisten con el encuentro. Cambiar a `fm` es además **lo único**
> que hace aparecer esa tarjeta.
>
> Por eso los rasgos elegidos **se copian a un bloque `texto` hijo del bloque `encuentro`**. Si no,
> el martes no están.

**Filtrar por `source === 'FleeMortals'` no es opcional:** 36 nombres chocan con XMM y **no son la
misma criatura** — el Kraken de FM es CR 26 y el de XMM, 23.

### El clímax no puede ser la primera pelea con un jefe encima

La regla de los «tres statblocks desconocidos» empuja a reciclar, y reciclando se llega sola a la
trampa: el combate 1 son Soldiers + Artillery + minions, y el clímax son **los mismos** más el
villano. En la hoja se ve distinto —sube el CR— y **en la mesa es la misma pelea otra vez**.

**Compara el histograma de ROLES, no el CR.** Si los dos encuentros comparten más de la mitad de
sus roles, todavía no tienes dos combates.

| | Escena A | Clímax |
|---|---|---|
| ❌ mal | 3 Soldier · 2 Artillery · 10 Minion | 1 Leader · 3 Artillery · **2 Soldier** · 10 Minion |
| ✅ bien | 3 Soldier · 2 Artillery · 10 Minion | 1 Leader · **5 Artillery** · **1 Brute** · 10 Minion |

Lo que cambió en el ✅ no es el número: es que **desaparecieron los Soldiers**. La escena A era una
pared de cuerpos en un pasillo —se avanza matando—; el clímax es campo abierto bajo fuego con un
solo enemigo en el suelo, y ése no viene a hacer daño sino a **agarrar y tirar** al que lleva el
objetivo. Mismo CR, misma mesa, otra pelea.

Tres preguntas que separan dos combates de verdad:

1. **¿De dónde viene el daño?** Del cuerpo a cuerpo ↔ de arriba, a distancia.
2. **¿Qué resuelve el combate?** Matar a todos ↔ un reloj que no depende de matar.
3. **¿Dónde está el enemigo?** En tu cara ↔ donde no lo alcanzas sin pagar algo.

Si las tres respuestas se repiten, cambia la plantilla de roles antes de tocar el presupuesto.

### El cierre necesita una decisión, no un epílogo

Ganar no es un final. Un cierre de «cayó la puerta, ¿qué hace tu personaje?» le pide a la mesa que
genere sola la emoción que el plan no le dio. **Lo que cierra una one-shot es un precio**, y el
sitio barato de ponerlo es en la propia victoria: lo que usaron para ganar es lo que rompe algo
que querían.

El molde, y cabe en quince minutos:

1. **La victoria, leída en voz alta, con el daño dentro.** El fuego que abrió la puerta está
   comiéndose el grano que venían a salvar.
2. **Tres cosas, dos manos.** Nómbralas tú —no preguntes «¿qué hacen?»— y dales UNA ronda: el
   grano, las familias, el villano que se escapa. **Dos.** Treinta segundos para discutirlo.
3. **El villano no pide clemencia.** Que termine su frase. Si tenía un argumento, éste es el
   momento en que resulta que tenía razón en algo.
4. **Un epílogo por lo que soltaron**, una frase cada uno, escritos de antemano. Que se note que
   lo que eligieron cambió la ciudad.
5. **Y ENTONCES** la vuelta de preguntas por jugador. Al final, no en lugar de.

Si el punto 2 no existe, el cierre es una ceremonia. Y si las tres cosas no son cosas que la mesa
**ya sabía que le importaban** —porque un secreto se las puso delante en la escena B—, es una
sorpresa barata en vez de una decisión.

### Los peligros son presupuesto gratis

`encuentros.hazards` es un array de `{id, name, type, round}` con `type ∈ always | start | mid |
end`, y se **persiste con el encuentro**: se escribe al armarlo y aparece en el tracker de combate,
en el panel PELIGROS. No cuesta CR, así que es la palanca para apretar un clímax que ya está en el
filo del presupuesto sin meter otro cuerpo en la iniciativa.

Cómo se escriben:

- **`always`** — las dos o tres reglas que gobiernan el espacio y que el DM olvida en la ronda 3:
  quién tiene cobertura, qué le cuesta al que lleva el objetivo. Son recordatorios, no daño.
- **Uno por ronda, y que escale**: entra alguien en R2, el terreno cambia en R3, arde en R4, se
  acaba en R5. Un `hazard` por ronda le da al clímax una forma que se oye.
- **Al menos uno a favor de la mesa.** El humo del aceite que ellos mismos provocaron les da media
  cobertura. Si los cinco peligros son castigo, es una lista de multas.
- **Nombre corto y accionable**, con el número: `«R2 · Aceite hirviendo: 10 pies frente a la
  puerta, 2d6 al entrar o terminar ahí»`. El campo es una línea que se lee de un vistazo, no un
  párrafo.

Si el reglamento es `dnd2024`, el clímax se arma igual pero sin roles ni villain actions; la
ficción la gobierna el Encounter Axis de `dnd-worldbuilder`.

---

## P6 · Alta en la app

**Nunca escribas en Supabase sin confirmación del DM.** Procedimiento, tablas, ids vigentes y la
mesa del reskin: **`references/alta-en-la-app.md`**.

Qué se da de alta: `lugares` · `npcs` · `items` · `mapa_nodos` + `mapa_pines` · `encuentros` ·
`quests` (la paraguas) · `monstruos` (solo si hay reskin con nombre propio).

Antes de escribir un solo `cf_*`, lee el overlay de la campaña. Un `cf_*` que no esté declarado
**se guarda y no se ve**. En `one-shots` ya existen los dos que importan:

```sql
select section, overlay->'customFields' from entity_schemas where campaign_slug = 'one-shots';
-- npcs    → cf_statblock, cf_rasgos, cf_inspiracion
-- lugares → cf_lugar_padre, cf_lectura, cf_mecanica
```

Y tira del compendio antes de escribir a mano: **1.047 mapas** indexados, **1.055 lugares con su
read-aloud** y **5.866 NPC cards** con esquema espejo de la tabla `npcs`, importables desde la app.

---

## P7 · El árbol

El plan modular, que **es** el entregable. Plantilla completa, JSON listo y el `UPDATE`:
**`references/plantilla-arbol.md`**.

La forma, a grandes rasgos:

```
☑ SEGUIMIENTO                       [checklist]  badge «EN MESA» · el TRACKER de la sesión
▸ 1 · APERTURA                      [texto]      badge «0:00 · 20 min»  · …y EL ENCARGO
▸ 2 · Escena A                      [texto]      badge «0:20 · 45 min · ✂»
    ├ <Lugar> [lugar] · <Plano> [mapa] · <Encuentro> [encuentro]
▸ 3 · Escena B                      [texto]      badge «1:50 · 45 min · ✂»
    ├ ¿De dónde sale <la pieza>?    [rama]       └ Ruta 1 ★probable · Ruta 2
    └ <La pieza> [tesoro]
▸ 4 · CLÍMAX                        [texto]      badge «2:50 · 60 min · NO SE CORTA» · rojo
    ├ <Villano> [npc] · <Encuentro final> [encuentro]
    │   └ Villain actions · Entorno  [texto]     ← porque el selector no los guarda
▸ 5 · CIERRE                        [texto]      └ <Quest> [quest]
▸ 6 · LOS DIEZ SECRETOS             [texto]      badge «DM · referencia» — el almacén, AL FINAL
    └ Cuáles salieron               [checklist]  10 casillas
```

**El checklist de arriba es un tracker, no una lista de tareas.** Lo de preparar —horas, party,
pendientes— se hace una vez y cabe en tres líneas al principio de la apertura. Lo que el DM mira
cada veinte minutos es **qué ya pasó**: un punto por beat, en orden, con los estados alternativos
escritos (*«el villano: muerto / preso / huido»*).

Dos cosas que **no** hay que construir, porque ya existen:

- **El reloj es el `badge`.** `PrepBloque` tiene `badge` y `badgeColor` libres y editables desde la
  tarjeta. No hace falta un campo de duración.
- **No hay tipo `secreto`, y es a propósito** (spec 007, FR-012b: gancho/escena/secreto/pista eran
  cinco etiquetas para la misma cosa —prosa con título—). Los diez hechos son un `texto` con un
  `checklist` hijo.

### El planeador NO renderiza markdown

Medido en `react/prep/cuerpos/texto.tsx`: el cuerpo de un bloque `texto` monta el motor vanilla
`textToContentEditable`, que hace **tres cosas y ninguna más** — escapa HTML, convierte
`@[Nombre](seccion:uuid)` en un chip, y `\n` en `<br>`. **`**negritas**` sale con los asteriscos
puestos**, y un plan lleno de `**` es un plan que el DM lee con basura encima.

Escribe en texto plano, con la tipografía que sí sobrevive:

```
MAYÚSCULAS para las etiquetas de sección      QUÉ QUIEREN:  ·  LEE EN VOZ ALTA:
·  para viñetas                               · Nah-Ual — Fog Cloud sobre el patio
────────────────────────────────  para separar bloques de la misma tarjeta
«comillas angulares» para lo que se lee en voz alta
sangría de 4 espacios para la segunda línea de una viñeta
```

### Las menciones son el único resaltado que la app entiende

Y son mejores que la negrita, porque además **enlazan**: el chip abre la ficha al hacer clic y
enseña un preview al pasar por encima. El formato es literal, se escribe a mano en el campo:

```
@[Nombre exacto](seccion:uuid)
```

Las siete secciones válidas (`MENTION_SOURCES` en `app.js`, y la lista real se lee de ahí):

| sección | tabla |
|---|---|
| `npcs` `ciudades` `establecimientos` `lugares` `items` `quests` | la del mismo nombre |
| `personajes` | `players` — ojo: la **sección** es `personajes`, la **clave** es `players` |

**Dónde se pintan y dónde no** — esto se mide, no se supone:

| campo | ¿pinta el chip? | por qué |
|---|---|---|
| `texto` de un bloque `texto` o `nota` | **sí** | `CuerpoTexto` monta el motor de menciones |
| `items[].t` de un `checklist` | **NO** | `CampoEditable` escribe `textContent` pelado |
| `titulo` de cualquier bloque | **NO** | idem |
| `texto` de una `rama` / `ruta` | **NO** | `CuerpoRama` también usa `CampoEditable` |

O sea: una mención en un checklist o en un título **se ve como `@[Chana Tepetl](npcs:9717…)`**, en
crudo, en mitad del plan. Ahí va el nombre a secas.

Dos reglas de escritura, y las dos salieron de regarla:

- **No le pongas artículo delante si el nombre ya lo trae.** `el @[El campanario de Belén](…)` se
  lee «el El campanario». Barrido: `grep -Ei '(el|la|los|las|del|al) @\[(El|La|Los|Las) '`.
- **La primera vez el nombre completo, después el corto.** El chip repetido doce veces en un
  párrafo lo vuelve ilegible; menciona la entidad donde el DM necesita saltar a la ficha, no cada
  vez que la nombras.

**Antes de escribir menciones, resuelve los uuid de una sola consulta** y guárdalos en constantes:
inventar un uuid no falla —se guarda igual— y produce un chip que no abre nada.

---

## P8 · Verificación

Aplica `verification-before-completion`: **evidencia antes de afirmar**, y también cuando el
veredicto sea «no hace falta».

- [ ] **La cadena cierra.** Lee las tres líneas de cada escena en seco, sin el contenido: el «qué se
      llevan» de cada una encaja con el «qué la dispara» de la siguiente. Es el chequeo más barato
      de los ocho y el que caza las roturas gordas.
- [ ] **Cada secreto tiene su «qué cambia»**, y cambia de verdad una decisión, una opción táctica o
      el trato con alguien. El que no, se borra.
- [ ] **Cada secreto está colgado de al menos una escena**, y el bloque de referencia está al FINAL
      del plan, no al principio.
- [ ] **Cero `**` en el plan.** `grep -c '\*\*'` sobre los `texto` tiene que dar 0: el planeador no
      renderiza markdown.
- [ ] **Todas las menciones resuelven**, y ninguna está en un `checklist`, un `titulo` o una `rama`
      —ahí se ven en crudo—. Consulta de barrido en `references/alta-en-la-app.md` §Menciones.
- [ ] **Los dos combates no comparten la mitad de sus roles.** Compara el histograma, no el CR.
- [ ] **El clímax tiene peligros**, al menos uno de ellos a favor de la mesa.
- [ ] Cada `refId` / `encuentroId` / `mapaId` del árbol resuelve a una fila viva. **No son claves
      foráneas** — viven dentro de un jsonb y la base no los valida; si la entidad se borra el
      bloque queda huérfano y solo lo dice la UI.
- [ ] Los ids de `encuentros.monsters` resuelven, y con la fuente correcta.
- [ ] Los `cf_*` escritos están en el overlay de `one-shots`.
- [ ] **Los valores de los nueve campos `select` están dentro de su enum.** La base no los valida y
      el formulario los pinta en blanco. Comando y tabla en `references/alta-en-la-app.md`
      §Los selects rígidos.
- [ ] El plan es modular: `jsonb_typeof(bloques) = 'array'`. Un objeto lo manda al render legacy.
- [ ] Los `id` de bloque son únicos dentro del plan, y `hijos` es un array en todos.
- [ ] Auditoría de peninsularismos (`references/espanol-mexicano.md`).
- [ ] La suma de los badges de tiempo cabe en las horas de P0.

**Verifica contra el motor, no contra tu lectura del motor:**

```bash
node -e "const ES=require('./entity-schema.js'); …ES.effectiveSchema(baseline, overlay, {isDM:true})"
node -e "const A=require('./srd-adapters.js'); A.bestiarioRowById('srd:Scarecrow')"
```

Medido el 2026-09-13: `Kraken` existe en **dos** fuentes con CR distinto (`FleeMortals` 26,
`XMM` 23) y `Ankheg` en dos con el mismo CR pero **solo una con rol de FM**. Un id sin fuente
elige por ti, y la diferencia llega hasta el semáforo de dificultad.

**Y el catálogo se mueve.** La versión anterior de esta skill decía que `srd:Scarecrow` resolvía a
`WttHC`; hoy `Scarecrow` solo está en `XMM` (y en `MM` dentro de `bestiary-aventuras.json`). Por
eso el comando se **corre**, no se cita de memoria — incluidas las dos líneas de arriba.

---

## Reglas duras

### 1 · Idioma: español mexicano simple

Chrome, notas y explicaciones en español mexicano. **Nombres propios y términos de reglas en
inglés verbatim** (Chalet Brantifax, Scarlet Sash, *charm of heroism*, Sacred Flame). Los
read-aloud van como paráfrasis en español, marcada como tal.

**Auditar, no confiarse.** Lista y comando en `references/espanol-mexicano.md`.

Y no es solo vocabulario: **es la sintaxis**. Traducir la prosa florida del módulo frase por frase
es fiel y a la vez ilegible para leer en voz alta. Frases cortas, una idea por frase.

### 2 · Modelar al grano del módulo, no más fino

17 salas → 17 `lugares` con pin. Pero los textos completos NO se duplican en el árbol: viven en su
ficha, y el bloque `lugar` la lee en vivo. Una locación con 3 cuartos irrelevantes no necesita 3
filas.

### 3 · Un campo vacío puede ser una decisión del autor

El barón de *Book of the Raven* va **sin statblock** porque el módulo dice que su espíritu no puede
manifestarse. Un default por vocación habría convertido un duelo en un encuentro. **No
autocompletes sin decirlo.**

### 4 · Validar una mecánica también exige evidencia

Si durante la preparación surge la duda de si algo funciona, **lee la regla COMPLETA, sin truncar**,
y **enumera casos, no muestrees uno**. Prohibido el slice (`[:N]`, `head`) sobre contenido de
reglas: una feature 2024 suele tener varios beneficios y el que importa puede estar al final.

---

## Trampas de verificación

Las tres dieron falsos negativos en una verificación real:

| Trampa | Síntoma | Regla |
|---|---|---|
| `text-transform: uppercase` | «la etiqueta no aparece» pero el contenido sí | `innerText` de Chromium **aplica** la transformación: compara insensible a mayúsculas |
| Presencia ≠ visibilidad | «el modal sigue encima» tras arreglarlo | Exige `getBoundingClientRect()` con área > 0: las pestañas ocultas siguen en el DOM |
| Hidratación diferida | `DATA.mapas` devuelve `[]` | Espera con `waitForFunction`, no lo leas justo tras `#app.visible` |

## Señales de que la vas a regar

- Empezaste a escribir contenido sin saber cuántas horas dura la sesión
- **Escribiste prosa antes de que la cadena cerrara en seco**
- **No sabes decir quién le dice el plan a los jugadores, ni en qué minuto**
- **El villano del clímax no ha sido nombrado, oído ni visto antes del minuto 90**
- Escribiste el árbol antes de clasificar la fuente (carril A)
- Planeaste cinco escenas para tres horas
- Ninguna escena intermedia tiene costura de corte
- **Un secreto no sabe decir qué cambia si la mesa lo descubre**
- **Los diez secretos están al principio del plan y ninguna escena los menciona**
- **El clímax es el combate de la escena A con un jefe encima**
- **Escribiste `**negritas**` en un bloque del planeador**
- **Metiste una mención en un checklist o en un título**
- **Una escena arranca porque los jugadores «tienen curiosidad», sin que nadie les pida nada**
- **Un aliado suelta información en una escena a la que nunca lo hiciste llegar**
- **La mesa necesita un objeto y el plan no dice quién sabe dónde está**
- **El cierre es un epílogo con preguntas, sin una sola decisión**
- Los secretos dicen «si hablan con X» en vez del hecho
- Escribiste `cf_*` sin haber leído el overlay de esa campaña
- **Inventaste un valor para un campo `select` porque el enum no tenía el tuyo**
- Elegiste `fm` y no copiaste los rasgos de entorno a un bloque
- Diste por buena una fila porque el `INSERT` no dio error
- **Buscaste un mapa de exteriores en un catálogo de interiores, dos veces**
- Te sonó natural escribir «coger», «vosotros» o «desván»
- Estás inventando un NPC que el módulo ya trae (carril A)
- Estás copiando un nombre oficial sin reskinear (carril B)

**Todas significan: regresa al paso que te saltaste.**

## Referencias

- `references/carril-b-original.md` — la musa y el reskin, paso a paso
- `references/plantilla-arbol.md` — el árbol completo, el JSON y el `UPDATE`
- `references/alta-en-la-app.md` — tablas, ids vigentes, overlay, la mesa del reskin
- `references/verificar-contenido.md` — comprobar que el módulo y sus criaturas resuelven
- `references/espanol-mexicano.md` — peninsularismos y comando de auditoría
- `references/artifact-guia.md` — **solo si el DM pide una página**; no es el entregable

## Manuales del repo (QuestKeep)

Estos mandan sobre esta skill en su terreno. Léelos, no los cites de memoria:

- `docs/lazy-dm-manual.md` — §2.9 (aventura publicada + el reloj del one-shot), §2.4 (secretos),
  §5 (correr la mesa), §6 (combate sin rejilla), §8 (reskin)
- `docs/flee-mortals-manual.md` — §2 (procedimiento), §3 (roles), §4 (presupuesto), §5 (minions),
  §6 (villain actions), §7 (entornos), §8 (villain parties)
- `specs/007-planeador-modular/data-model.md` — la forma exacta del bloque
