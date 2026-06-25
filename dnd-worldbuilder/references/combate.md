# Combate — Referencia de Entidad

Un **combate** no es un saco de HP vs party. Es un espacio de decisiones multi-dimensional
con objetivo claro, ventajas descubribles, riesgos calculables y elementos impredecibles.
Framework: **Encounter Axis**.

## Campos en Supabase

El combate vive distribuido en dos bloques del `session_plan`:

| Bloque | Qué guarda |
|--------|-----------|
| `bloque_escenas[]` con `tipo: "combate"` | El **encuentro** (protein + ejes + espacio) |
| `bloque_monstruos[]` | Los **monstruos** del encuentro (IDs del catálogo, reskins opcionales) |

Schema: 1 entrada en `bloque_escenas` + N entradas en `bloque_monstruos` por combate.
El schema de `bloque_escenas` para combates **extiende** el genérico con un campo `ejes` JSONB
(ver sección "Output" abajo).

## Contexto requerido (inputs)

Antes de diseñar, la skill necesita:

- **Party composition** — # jugadores, clases, niveles *(obligatorio)*. Si viene via
  `halo-session-prep`, se saca de `personajes`. Si es invocación directa, **pedirlo al DM**.
- **Ubicación / entorno** — lugar del combate *(obligatorio)*. Afecta qué monstruos y qué
  ejes tienen sentido.
- **Tono / quest context** — qué busca la escena (boss fight, persecución, revelación).
- **Catálogo de monstruos** — la skill lo consulta directo en Supabase (tabla `monstruos`).

Si falta cualquier obligatorio, **preguntar antes de diseñar**. Nunca asumir.

---

## Filosofía: Encounter Axis Framework

Cuatro principios core:

- **Novelty** — cada combate ofrece algo nuevo (no repetir la misma dinámica)
- **Autonomy** — los jugadores eligen cómo atacar el problema, no solo "quién golpea a quién"
- **Avoid the Slog** — las múltiples decisiones evitan el deathmatch tedioso
- **Clarity** — los ejes siempre son visibles/descubribles → decisiones informadas

### La Regla de Tres *(obligatoria)*

**1 Protein + 2 ejes adicionales = mínimo.** Resultado: 5 × 5 × 5 = 125 outcomes posibles.
Los 3 ejes deben ser descubribles por los jugadores. Si un eje es invisible, no cuenta.

---

## El menú de ejes (4 categorías)

### Proteins (Objetivos) — condición que cierra el encuentro

8 opciones:

1. **Kill Them** — matar a todos. ⚠️ Incluir siempre un *retreat number* (HP% o # bajas en
   que los enemigos huyen) para evitar el slog.
2. **Kill the Target** — matar a UN objetivo específico (boss fight, asesinato). Los demás
   son obstáculos, no objetivos.
3. **Protect the Target** — defender NPC/objeto X rondas o hasta que escape a zona segura.
4. **Stop the Flood** — cortar origen de oleadas (bloquear entradas, destruir puentes). No
   hay que matar a todos.
5. **Escape** — distanciarse de perseguidor o salir de zona peligrosa (cueva colapsando).
6. **Stop the Ritual** — interrumpir evento mágico con timer. "Puzzle dentro del combate."
7. **Get the MacGuffin** — tomar objeto **móvil** y salir.
8. **Pull the Lever / Destroy the Nexus** — versión **estática** del MacGuffin: activar/romper
   interruptor, portal, cristal, nexo.

### Optimizers (Ventajas tácticas) — no cierran el combate pero dan ventaja

6 opciones:

1. **The High Ground** — elevación da ventaja a quien ataca desde arriba, desventaja desde abajo.
2. **The Stash** — zona con recursos (pociones, pergaminos, munición) descubribles.
3. **The BIG Gun** — equipo de asedio (ballista, cañón) que permite pegar por encima del nivel.
4. **Levers 'n' Traps** — defensas del villano que los PCs pueden tomar (jets de fuego,
   calderos de ácido suspendidos).
5. **Boons** — mejoras temporales o zonas especiales (fuente mágica +1, Haste zone).
6. **Reinforcements** — alarma/cuerno para llamar aliados; cambia los números del campo.

### Hazards (Riesgos ambientales) — dañan/limitan movimiento

4 categorías:

1. **No-Go Zones** — peligro mortal obvio. Grieta masiva, borde de skyship: caer = muerte.
2. **Vats of Acid** *(categoría con variantes)* — daño inmediato con chance de escapar antes
   de morir. Variantes: lava, electric eels, Pit of Creatures.
3. **Frogger** — peligros en movimiento que se pueden esquivar: estampida, río embravecido,
   tráfico urbano durante el combate.
4. **Thin Ice** — stages progresivos (stable → cracked → broken). Criatura Large agrieta
   automático; Medium solo si salta o golpea con arma pesada. Adaptable: techos de vidrio,
   puentes de cuerda, glifos mágicos.

### Chaos (Elementos impredecibles) — cambian la dinámica

7 opciones:

1. **Fire** — material inflamable cerca. "Universalmente entendido y algo irresistible."
2. **Lights Out** — oscuridad mágica, niebla. Empareja bien con Pull the Lever.
3. **The Random Stash** — stash sin etiquetas. Poción de curación o AoE dañino, al azar.
4. **Bring It Down** — destruir soportes estructurales (mina, ruinas, airship engines).
5. **Unlabeled Levers** — defensas enemigas sin etiquetas: adivinar el efecto.
6. **Free Them** — liberar criaturas enjauladas (elementales, vampiros) que atacan a cualquiera
   en orden aleatorio.
7. **Activate It** — orbe/cristal vago. Puede ser Wild Magic Surge o Dead Magic Zone.

---

## Dificultad (D&D 5e DMG 2024 — XDMG)

Tres tiers. **Sin multiplicador** por cantidad (regla 2024 simplificada — ya no existe el
ajuste de XP por # de enemigos del 2014).

- **Low** — 1-2 momentos tensos, salen victoriosos sin bajas (pueden gastar curación)
- **Moderate** — sin curación puede irse mal. Débiles caen, pequeña chance de muerte
- **High** — letal para ≥1 PC. Requiere tácticas + algo de suerte

### XP Budget per Character (XDMG 2024)

| Nivel PC | Low    | Moderate | High   |
|----------|--------|----------|--------|
| 1        | 50     | 75       | 100    |
| 2        | 100    | 150      | 200    |
| 3        | 150    | 225      | 400    |
| 4        | 250    | 375      | 500    |
| 5        | 500    | 750      | 1,100  |
| 6        | 600    | 1,000    | 1,400  |
| 7        | 750    | 1,300    | 1,700  |
| 8        | 1,000  | 1,700    | 2,100  |
| 9        | 1,300  | 2,000    | 2,600  |
| 10       | 1,600  | 2,300    | 3,100  |
| 11       | 1,900  | 2,900    | 4,100  |
| 12       | 2,200  | 3,700    | 4,700  |
| 13       | 2,600  | 4,200    | 5,400  |
| 14       | 2,900  | 4,900    | 6,200  |
| 15       | 3,300  | 5,400    | 7,800  |
| 16       | 3,800  | 6,100    | 9,800  |
| 17       | 4,500  | 7,200    | 11,700 |
| 18       | 5,000  | 8,700    | 14,200 |
| 19       | 5,500  | 10,700   | 17,200 |
| 20       | 6,400  | 13,200   | 22,000 |

**Cómo se usa (3 pasos oficiales XDMG):**
1. Elegir dificultad (Low / Moderate / High)
2. Calcular budget: `budget = valor_tabla × # PCs`. Ej: 5 PCs nivel 3, Moderate → 225 × 5 = 1,125 XP
3. Gastar el budget sumando XP de monstruos del catálogo, sin pasarse (OK dejar unos pocos
   XP libres)

**Troubleshooting oficial XDMG** — avisar al DM si aplica:

- **>2 criaturas por PC** → incluir criaturas frágiles (crítico en niveles 1-2)
- **CR 0** → usar con moderación, preferir swarms del MM
- **Máx 2-3 stat blocks distintos** por encuentro (más = difícil de correr en mesa)
- **CR > nivel del party** → riesgo alto de one-shot a un PC; advertir explícitamente
- **Features imposibles** de contrarrestar por el nivel del party → considerar no usar

---

## Proceso de diseño (8 pasos)

### 1. Recolectar contexto

Si viene de `halo-session-prep`, está servido. Si es invocación directa, pedir al DM lo
obligatorio (party, ubicación). **No asumir** defaults.

### 2. Preguntar dificultad

Mostrar los 3 tiers (Low / Moderate / High) al DM y pedir elección.

### 3. Calcular budget y consultar catálogo

Calcular `budget = valor_tabla × # PCs`. Consultar `monstruos` filtrando por CR apropiado
al budget y por `entorno` coherente con la ubicación:

```sql
-- ⚠️ `cr` es un STRING con XP embebido ("2 (XP 450; PB +2)") — NO uses `cr::text = ANY(...)`,
-- devuelve vacío. Filtra con LIKE. `entorno` son listas en inglés (Urban, Forest…). Los
-- statblocks NPC (Bandit, Tough, Bandit Captain, Mage, Gladiator…) salen por tipo Humanoid.
SELECT id, nombre, tipo, tamano, cr, entorno, hp, ac, rasgos, acciones
FROM monstruos
WHERE NOT archived
  AND (cr LIKE '1 (%' OR cr LIKE '2 (%' OR cr LIKE '3 (%'
       OR cr LIKE '4 (%' OR cr LIKE '5 (%')               -- ajustar al budget
  AND (entorno ILIKE '%Forest%' OR tipo ILIKE '%Humanoid%')  -- ajustar a ubicación
ORDER BY nombre;
```

### 4. Proponer 2-3 combos de monstruos

Al DM, con rol táctico y XP total:

> **Combo A** (Moderate, budget 3,000): 1 Cult Fanatic (450) + 4 Cultists (25×4) + 2 Shadows (100×2) = **750 XP**. *Rol:* Fanatic canaliza en el centro, cultistas son distractores frágiles, shadows flanquean desde el techo.
>
> **Combo B** (Moderate): ...
>
> **Combo C** (Moderate): ...

DM elige. Si el combo elegido requiere reskin (flavor nuevo manteniendo stat block), aplicar
las 3 capas sensoriales del paso 8 al monstruo reskineado.

### 5. Proponer 3 Proteins

La skill ofrece **siempre 3 variantes** coherentes con los monstruos y la ubicación:

> 1. **Stop the Ritual** — el Fanatic canaliza; 3 rondas antes de invocación
> 2. **Kill the Target** — matar al Fanatic, los cultistas huyen al caer él
> 3. **Escape** — los PCs deben extraer al rehén antes de que llegue la entidad

DM elige. Si eligió **Kill Them**, definir *retreat number* (ej: "cultistas huyen cuando el
Fanatic cae o si pierden 50% de su número").

### 6. Proponer 4 ejes adicionales

Mezcla de Optimizers / Hazards / Chaos coherentes con el espacio y el Protein elegido:

> 1. **[Optimizer] The Stash** — pergaminos de Counterspell en la sacristía norte
> 2. **[Hazard] Thin Ice** — glifos en el piso se agrietan con críticos; 3 grietas = colapso
> 3. **[Chaos] Fire** — braseros encendidos; tapiz-sello inflamable al centro
> 4. **[Hazard] No-Go Zone** — pozo sin fondo en la esquina sur (caer = muerte)

DM elige **2**. La Regla de Tres queda cumplida (Protein + 2 ejes = 3 dimensiones).

### 7. Narrar el espacio

Mapa mental breve (texto, 3-5 oraciones): dónde vive cada eje, qué señales lo hacen
descubrible por los PCs sin anunciarlo. El DM debe poder visualizar la sala al leerlo.

### 8. Proponer las 3 capas sensoriales del monstruo-Protein

**Proactivamente**, ofrecer al DM:

- **Primera señal** — lo que perciben ANTES de verlo (rastros, olores, sonidos en el entorno
  previo). Construye tensión.
- **Encuentro visual** — la escena cinematográfica al verlo por primera vez. Incluir *detalle
  ancla* memorable (lo que los jugadores van a repetir).
- **Comportamiento en combate** — prioridades tácticas, patrones observables, reacción al
  daño. No stats — comportamiento.

El DM acepta, modifica o descarta. Si el Protein es `Kill Them` (sin target único), aplicar
las 3 capas al monstruo más representativo del grupo.

---

## Output

### A) Escena (→ `bloque_escenas[]`)

Schema extendido con campo `ejes`:

```json
{
  "tipo": "combate",
  "objetivo": "string narrativo del Protein (lo que el DM narra como condición de cierre)",
  "obstaculo": "string narrativo de los obstáculos principales",
  "espacio": "mapa mental breve — dónde está cada eje en la sala",
  "ejes": {
    "protein": {
      "tipo": "Stop the Ritual",
      "descripcion": "El Cult Fanatic canaliza la invocación de una entidad mayor",
      "condicion_cierre": "Interrumpir el cast antes de la ronda 4, o matar al Fanatic",
      "retreat_number": null
    },
    "optimizers": [
      {
        "tipo": "The Stash",
        "descripcion": "3 Pergaminos de Counterspell en la sacristía norte",
        "como_descubrirlo": "INT (Arcana) DC 12 al mirar hacia el norte, o registrar activamente"
      }
    ],
    "hazards": [
      {
        "tipo": "Thin Ice",
        "descripcion": "Glifos mágicos en el piso conectados al círculo ritual",
        "stages": [
          "stable: el piso aguanta",
          "cracked: tras un crítico o peso Large, una sección se agrieta",
          "broken: 3 secciones rotas = colapso al nivel inferior donde duerme una criatura"
        ]
      }
    ],
    "chaos": [
      {
        "tipo": "Fire",
        "descripcion": "Braseros encendidos cerca del tapiz-sello inflamable",
        "trigger": "Si un PC usa fuego en zona o si un monstruo es empujado hacia un brasero"
      }
    ]
  }
}
```

### B) Monstruos (→ `bloque_monstruos[]`)

Schema existente (sin cambios). Si se aplicaron las 3 capas opcionales (paso 8), van en los
campos `reskin_*`:

```json
{
  "monstruo_id": "uuid del catálogo",
  "nombre": "nombre narrativo (original o reskineado)",
  "cantidad": 2,
  "flag": "match_directo | reskin",
  "contexto_narrativo": "rol táctico en el combate, prioridades",
  "reskin_primera_senal": "... o null si match_directo sin reskin",
  "reskin_encuentro": "... o null",
  "reskin_comportamiento": "... o null"
}
```

---

## Checklist de calidad

- [ ] 1 Protein claro que cierra el encuentro
- [ ] ≥2 ejes adicionales (llega a ≥125 outcomes — Regla de Tres)
- [ ] Cada eje es descubrible por los jugadores (clarity)
- [ ] Cada eje ofrece decisión significativa (autonomy)
- [ ] Si Protein = Kill Them → *retreat number* definido
- [ ] Hazards con stages cuando aplique (no binarios)
- [ ] Chaos con trigger explícito (cuándo entra)
- [ ] Monstruos del catálogo: match directo > reskin > nunca inventar stat blocks
- [ ] Dificultad calibrada con tabla XP XDMG 2024 (sin multiplicador)
- [ ] El combate puede resolverse sin "kill them all" (salvo que el Protein lo exija)
- [ ] 3 capas sensoriales ofrecidas proactivamente para el monstruo-Protein
- [ ] Coherencia entre monstruos, ubicación y ejes elegidos

---

## Ejemplo completo

**Contexto:** 4 PCs nivel 5 (Mago, Pícaro, Clérigo, Bárbaro). Sala del ritual en templo
derruido del páramo. Quest: evitar que el culto de Vecna invoque una entidad mayor.

**Dificultad:** Moderate → budget = 750 × 4 = **3,000 XP**.

**Combo elegido:** 1 Cult Fanatic (450 XP) + 4 Cultists (25×4 = 100) + 2 Shadows (100×2 = 200)
+ 1 Priest (450) = **1,200 XP** (queda holgado — espacio para drama sin riesgo letal total).
*Nota: XP del MM 2014/24 — siempre verificar contra la tabla `monstruos` del catálogo.*

**Protein:** **Stop the Ritual.** Cult Fanatic canaliza en el centro. En la ronda 4, si no
fue interrumpido, la entidad llega y el combate termina (la sesión cambia de rumbo).
Condición de cierre: romper el círculo (DEX DC 15 con daño arcano), matar al Fanatic, o usar
un Counterspell.

**Ejes adicionales (2 de los 4 propuestos):**

1. **[Optimizer] The Stash** — En la sacristía al norte hay 3 Pergaminos de Counterspell.
   *Cómo descubrirlo:* visibles si alguien entra a la sacristía (puerta abierta, ven estantes);
   también INT (Arcana) DC 12 al entrar a la sala principal detecta residuo mágico "fresco"
   hacia el norte.

2. **[Hazard] Thin Ice** — El piso es una red de glifos mágicos conectados al círculo central.
   *Stages:* (a) estable en condiciones normales; (b) cualquier crítico en combate agrieta
   una sección (el daño del glifo se vierte en el piso); (c) 3 secciones agrietadas → colapso
   y todos caen 15 pies al nivel inferior, donde duerme un Ogro encadenado (Chaos secundario
   no declarado de antemano).

**Espacio:**

> Sala octagonal de piedra gris. Círculo ritual en el centro, iluminado azul frío, con el
> Fanatic canalizando sobre un atril. 4 cultistas cantan en cada esquina (uno por esquina).
> 2 Shadows flotan cerca del techo, ignoradas por los cultistas. Al norte: puerta abierta a
> la sacristía (el Stash). Al sur: balcón con caída al páramo (15 pies). El piso brilla
> tenuemente — glifos ocultos visibles solo con magia o al mirar fijo.

**3 capas sensoriales (Cult Fanatic — el Protein):**

> **Primera señal:** Antes de abrir la puerta, el aire pesa como antes de una tormenta.
> Escuchan un cántico — no palabras que entienden, pero el ritmo se mete en el pecho.
> Los cristales del pasillo laten sincronizados con tu propio corazón, y eso te asusta.
>
> **Encuentro:** Abres la puerta y el cántico no se detiene. El Fanatic no te mira — tiene
> los ojos cerrados y sangra ligeramente por la nariz. En cada inhalación su voz se
> multiplica, como si otras voces le prestaran aire desde adentro. Viste una túnica
> manchada de algo que no es sangre: más oscuro, y se mueve.
>
> **Comportamiento:** Nunca ataca primero — canaliza. Si lo hieres, sigue canalizando
> (tirada de Concentración; DC = daño recibido). Solo si su HP baja a la mitad, abre los
> ojos — y ahí cambia todo: grita una orden a los cultistas que se vuelven suicidas
> (ataque con ventaja, ignoran defensa propia). Si llega a la ronda 3 del ritual sin ser
> detenido, levita, la voz se vuelve gutural, y la entidad **llega** — el combate termina
> y la sesión pivota a huir del templo colapsando.

---

## Notas de invocación

Esta referencia se carga desde `dnd-worldbuilder/SKILL.md` cuando:

- El usuario pide diseñar un combate directamente ("diseña un combate", "encuentro para la
  sesión", "pelea contra X", "haz un combate más interesante")
- `halo-session-prep` delega la generación del `bloque_escenas` tipo `combate` + su
  `bloque_monstruos` asociado (paso 4 de esa skill)

En invocación directa, seguir los 8 pasos tal cual. En invocación desde session-prep, el
contexto (party, ubicación, quest) ya viene servido — saltar al paso 2.
