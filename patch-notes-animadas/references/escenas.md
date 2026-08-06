# Escribir `render(t)`

Lo único que se escribe entero por proyecto. El esqueleto de abajo es el del
primer vídeo (QuestKeep, 30 s, 16:9, mudo) reducido a sus patrones: cámbiale los
tiempos y el contenido, conserva la forma.

`render(t)` es **pura**: mismo `t`, mismo DOM. Por eso empieza reseteando y por
eso no hay ni un `setTimeout` — encadenar efectos rompe el seek y, con él, la
grabación y la verificación por fotogramas.

## Reparto de 30 s

| Parte | Tramo | Ritmo | Qué hace |
|---|---|---|---|
| S1 disparo | 0 – 4.6 | lento | deja reconocer la pantalla antes de que pase nada |
| S2 apertura | 4.6 – 9.6 | medio | aparece el gesto o el control |
| S3 proceso | 9.6 – 21.8 | rápido | el grueso, en 2-3 tiempos |
| S4 estallido | 21.8 – 27 | — | la cámara se aleja, caen las conclusiones |
| S5 caída | 27 – 30 | quieto | colapso → logo → corte seco |

## Esqueleto

```js
function render(t) {
  /* … reseteo (ya viene en la plantilla) … */

  /* ── S1 · el producto aterriza ─────────────────────────────────────── */
  if (t < 4.6) {
    cam(ip(t, [0, 4.6], [SW/2, 660]), ip(t, [0, 4.6], [SH/2, 430]),
        ip(t, [0, 3.4], [1.02, 1.16]));            // deriva lenta, no estático
    stage.style.opacity = 1;                        // frame 0 COMPLETO
    stage.style.filter = `blur(${(1 - E.expoOut(seg(t, 0, .9))) * 2.5}px)`;
    $('vignette').style.opacity = ip(t, [0, 1.2], [.78, .9]);
    $('scrim').style.opacity = ip(t, [.3, 1.5], [0, 1]) * (1 - seg(t, 3.6, 4.35));
    set($('t_kick'), E.expoOut(seg(t, .55, 1.35)));
    set($('t_h1'),   E.expoOut(seg(t, .9, 1.9)),
        `translateY(${(1 - E.expoOut(seg(t, .9, 1.9))) * 30}px)`);
    if (t > 3.5) {                                  // sale ANTES de entrar al detalle
      const out = seg(t, 3.5, 4.35);                // (cruce, nunca hueco en negro)
      $('t_kick').style.opacity = 1 - out;
      $('t_h1').style.opacity = 1 - out;
    }
    return;
  }
  $('vignette').style.opacity = .9;

  /* ── S2 · empuje + cursor + el control aparece ─────────────────────── */
  if (t < 9.6) {
    cam(ip(t, [4.6, 6.0], [660, cx(R.objetivo)]),
        ip(t, [4.6, 6.0], [430, cy(R.objetivo)]),
        ip(t, [4.6, 6.0], [1.16, 2.05]));
    focus(R.zona, E.expoOut(seg(t, 4.7, 5.9)));

    if (t >= 5.0 && t < 7.4) {                      // arco, no recta
      const c = cursorArc(t, [5.0, 6.35], [300, 760], [430, 470],
                          [cx(R.objetivo) - 24, cy(R.objetivo)]);
      c.style.opacity = clamp01(seg(t, 4.95, 5.2)) * (1 - seg(t, 7.05, 7.4));
      if (t >= 6.3) {                               // anillo del clic
        const k = seg(t, 6.3, 6.85), ring = $('clickring');
        ring.style.left = cx(R.objetivo) + 'px'; ring.style.top = cy(R.objetivo) + 'px';
        ring.style.opacity = (1 - k) * .95;
        ring.style.transform = `scale(${1 + E.expoOut(k) * 4.6})`;
      }
    }
    if (t >= 6.45) {                                // cambia a la captura CON el menú
      $('sharpImg').src = IMG.menu; $('softImg').src = IMG.menu;
      const g = seg(t, 6.45, 7.25), m = R.menu;     // se revela con una máscara
      sharp.style.clipPath = `inset(${m.y}px ${SW - m.x - m.w}px
        ${SH - m.y - m.h * clamp01(g * 1.15)}px ${m.x}px round 8px)`;
      soft.style.filter = 'blur(4.4px) brightness(.5) saturate(.68)';
    }
    setCap('El gesto, en una frase.', E.expoOut(seg(t, 7.15, 7.95)) * (1 - seg(t, 9.15, 9.6)));
    return;
  }

  /* ── S3 · el proceso, en tiempos ───────────────────────────────────── */
  if (t < 15.6) {
    if (t < 10.6) {                                 // se marca la elección
      $('sharpImg').src = IMG.menu; $('softImg').src = IMG.menu;
      cam(cx(R.menu), cy(R.menu), 2.5);
      focus(R.menuOpciones, 1);
      pickRow(R.opcionElegida, seg(t, 9.7, 10.15)); // el pie dice X → se dibuja X
      setCap('Eliges <b class="g">X</b>.', E.expoOut(seg(t, 9.6, 10.1)) * (1 - seg(t, 10.25, 10.6)));
      return;
    }
    /* 10.6 – 11.1 · MEDIO SEGUNDO DE PAUSA. No se mueve nada.
       Es la regla que más cuesta respetar y la que más se nota. */
    cam(ip(t, [11.1, 12.2], [cx(R.menu), cx(R.resultado)]),
        ip(t, [11.1, 12.2], [cy(R.menu), cy(R.resultado)]),
        ip(t, [11.1, 12.2], [2.5, 2.28]));
    focus(t < 12.0 ? R.panel : R.resultado, clamp01(seg(t, 11.2, 12.4)));
    // estados encadenados con fundido cruzado (mismo clip al capturarlos)
    L[1].style.opacity = clamp01(seg(t, 10.75, 11.15)) * (1 - seg(t, 12.15, 12.5));
    L[2].style.opacity = clamp01(seg(t, 12.15, 12.62));
    if (t >= 13.0) {                                // zoom al detalle citado…
      cam(cx(R.resultado),                          // …centrado en el ELEMENTO ENTERO,
          cy(R.resultado),                          //   no en el detalle, o el dato
          ip(t, [13.0, 13.9], [2.28, 3.2]));        //   citado se sale del cuadro
    }
    setCap(t < 13.4 ? 'Lo que ocurre…' : '…y el remate, <b class="g">con el dato</b>.',
      E.expoOut(t < 13.4 ? seg(t, 12.3, 12.9) : seg(t, 13.5, 14.1)) * (1 - seg(t, 15.2, 15.6)));
    return;
  }

  /* … más tiempos de S3 … */

  /* ── S4 · la cámara se aleja y caen las tarjetas ───────────────────── */
  if (t < 27.0) {
    $('sharpImg').src = IMG.full; $('softImg').src = IMG.full;
    cam(ip(t, [21.8, 23.1], [cx(R.resultado), SW/2]),
        ip(t, [21.8, 23.1], [cy(R.resultado), SH/2]),
        ip(t, [21.8, 23.1], [2.55, 1.0]));
    focus(null, 0);
    $('veil').style.opacity = ip(t, [22.9, 23.6], [0, .42]);   // para que se lean
    stagger(CARDS, t, 23.15, .62, .12);                        // 120 ms entre tarjetas
    CARDS.forEach((c, i) => {
      const p = clamp01((t - (23.15 + i * .12)) / .62);
      c.style.transform = `translateY(${(1 - E.expoOut(p)) * 34}px)
                           scale(${.965 + .035 * E.overshoot(p)})`;
    });
    return;
  }

  /* ── S5 · colapso → logo → CORTE SECO ──────────────────────────────── */
  cam(SW/2, SH/2, ip(t, [27.0, 28.1], [1.0, .82]));
  $('endwrap').style.opacity = 1;
  const col = seg(t, 27.0, 27.85);
  stage.style.opacity = 1 - E.expoIn(col);
  stage.style.filter = `blur(${E.expoIn(col) * 16}px)`;
  $('veil').style.opacity = ip(t, [27.0, 27.9], [.42, 1]);

  const cIn = seg(t, 27.5, 27.95), cOut = seg(t, 27.95, 28.35);
  $('collapse').style.opacity = E.expoOut(cIn) * (1 - cOut);
  $('collapse').style.transform = `scale(${(0.18 + .82 * E.expoOut(cIn)) * (1 + cOut * 5.5)})`;

  const wIn = seg(t, 28.1, 28.95);
  $('wordmark').style.opacity = E.expoOut(seg(t, 28.1, 28.6));
  $('wordmark').style.transform = `scale(${.72 + .28 * E.overshoot(wIn)})`;
  $('wordmark').style.filter = `blur(${(1 - E.expoOut(wIn)) * 8}px)`;
  // A partir de 29.0 no se toca NADA: el último fotograma se sostiene limpio.
}
```

## Lo que más se nota

1. **Pausa antes del resultado.** Medio segundo sin movimiento. Sin ella el
   espectador no llega a ver el momento que justifica el vídeo.
2. **Nunca dos planos sin cruce.** Lo que sale empieza a salir *antes* de que
   entre lo siguiente. Más de 0.3 s de hueco se lee como que se colgó.
3. **Un plano de sólo tipografía** entre dos de UI da respiro y marca el ritmo —
   pero si puedes decirlo con la pantalla real, dilo con la pantalla real.
4. **Fundir estados capturados** es más creíble que animar el cambio a mano: es
   literalmente lo que hace el producto.
5. **El cierre corta en seco.** Un fundido a negro le quita decisión al final.
