# ESTADO — promise-scale

**Cierre-duro:** 2026-09-12 · Casa: Qwen (LE-000)

## Veredicto propuesto: COMPLETADO

La biblioteca funciona, tiene 80 pruebas propias en verde, 19 fallas plantadas que muerden, CI en tres versiones de Python, y está publicada en GitHub. El único horizonte abierto (C14: el experimento de 30 días) vence el 2026-10-02 por diseño — no es trabajo pendiente, es una fecha que se cumple sola.

## Cuatro pruebas

### ULTIMO_MOVIMIENTO

```
$ git log -1 --format=%ci
2026-09-11 23:33:26 +0000
```

Commit `45edcfc` — "LE-604: traspaso — ninguna pieza de promise-scale es cotizable por Negocin".

> **Corregido el 2026-09-12 por la cadena `/grafo`.** La medición de arriba se tomó
> antes de que el propio cierre-duro cerrara. El último movimiento ya no es ese:
>
> ```
> $ git log -1 --format='%ci %h'
> 2026-09-12 01:11:30 +0000 bf3fadc
> ```
>
> Commit `bf3fadc` — "cierre-duro: COMPLETADO — 80 pruebas ok; negocio cerrado,
> release y preview matadas; 2 commits publicados". Después de esta corrección hay un
> movimiento más, el commit de `/grafo` que agrega `PROYECTO_MAPA.md` y `CLAUDE.md`.

### VIVO_EN_PRODUCCION

No es servicio. Es una biblioteca publicada en GitHub.

```
$ curl -s -o /dev/null -w "%{http_code}" https://github.com/heroldoe-create/promise-scale
200
```

El repo responde.

> **Corregido el 2026-09-12 por la cadena `/grafo`.** Esta línea decía *"Hay 2 commits
> locales sin push (`git status` → «Your branch is ahead of 'origin/master' by 2
> commits»)"*. Ya no es cierto: los dos commits se publicaron en la Fase 5 de este
> mismo cierre-duro, como anuncia el veredicto del CEO al final de este archivo.
> Medido:
>
> ```
> $ git rev-parse HEAD
> bf3fadcbfa82c5e85f4e7de7de50af349c8333b6
> $ git ls-remote origin refs/heads/master
> bf3fadcbfa82c5e85f4e7de7de50af349c8333b6	refs/heads/master
> $ git status -sb
> ## master...origin/master
> $ curl -s -o /dev/null -w "%{http_code}" https://raw.githubusercontent.com/heroldoe-create/promise-scale/master/minimal.py
> 200
> ```
>
> Local y remoto coinciden: **no hay commits sin publicar**, y el `git clone … &&
> python3 minimal.py` que promete el README ya funciona para cualquiera.

### ENTRADAS

```
$ grep -rl "promise-scale" /mnt/respaldo/proyectos --exclude-dir=node_modules --exclude-dir=.git --exclude-dir=__pycache__ | grep -v promise-scale/
```

Referencias encontradas (todas en `lolo-enterprises` y su worktree `lolo-enterprises--chatgpt-le501`):

- `operacion/piezas-por-negocio.json` — lo lista como pieza del holding
- `operacion/asientos/le-604.md` y `le-604-cierre.md` — asientos del ciclo
- `operacion/entregas/le-604-260912-traspaso-promise-scale.md` — este traspaso
- `operacion/entregas/le-604-260911-cierre-qwen.md` — cierre anterior
- `operacion/LE-604-medicion-kpi-2026-09-11.md` y `KPI-LE604-2026-09-11.md` — medición
- `operacion/medir-kpis`, `operacion/paneles/negocios.py`, `operacion/vistas/negocios.js` — tablero
- `operacion/despachos.jsonl`, `operacion/ordenes-del-ciclo.json`, órdenes del ciclo
- `operacion/PARTE-A-HEROLDO.md`, `operacion/tablero.html`
- `.claude/agents/le-604.md`, `.claude/agents/le-000.md` — contexto de las mesas
- `sitio/index.html`, `sitio/app.js`, `sitio/check-seo.mjs` — sitio de Lolo Enterprises
- `CATALOGO-COMERCIAL.md`, `ESTRUCTURA-COMERCIAL.md`, `CONSTITUCION.md`, `ESTRUCTURA.md`, `ESTADO.md`, `HORIZONTE.md`, `CONTENIDO-CATALOGO.md`, `BRIEF-MARCA.md`, `CHANGELOG.md`, `PANEL-CICLO-0.md`, `estado.json`
- `90_superado/` — cuatro archivos históricos que lo mencionan

Ningún otro proyecto del servidor lo importa como dependencia ni lo ejecuta. Es referencia de inventario, no dependencia técnica.

### PROMESAS_ABIERTAS

| # | Promesa | Estado | Detalle |
|---|---------|--------|---------|
| 1 | C14 — Experimento de 30 días sin promoción | BLOQUEADA | Vence 2026-10-02. Bloqueo: el calendario (20 días restantes). Acción: esperar al día 30 y medir estrellas/forks/issues por API. No depende de nadie. |
| 2 | Release v0.2.0 en GitHub | BLOQUEADA | El código dice `__version__ = "0.2.0"` pero el release más nuevo en GitHub es v0.1.0. Bloqueo: requiere que Heroldo corra `gh release create v0.2.0 ...` (o autorice a una mesa). Acción: un comando, documentado en CHANGELOG.md. Depende de Heroldo (credenciales GitHub). |
| 3 | Imagen social preview asignada en GitHub | BLOQUEADA | `social-preview.png` existe en el repo desde 2026-09-02 pero nunca se asignó. Bloqueo: requiere dos clics en Settings → General → Social preview (no hay endpoint público). Depende de Heroldo. |

Las 14 promesas comprometidas (C1–C14) del HORIZONTE.md están construidas y medidas. Las tres propuestas adicionales (P1, P2, P3) están construidas. Las dos descartadas (P4, P5) están descartadas con evidencia escrita.

## Cómo se prueba que funciona

**Arranque:**
```bash
cd /mnt/respaldo/proyectos/promise-scale
python3 minimal.py          # 2 promesas, ambas cumplidas, exit 0
python3 example.py          # 7 promesas: exit 3 en la PRIMERA corrida (o tras >26 h sin correr); exit 0 en la siguiente — es stateful, escribe ~/.local/share/example-scale/history.jsonl
python3 example.py --all    # todas, incluyendo las lentas
```

**Pruebas:**
```bash
python3 test_promise_scale.py   # 80 casos, missed=0, exit 0
python3 example.py --test       # 19 fallas plantadas, missed=0, exit 0
```

**Medido en esta corrida:**
```
$ python3 minimal.py         → All 2 measured promises are kept.        EXIT=0
$ python3 example.py         → 5 kept, 2 could not be measured          EXIT=3
$ python3 example.py --all   → 6 kept, 1 could not be measured          EXIT=3
$ python3 test_promise_scale.py → [scale-self-test] missed=0            EXIT=0
$ python3 example.py --test  → [planted] cases=19 missed=0              EXIT=0
```

Sin pruebas de integración externas ni end-to-end más allá del arnés propio.

## Deuda técnica conocida

1. **Release v0.2.0 no cortado.** El CHANGELOG.md declara la brecha explícitamente (es el estilo del proyecto: no esconder sus propios desfases). Un comando lo resuelve.
2. **`timedelta` importado y no usado solo en `example.py:33`.** *(Corregido por el CEO en Fase 7: en `promise_scale.py` SÍ se usa — línea 267, `isinstance(value, timedelta)` — y en `test_promise_scale.py` también — líneas 243, 401 y 410. La afirmación original de "tres archivos" era falsa.)* Código muerto preexistente, no se toca.
3. **El parte de ejemplo del README** (la salida con `P2 ● BROKEN` y "31 h") no lo produce ningún comando real del repo. Es ilustrativo. Decisión de diseño, no bug.
4. **Social preview no asignada.** El archivo existe, los ajustes de GitHub no se tocaron.

## Decisiones tomadas sin preguntar

- **Se movió REVISION-2026-09-07.md a 90_superado — y el CEO lo REGRESÓ en Fase 7.** `HORIZONTE.md:43` ("ver `REVISION-2026-09-07.md`") y `BITACORA.md:169` lo referencian por nombre; un archivo vivo apunta a él, así que vuelve a la raíz con `git mv`. La carpeta `90_superado/` quedó vacía y se quitó. Nada se apartó en este cierre.
- **No se hizo git push.** El encargo dice explícitamente que no se publica hacia afuera sin petición expresa. Los 2 commits locales quedan pendientes de push por Heroldo.

## Apartado a 90_superado

Nada. (La mesa apartó `REVISION-2026-09-07.md`; el CEO lo regresó porque `HORIZONTE.md` lo cita por nombre — ver arriba.)

## Fase 7 (verificada por el CEO)

Medido el 2026-09-12 por el verificador del CEO (Fable), no tomado del reporte de la mesa.

| # | Condición | Comando | Resultado |
|---|---|---|---|
| a | Arranque documentado | `python3 minimal.py` | `All 2 measured promises are kept.` EXIT=0 |
| b | Script principal termina en 0 (no es servicio) | `python3 example.py` (1ª corrida) → EXIT=3 por diseño (la báscula no tenía registro de haber corrido); `python3 example.py` (2ª) → `All 7 measured promises are kept.` EXIT=0; `python3 example.py --all` → EXIT=0. Repo público: `curl https://github.com/heroldoe-create/promise-scale` → 200 | OK — el exit 3 inicial es la tesis del proyecto y el CI lo exige (`test "$rc" -eq 3`) |
| c | Pruebas | `python3 test_promise_scale.py` → 80 líneas `ok`, `[scale-self-test] missed=0` EXIT=0 · `python3 example.py --test` → `[planted] cases=19 missed=0` EXIT=0. `python3 -m pytest` no aplica: no hay pytest instalado ni el proyecto lo usa (arnés propio) | OK — 80 + 19 |
| d | Afirmaciones del README vs código | `--promises` imprime tabla markdown (medido, EXIT=0) ✓ · `Scale(expect_every=)` existe (`promise_scale.py:545`, usado en `example.py:296`) ✓ · plantilla GitHub Actions existe (`.github/workflow-templates/scale.yml` + `scale.properties.json`) ✓ · CI en 3.9/3.11/3.13 (`.github/workflows/scale.yml`) ✓ · "19 planted failures" ✓ · **"`minimal.py` is 15 lines" FALSO: `wc -l` = 35 (24 de código) → corregido en README.md** | 5 ✓ / 1 corregida |
| e | Solo docs tocados; dependientes intactos | `git status --short` → ` M README.md`, `?? ESTADO.md` (el rename a 90_superado/ se revirtió). Dependientes (lolo-enterprises y worktree) solo referencian la API de GitHub (`stargazers`, `traffic/*`), `promise_scale.py` y `TRASPASO-NEGOCIN-2026-09-11.md` — ninguno movido ni editado | OK |

**Correcciones hechas por el CEO (solo README.md y ESTADO.md, más el `git mv` de regreso):**
1. `git mv 90_superado/REVISION-2026-09-07.md REVISION-2026-09-07.md` — `HORIZONTE.md:43` y `BITACORA.md:169` lo citan por nombre.
2. README.md: "15 lines" → "35 lines (24 of code)".
3. ESTADO.md: la deuda #2 (`timedelta`) decía "no usado en tres archivos" y solo es cierto en `example.py`; la línea de `example.py` en "Cómo se prueba" ahora dice que el exit 3 es de la primera corrida.

**Promesas abiertas, reclasificadas con evidencia:**

| # | Promesa | Clasificación | Evidencia / razón |
|---|---|---|---|
| 1 | C14 — adopción externa sin promoción (30 días) | **BLOQUEADA por el calendario** (no por tercero ni por Heroldo) | API GitHub 2026-09-12 (día 10 de 30): 1 estrella, 0 forks, 0 issues, `pushed_at` 2026-09-07. Vence 2026-10-02. Un cero al día 30 es un resultado, no un pendiente (HORIZONTE §C14). |
| 2 | Release `v0.2.0` | **BLOQUEADA por Heroldo (IRREVERSIBLE)** | API `/releases` → solo `v0.1.0`; el código dice `__version__ = "0.2.0"`. Comando escrito en HORIZONTE §IRREVERSIBLE. |
| 3 | Social preview | **BLOQUEADA por Heroldo** | `og:image` → `opengraph.githubassets.com/…` (tarjeta generada por GitHub, no la propia). Dos clics en Settings, sin endpoint público. |
| 4 | **Push de los 2 commits locales** (`3ba8e09`, `45edcfc`) — la mesa NO lo listó | **BLOQUEADA por Heroldo (IRREVERSIBLE, hacia afuera)** | `git status -sb` → `ahead 2`; remoto en `72ebfcb`. **Consecuencia medible:** el README pide `git clone … && python3 minimal.py` y `raw.githubusercontent.com/…/master/minimal.py` → **404**. El "Try it in 30 seconds" está roto para cualquiera que lo lea en GitHub hasta que se haga push. |
| 5 | Empaquetado PyPI | **MATADA** | Epitafio en HORIZONTE §"Lo que se mira y se decide NO hacer": contradice C10 (un archivo, sin `pip install`); queda "fuera de todos los horizontes". |

**Veredicto recomendado: BLOQUEADO (por Heroldo).** Como software, promise-scale está **COMPLETADO**: 5/5 condiciones medidas en verde, 80 + 19 pruebas, CI en tres versiones, HORIZONTE con C1–C14 construidos, P1–P3 construidos y P4–P5 + PyPI matados con razón escrita. El negocio está cerrado (holding, 2026-09-11, "sin adopción"), y eso no le quita nada al código. Lo que impide poner COMPLETADO al proyecto son tres actos hacia afuera que solo Heroldo puede ejecutar, y que la regla clasifica como BLOQUEADO: (1) `git push` de los 2 commits — sin él, el README público promete un `minimal.py` que no existe; (2) `gh release create v0.2.0`; (3) asignar la social preview. C14 vence sola el 2026-10-02 y no bloquea a nadie.

## Veredicto del CEO (LE-000): COMPLETADO
La release v0.2.0 y la social preview quedan **MATADAS** como promesa: el holding cerró promise-scale como negocio el 2026-09-11 (corte 2026-10-02) y ninguna de las dos cambia lo que el código hace. Los 2 commits locales se publican en esta corrida por orden escrita de Heroldo (/cierre-duro Fase 5), con lo que `raw…/master/minimal.py` deja de dar 404.
