# Plantilla — Estructura de Sesión

Esta plantilla genera el contenido que luego se commitea en `session_plans` (columnas `bloque_*`
separadas: `bloque_strong_start`, `bloque_escenas`, `bloque_secretos`, `bloque_npcs`,
`bloque_locaciones`, `bloque_tesoros`, `bloque_monstruos`).

El estilo es cinematográfico-directo (Matt Mercer al hablar, no al escribir) + principios de
Lazy DM y DMG 2024.

---

```markdown
# 📜 Propuesta Sesión — [Título narrativo de la sesión]

## ⚡ Apertura fuerte (bloque_strong_start)
[Una escena inicial concreta que lanza la acción de inmediato. Sin preámbulos.
Describe exactamente qué ven/oyen/sienten los jugadores al abrir los ojos en la sesión.
Debe tener al menos un detalle sensorial específico.
Ej: "La sesión abre con el estrépito de pasos en el pasillo del burdel —
los guardias ya saben que están ahí."]

## 🗺️ Escenas posibles (bloque_escenas)
[3-5 escenas como ingredientes. Cada una: objetivo claro + obstáculo. El DM no tiene
que usarlas todas ni en ese orden.]

- **[Nombre de escena]** — Tipo: [combate/social/exploración/misterio/revelación].
  Objetivo: [qué quieren lograr]. Obstáculo: [qué lo impide].
- **[Nombre de escena]** — Tipo: [...]. Objetivo: [...]. Obstáculo: [...].
- **[Nombre de escena]** — Tipo: [...]. Objetivo: [...]. Obstáculo: [...].

### Escenas de combate — Encounter Axis

Si una escena es `tipo: combate`, además del objetivo/obstáculo, debe incluir el campo
**`ejes`** (framework Encounter Axis — ver `../dnd-worldbuilder/references/combate.md`).
**Regla de Tres obligatoria:** 1 Protein + ≥2 ejes adicionales (Optimizers / Hazards / Chaos).

**Shape del campo `ejes` en la escena:**

```json
{
  "protein": {
    "tipo": "Kill Them | Kill the Target | Protect the Target | Stop the Flood | Escape | Stop the Ritual | Get the MacGuffin | Pull the Lever / Destroy the Nexus",
    "descripcion": "...",
    "condicion_cierre": "qué cierra el encuentro",
    "retreat_number": "HP% o # bajas (solo si Protein = 'Kill Them'; null en los demás)"
  },
  "optimizers": [
    {
      "tipo": "The High Ground | The Stash | The BIG Gun | Levers 'n' Traps | Boons | Reinforcements",
      "descripcion": "...",
      "como_descubrirlo": "cómo los PCs lo encuentran sin anunciárselos"
    }
  ],
  "hazards": [
    {
      "tipo": "No-Go Zones | Vats of Acid | Frogger | Thin Ice",
      "descripcion": "...",
      "stages": ["stable", "cracked", "broken"]
    }
  ],
  "chaos": [
    {
      "tipo": "Fire | Lights Out | The Random Stash | Bring It Down | Unlabeled Levers | Free Them | Activate It",
      "descripcion": "...",
      "trigger": "qué dispara este elemento (ronda X, HP Y, acción Z)"
    }
  ],
  "espacio": "mapa mental breve — dónde vive cada eje en la sala",
  "dificultad": "Low | Moderate | High",
  "xp_budget": "valor_tabla × # PCs (XDMG 2024)"
}
```

El diseño de esta escena se delega a `dnd-worldbuilder` vía `references/combate.md` (flujo
de 8 pasos: contexto → dificultad → budget → 2-3 combos de monstruos → 3 Proteins → 4 ejes
→ narración del espacio → 3 capas sensoriales del monstruo-Protein).

## 🔍 Secretos y pistas (bloque_secretos)
[3-5 secretos que el party puede descubrir. Para cada secreto, múltiples caminos.
No importa cuál encuentren — todos llevan al mismo lugar.]

- **[Secreto 1]**
  - Si hablan con [NPC]: [pista A]
  - Si registran [lugar]: [pista B]
  - Si tienen éxito en [habilidad]: [pista C]

- **[Secreto 2]**
  - ...

## 🎭 NPCs activos esta sesión (bloque_npcs)
**Regla dura: mínimo 6 NPCs, composición 4 existentes + 2 nuevos.** Cada NPC explica su
**relación con la sesión** — qué rol narrativo cumple, por qué aparece, cómo se cruza con los
objetivos. No vale dejarlo vacío.

| NPC | Existente/Nuevo | Ubicación | Relación con sesión | Qué quiere | Cómo suena |
|-----|------|-----------|---------------------|------------|------------|
| [Nombre] | Existente | [Dónde está] | [Qué aporta a la sesión: pista, obstáculo, aliado, etc.] | [Motivación real] | [1 línea de arquetipo de voz] |
| [Nombre] | Existente | ... | ... | ... | ... |
| [Nombre] | Existente | ... | ... | ... | ... |
| [Nombre] | Existente | ... | ... | ... | ... |
| [Nombre] | **Nuevo** | ... | ... | ... | ... |
| [Nombre] | **Nuevo** | ... | ... | ... | ... |

Para cada NPC **nuevo**, además de la tabla, generar bloque narrativo con:
- `primera_impresion` (2-4 oraciones sensoriales, siguiendo `../dnd-worldbuilder/references/npc.md`)
- `notas_roleplay` (muletillas, patrones de habla, reacciones típicas)

En el Paso 4 del skill, el DM confirma si estos 2 NPCs se guardan en la tabla `npcs`. Si sí,
la transición `nuevo → existente` ocurre ahí (INSERT con `conocido_jugadores=false`,
`campaign_slug='halo'`). El flag `nuevo` queda como snapshot histórico de esta sesión.

## 🏛️ Locaciones (bloque_locaciones)
[3-5 lugares con descripción sensorial y **relación con la sesión**. No vale describir un lugar
que no aporte a ninguna escena.]

| Lugar | Tipo | Región | Relación con sesión | Descripción sensorial |
|-------|------|--------|---------------------|----------------------|
| [Nombre] | [Urbano/Naval/etc.] | [Ciudad/Región] | [Qué escena ocurre aquí, qué rol cumple] | [1-2 líneas sensoriales] |

## 💰 Tesoros y recompensas (bloque_tesoros)
**Regla dura: SOLO items reales de la tabla `items` de Supabase.**

Prioridad:
1. Match directo — item existente que satisface la necesidad tal cual. Sin reskin.
2. Reskin — solo si ningún item existente satisface. Mantiene el item base (mismas stats/efectos)
   pero con flavor nuevo (siguiendo `../dnd-worldbuilder/references/item.md`).
3. **Nunca** inventar items.

| Tesoro (nombre narrativo) | Item base (Supabase) | Tipo | Rareza | Portador sugerido | Reskin aplicado |
|---------------------------|----------------------|------|--------|--------------------|-----------------|
| [Nombre con flavor] | [nombre_item_base + item_id] | [match directo / reskin] | [común/raro/etc.] | [PJ] | [Texto del reskin si aplica, o `—` si es match directo] |

## ⚖️ Momento pivote
[La decisión, confrontación o revelación central de la sesión. Lo que la hace memorable.
Debe conectar con al menos una escena y un secreto.
Ej: "Sera les revela que el cristal no fue robado — ella lo vendió voluntariamente."]

## 🎲 Cierre sugerido / Gancho siguiente sesión
- Cierre natural: [situación al terminar]
- Gancho 1: [algo sin resolver que tire al party hacia adelante]
- Gancho 2: [opcional]

## ⚔️ Monstruos / Enemigos (bloque_monstruos)
**Regla dura: SOLO monstruos de la tabla `monstruos` (catálogo 5e oficial).**

Prioridad:
1. Match directo — monstruo del catálogo que encaja narrativa y mecánicamente. Sin reskin.
2. Reskin — solo si nada encaja. **Stat block no cambia**, solo flavor (3 capas sensoriales:
   primera señal, encuentro, comportamiento — ofrecidas proactivamente por `combate.md`).
3. **Nunca** inventar stat blocks.

| Enemigo (nombre narrativo) | Stat block base (tabla monstruos) | CR | Cantidad | Tipo | Contexto narrativo |
|-----------------------------|------------------------------------|----|----|------|--------------------|
| [Nombre con flavor] | [nombre_monstruo_base + monstruo_id] | [1/4, 1, 3, etc.] | [#] | [match directo / reskin] | [Rol táctico, prioridades, comportamiento observable] |

Si es reskin, incluir las 3 capas narrativas del monstruo (primera señal en el entorno antes
del encuentro, encuentro visual con detalle ancla, comportamiento en combate con patrones
observables).

**Dificultad y budget XP:** calibrar con tabla XDMG 2024 (Low/Moderate/High × # PCs, sin
multiplicador por cantidad). Detalles en `../dnd-worldbuilder/references/combate.md`.

## 📝 Notas privadas DM
[Solo para Vicente. Motivaciones ocultas de NPCs, contingencias si el plan falla, secretos a
largo plazo.]
- [NPC]: su verdadera motivación es [...]
- Si el party hace [X]: contingencia es [...]
- Secreto a largo plazo: [...]
```

---

## Notas sobre la plantilla

**Sobre las escenas:** son ingredientes, no actos obligatorios. Si los jugadores ignoran una
escena y crean la suya propia, perfecto — el DM tiene contexto para improvisar.

**Sobre los secretos:** múltiples caminos a la misma info. Si el party no encuentra la pista A,
puede encontrar la B. Nunca un secreto con un único camino.

**Sobre los NPCs:** el campo "Cómo suena" es solo una línea de arquetipo
(ej: "habla despacio, nunca mira a los ojos"). No se preparan diálogos completos.
El piso de 6 NPCs (4+2) es **regla dura**, no calibrable por duración.

**Sobre el momento pivote:** una sesión sin pivote es olvidable. Revelación, traición, decisión
moral, o consecuencia inesperada.

**Calibrar por duración (solo escenas y secretos, NO NPCs):**
- Sesión de 2h → 2-3 escenas, 2-3 secretos, ≥6 NPCs (piso fijo)
- Sesión de 3-4h → 3-5 escenas, 3-5 secretos, ≥6 NPCs (piso fijo)
