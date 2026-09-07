# HORIZONTE — promise-scale

**Modo DEFINIR**, escrito el 2026-09-07 en el loop nocturno, con Heroldo dormido.

Por eso la regla de este archivo: **solo es COMPROMETIDO lo que los documentos
del proyecto ya habían bloqueado por escrito.** Todo lo minado del estado del
arte entra como **PROPUESTO**, sin confirmar, aunque parezca obvio. Nada de lo
propuesto está aprobado por nadie.

---

## Qué es el proyecto

Una báscula de promesas: declaras lo que tu sistema le promete a quien depende
de él, en las palabras de esa persona, y cómo se mide cada promesa. Luego la
pesas. Un archivo de Python, sin dependencias.

**Para quién.** Quien opera un sistema propio que ya tiene monitoreo y aun así
se entera de las cosas por otro lado. En la práctica, hoy: gente que corre
sistemas de agentes de IA en su propia máquina.

**Qué problema resuelve, exactamente.** No "¿está bien?" — eso ya lo contestan
mil herramientas. Contesta **"¿podría siquiera darme cuenta?"**, y se niega a
redondear esa respuesta hacia arriba. Una sonda que no pudo medir se ve, en
cualquier tablero, igual que una que midió y salió bien. Aquí tiene estado
propio, color propio, código de salida propio, y se ordena **por encima** de los
avisos, porque nadie investiga un encogimiento de hombros.

**En qué categoría cae.** Es la pieza chica que se pone *encima* de lo que ya
corres. En el vocabulario de la industria toca tres cosas sin ser ninguna:
**health checks** (pero mide el resultado, no el proceso), **health models /
service levels** (pero sin plataforma), y **alert testing / chaos drills sobre
los propios medidores** (que es lo que hacen sus fallas plantadas). Su README ya
declara lo que no es: ni sistema de monitoreo, ni framework de agentes, ni
orquestador.

---

## Alcance COMPROMETIDO

Solo lo que el README, los docstrings, el workflow o los mensajes de commit ya
habían bloqueado antes de esta noche. Todo esto está construido y medido — ver
`REVISION-2026-09-07.md`.

| | Compromiso | Dónde se bloqueó |
|---|---|---|
| C1 | Cinco estados, y `unmeasured` ≠ `unmeasurable` | README, tabla "The five states" |
| C2 | `unmeasurable` **nunca** cuenta como verde, y se ordena por encima de los avisos | README, titular |
| C3 | Códigos de salida para cron y CI: roto 1, ciego 3, aviso 2, todo cumplido 0 | README + docstring |
| C4 | Una sonda que revienta es `unmeasurable`, no rota y no bien | README, "Never let a probe crash into silence" |
| C5 | "Desde cuándo": historial en JSONL, para que una promesa diga "rota desde hace 31 h" | README, "Since when" |
| C6 | El historial es un lujo: si no se puede escribir, la corrida no falla | comentario en `promise_scale.py` |
| C7 | Fallas plantadas: `--test` rompe cada promesa a propósito y exige que la báscula lo VEA | README |
| C8 | Una promesa nueva llega con su caso plantado, o no llega | README, en negritas |
| C9 | Tabla de promesas generada (`--promises`), para que doc y código no se separen | README |
| C10 | **Un archivo, sin dependencias, sin `pip install`** — porque un chequeo de salud que puede romperse durante una instalación es un chequeo con una forma nueva de fallar | README, "Install" |
| C11 | Python 3.9+, con las plantadas corriendo en CI en 3.9, 3.11 y 3.13 en cada push | workflow + notas del release |
| C12 | Separar la lectura del juicio, para que el juicio se pueda plantar | README, "Writing a good promise" |
| C13 | Que ninguna capa certifique la lectura de otra | README, "Writing a good promise" — **con mecanismo desde el 2026-09-07**: `source=` y `--own` (ver P2) |
| C14 | El experimento: publicado **2026-09-02**, sin promoción, para medir si a alguien le importa **sin empujarlo**. Ventana de 30 días → **vence 2026-10-02** | mensaje del commit `12aeb31` |

**Sobre C14, que hasta hoy no vivía en el repo.** El criterio estaba solo en un
mensaje de commit, que es el único lugar donde nadie lo va a buscar. Queda
escrito aquí: el experimento mide **"¿le importa a alguien sin que yo lo
empuje?"**, y por eso publicarlo en foros contestaría una pregunta distinta y lo
invalidaría. Estado medido por API el **2026-09-07** (día 5 de 30): 1 estrella,
0 forks, 0 issues abiertos, 0 pull requests, 13 topics, Discussions activas,
release `v0.1.0`. Un resultado de cero al día 30 **es un resultado**, no un
fracaso de ejecución: es la respuesta a la pregunta que se hizo.

---

## Alcance PROPUESTO — cerrado el 2026-09-07

**Segunda pasada del 2026-09-07: ninguna propuesta queda sin destino.** P1, P2 y
P3 están **CONSTRUIDAS** (con la prueba que falla sin ellas, abajo en cada una);
P4 y P5 están **DESCARTADAS** con la medición que las mata. Lo que sigue abajo
es el texto original de la propuesta, con su destino y su evidencia encima —
para que se pueda leer qué se propuso y qué se hizo, y no solo el resultado.

Minado el 2026-09-07. Buscado con el **MCP de Perplexity**
(`perplexity_search`), porque perplexica estaba agotada ese día; y con la **API
de GitHub** para el estado del repositorio. Cada punto trae su fuente y su fecha.

Están en orden de qué tan cerca están de la tesis del proyecto. **Los tres
primeros son los únicos que se recomiendan de verdad**; el resto está listado
para que se pueda decir que no a algo concreto.

### P1 — Que la báscula se pese a sí misma — **CONSTRUIDA 2026-09-07**

**Archivo:** `promise_scale.py` — `Scale(expect_every=...)`, `judge_last_run()`,
`last_run_at()`, `_hours()`, `Scale.promises()`. **Demostrada en** `example.py`.

**La prueba que falla sin ella** (`python3 test_promise_scale.py`, 16 casos
nuevos). Los tres que muestran el agujero, con la báscula sin `expect_every`:

```
ok  without expect_every there is no extra promise (nothing changes)   expected 1  got 1
ok  and a scale that has never run once reads as all green — the hole  expected 0  got 0
ok  so the run exits 3 even though every promise you wrote is kept     expected 3  got 3
```

Y el ciclo entero, corrido en una máquina limpia (`HOME` nuevo):

```
$ python3 example.py --brief   → kept 5/7 · could not measure scale P5   EXIT=3
$ python3 example.py --brief   → kept 6/7 · could not measure P5         EXIT=3
$ python3 example.py --all --brief → kept 7/7                            EXIT=0
```

**Que la prueba muerde, medido, no supuesto.** Se mutó el mecanismo (que
`promises()` no inyecte nunca la promesa implícita) y el arnés cazó **8 casos**
y salió 1. Sin la mutación, 80 casos en verde.

**En CI:** el ejemplo corre dos veces y se exige que la primera salga **3**. Si
la vigilancia se calla, la primera corrida sale verde y ese paso lo caza — se
comprobó forzándolo: `STEP_EXIT_IF_SELFWATCH_SILENT=1`.

**Decisiones que no estaban en la propuesta y hubo que tomar:**
- Tarde es `unmeasurable`, nunca `broken` (ya venía propuesto así, y se cumplió).
- Se llega tarde a la cadencia **más un décimo** (24 h → 26.4 h), para que el
  vaivén normal de un cron no dispare una alarma sobre sí misma.
- Es **opt-in**: sin `expect_every` no aparece nada y nada cambia. Una báscula
  que se corre a mano no tiene cadencia contra la cual llegar tarde, y una
  promesa roja por algo que nadie puede arreglar se aprende a ignorar.
- Un `expect_every` ilegible, un historial apagado o una clave ya ocupada por
  una promesa tuya **no revientan la corrida**: cada uno sale `unmeasurable`
  diciendo exactamente eso. Una báscula que se muere por su propia configuración
  es una báscula que se calla a las 4 de la mañana.
- La promesa implícita **entra a la cobertura de `--test`**: si la enciendes y no
  la plantas, `--test` la nombra. La vigilancia no está exenta de la regla del
  proyecto.

<details><summary>El texto original de la propuesta</summary>

**La báscula no vigila que la báscula haya corrido.** Si borran la entrada de
cron, si el disco se llena, si el `python3` del cron desaparece: nada lo nota.
Una báscula que no corrió y una báscula sin novedades **se ven idénticas desde
fuera** — que es, palabra por palabra, la falla que este proyecto existe para
denunciar, un piso más arriba.

El estado del arte le puso nombre y lo pide explícitamente:

> *"Track **check execution rates** to verify monitors run on schedule. Missing
> checks indicate infrastructure problems."*
> — upstat.io, "Monitoring the Monitors", 2025-10-16

Y, en el vocabulario de sistemas de agentes:

> *"Implement heartbeat signals or execution receipts […] so a missing heartbeat
> triggers an alert rather than silent absence."*
> — SD Times, *"Your Agents Aren't Failing. They're Not Running."*, 2026-08-03

**Lo bueno: el dato ya está.** El historial guarda `at` en cada corrida. Nadie
lo lee para esta pregunta. Forma propuesta, cabe en el estilo del archivo:

```python
Scale(..., expect_every="24h")     # y una promesa implícita, siempre presente
# P0  ● UNMEASURABLE  This scale has actually been running
#     last run 3.1 days ago, and it is set to run every 24 h
```

Que salga `unmeasurable` y no `broken` es deliberado: no sabes si el sistema
está mal, sabes que **dejaste de mirar**. Exactamente el estado que ya existe.

</details>

### P2 — Dar mecanismo a C13 — **CONSTRUIDA 2026-09-07**

**Archivo:** `promise_scale.py` — `@promise(source=...)`, `weigh(own=)`,
`--own`, el campo `source` en cada lectura del `--json`, la línea del parte y la
columna de `--promises`. **Demostrada en** `example.py` (promesa P6, prestada
del parte de otra capa, con sus tres casos plantados).

**La prueba que falla sin ella** (10 casos nuevos):

```
ok  --own drops the borrowed reading                          expected 'unmeasured'  got 'unmeasured'
ok  and names the layer whose word it refused to take         expected True          got True
ok  and every reading carries where it came from              expected "the sentinel's report" got …
ok  the printed report names the source, so nobody reads it as measured here  expected True
ok  refusing a borrowed reading is a choice, not a failure     expected 0            got 0
```

**Que la prueba muerde:** mutado `--own` para que no salte nada, el arnés cazó
**2 casos** y salió 1.

**Lo medido en vivo:** `python3 example.py --own --brief` → `kept 6/6` (la
lectura prestada desaparece); sin `--own` → `kept 7/7`.

**Decisión de diseño:** saltar una lectura prestada es `unmeasured`, no
`unmeasurable`. Es una decisión que tomaste, no una que el sistema te quitó —
que es exactamente la diferencia que separa esos dos estados en este proyecto.

<details><summary>El texto original de la propuesta</summary>

Es el único de los tres consejos duros del README que sigue siendo solo prosa,
y ya está resuelto en la implementación viva en español: cada promesa se marca
como leída-del-parte-de-otro, y una bandera las salta para que el vigilante no
se certifique a sí mismo con cara de medición fresca.

Forma propuesta, mínima y aditiva:

```python
@promise("P7", "…", source="sentinel")   # esta lectura viene de otro
scale --own                              # mide solo lo propio
```

Y en el `--json`, que cada lectura diga de dónde salió. Sin eso, el consejo del
README se puede seguir por disciplina, que es justo lo que el proyecto no acepta
en ningún otro punto.

</details>

### P3 — Lecturas caras, guardadas con su edad — **CONSTRUIDA 2026-09-07**

**Archivo:** `promise_scale.py` — la clase `Carry`, `Scale(carry=,
carry_max_age=)` y la rama de acarreo dentro de `weigh()`. **Demostrada en**
`example.py` (P5, la promesa lenta).

**La prueba que falla sin ella** (11 casos nuevos). Las dos que sostienen la
regla:

```
ok  and cannot print it without saying when it was taken        expected True  got True
ok  a stored reading past its limit -> unmeasurable, NOT unmeasured  expected 'unmeasurable'
```

**Que la prueba muerde:** mutado el guardado para que archive cualquier cosa, el
arnés cazó **2 casos** y salió 1.

**Y el hallazgo que solo apareció corriendo el ciclo entero.** Con los casos
nuevos ya en verde, el ejemplo corrido dos veces en una máquina limpia enseñó
que la primera corrida rápida **archivaba su propia nota de "todavía no hay
lectura guardada"** —un `unmeasurable` sobre la ausencia de una lectura— y la
segunda la **acarreaba como si fuera una medición**:

```
P5  ● UNMEASURABLE  …the stored reading is missing — carried from the slow run 0 min ago
```

Arreglado: solo se archiva lo que midió una corrida que **incluía ese modo**
(`Carry.write(readings, modes)`). Una nota que dice "no pude medir esto" no es
una medición, y en el momento en que se archiva como tal el mecanismo entero se
convierte en el verde viejo que existe para evitar. Quedó plantado en tres casos
nuevos. *Es la misma lección que ya está en la bitácora: el arnés estaba verde
porque solo le daban entradas válidas.*

**Decisiones que no estaban en la propuesta:**
- La edad va **soldada al texto**, no ofrecida al lado: `"34/34 — carried from
  the slow run 4 h ago"` se arma dentro de la librería, así que no hay forma de
  imprimir una lectura guardada sin decir de cuándo es.
- Cada lectura guarda **su propia hora**, no la del archivo. Con la hora del
  archivo, medir una promesa barata refresca la edad de la cara.
- Una lectura acarreada **nunca se vuelve a archivar**: si se archivara, su
  reloj arrancaría de nuevo en cada corrida y no envejecería jamás.
- Sin `carry` configurado, un modo saltado sigue siendo `unmeasured` — no cambia
  nada para quien no lo pide.

<details><summary>El texto original de la propuesta</summary>

Hoy `--all` corre las promesas lentas y `scale` a secas las declara `unmeasured`.
El modo rápido nunca ve el resultado de las lentas, así que el parte de todos los
días está incompleto por diseño. La implementación viva ya resolvió esto: la
corrida completa de cada noche deja su resultado en un archivo, y el modo rápido
lo **lee con su hora** si tiene menos de 26 horas, mostrando la edad en el texto.

La trampa a evitar —y por eso esto va con P2 y no antes— es que una lectura
guardada que se muestra sin su edad es una lectura vieja disfrazada de fresca.
Se propone que **sea imposible mostrarla sin decir de cuándo es**, y que al pasar
del límite vuelva a `unmeasurable`, no a `unmeasured`.

</details>

### P4 — Un estado más: "apagada a propósito" — **DESCARTADA 2026-09-07**

**La medición que la mata.** La implementación viva tiene ese sexto estado desde
el 2026-09-02 y lee las promesas pausadas de un archivo. Medido hoy, cinco días
después, sobre esa instalación:

```
$ [el archivo de promesas pausadas]  →  DOES NOT EXIST
```

Nunca se creó. Catorce promesas corriendo cada quince minutos durante cinco
días y **cero** usos del estado que se propone copiar. Un sexto estado en una
librería de un archivo, sin un solo caso de uso en el sistema que lo inventó, es
peso muerto y una casilla más que cada consumidor del `--json` tiene que
aprender. Queda escrito para que la próxima persona que lo piense sepa que ya se
pensó, y con qué se midió.

**Si alguna vez aplica:** el criterio no es "alguien lo pidió", es que alguien
tenga una promesa que necesite silenciar **por semanas** y que hoy esté
apagándola borrando el `@promise` — que es la señal de que la falta hace daño.

### P5 — Contratos de entrada para las sondas — **DESCARTADA como API 2026-09-07**

**La medición que la mata:** hacerlo de verdad significa validar un esquema
—campos declarados, número de versión, qué hacer con un campo que falta— y eso
son decenas de líneas que no miden nada, dentro de un archivo cuyo compromiso C10
es *un archivo, sin dependencias*. Es una **regla de cómo escribir una sonda**, no
una capacidad de la báscula: la propia propuesta ya lo decía.

**Lo que sí se hizo, que es el residuo útil:** entró como el cuarto consejo duro
del README (*"Don't parse another program's text"*), junto a los otros tres, y
como la promesa P6 del ejemplo — que lee el parte de otra capa y lo **juzga antes
de creerlo**: parte viejo → `unmeasurable`, sensor que desapareció del parte →
`unmeasurable`, y solo entonces el estado que el parte dice. Con sus tres casos
plantados. La recomendación queda ilustrada por código que corre, en vez de ser
un párrafo.

<details><summary>El texto original de la propuesta</summary>


Cuando una promesa se mide leyendo la salida de otro programa, parsear texto con
expresiones regulares es frágil de una forma silenciosa: el otro programa cambia
un renglón y la promesa empieza a contestar mal sin romperse. La implementación
viva pasó de leer texto a exigir un JSON con número de esquema y campos
declarados; un campo renombrado sin subir el esquema **se declara**, no se
rellena a mano.

Es una buena idea y probablemente **no pertenece a este archivo**: es una
recomendación para el README ("no parsees texto de otro programa"), no una API.

</details>

### Lo que se mira y se decide NO hacer

- **Publicar en PyPI.** Contradice C10 de frente. Si alguna vez se hace, es un
  paquete que instala *una copia del archivo*, y aun así habría que explicar por
  qué. Hoy: no.
- **Exportar a Prometheus / OpenTelemetry.** Es la salida obvia y la trampa
  obvia: en cuanto la báscula alimenta un tablero, alguien pinta `unmeasurable`
  de amarillo y la única regla del proyecto se pierde en el camino. Si se hace,
  el estado tiene que sobrevivir el viaje, y eso es trabajo de diseño, no de
  exportador. El `--json` ya cubre el 90 % del caso.
- **Reintentos, ventanas de confirmación, umbrales de fallos consecutivos.**
  Son buenas prácticas reales de monitoreo (dotcom-monitor, 2026-07-15) y son de
  la capa de abajo. Aquí serían el principio de convertirse en lo que el README
  dice que no es.
- **Notificaciones, escalamientos, guardias.** Lo mismo. La báscula devuelve un
  código de salida; quien lo lea decide a quién despierta.

---

## Brecha entre la intención y el estado del arte

Lo que se buscó fue si alguien más hace lo que este proyecto dice hacer. Sí y no,
y la diferencia es más nítida de lo que el README afirmaba:

**El estado existe en todas partes. Lo que no existe es el orden.**

- Azure Monitor lo llama **Unknown**: *"the health state of the entity can't be
  determined due to insufficient data or a lack of signals"*. En la misma tabla,
  **Unhealthy** lleva la nota *"Counts as downtime for health objective"* — y
  **Unknown no lleva ninguna**. (Microsoft Learn, actualizado 2026-07-21)
- Azure Resource Health dice que Unknown *"isn't a definitive indication of the
  state of the resource"* (2025-11-10), y al menos un proveedor deja **apagar**
  la alerta de Unknown con un interruptor (Site24x7, KB de Azure Resource
  Health).

O sea: el default de la industria es que **no saber no cuenta en tu contra**.
Esa es la brecha, y es exactamente lo que este proyecto invierte. La afirmación
original del README ("no encontré esta parte en ningún lado") era demasiado
fuerte y ya quedó matizada con estas fuentes — el proyecto sale ganando, porque
ahora la diferencia está medida en vez de declarada.

**Y la segunda mitad tiene nombre y número.** Plantar fallas a propósito para ver
si el medidor las ve se llama, en la industria, *chaos drill* sobre las alertas:

> *"Once a quarter, deliberately break a check […] and confirm the alert fires
> […]. **About a third of alerts fail their first drill.**"*
> — dotcom-monitor, "Website Monitoring Best Practices", 2026-07-15

Una de cada tres. Eso convierte *"una báscula que nadie ha visto fallar no es una
báscula"* de opinión en número. También hay precedente técnico: Prometheus trae
`promtool` con pruebas unitarias en YAML para reglas de alerta (OneUptime,
2026-01-30). La diferencia de `@planted` es dónde se planta: en la función de
juicio, en el lenguaje de la sonda, sin desplegar nada.

**Lo que el estado del arte pedía y aquí faltaba:** la vigilancia de que el
chequeo haya corrido. Era el hueco real, lo nombraban las dos fuentes de arriba,
y **quedó construido el 2026-09-07** (P1). Lo que sigue siendo distinto de lo
que hace la industria no es tener la vigilancia: es que aquí llegar tarde sale
`unmeasurable` y por lo tanto **no cuenta como verde**, en vez de ser un aviso
que se puede apagar con un interruptor.

**Sobre la categoría "sistemas de agentes":** la fuente más cercana a la tesis
de este proyecto es de agosto de 2026 y llega por su cuenta a la misma
distinción:

> *"'No result' implies the agent ran, observed the source, and found nothing.
> 'Unknown' means the agent could not verify whether it observed the source at
> all. Conflating the two causes systems to report false certainty, making real
> failures indistinguishable from genuinely empty data."*
> — SD Times, 2026-08-03

Que alguien llegue solo al mismo lugar dos meses después es señal de que el
problema es real, no de que el proyecto llegó tarde: ese artículo describe el
problema y no publica la herramienta.

---

## No-negociables

Estos no se tocan sin que Heroldo lo diga por escrito. Los cinco primeros son
del proyecto desde antes; el sexto se aprendió esta noche.

1. **`unmeasurable` nunca cuenta como verde**, y se ordena por encima de los
   avisos. Cualquier cosa que lo suavice —una bandera para ignorarlo, plegarlo a
   "no aplica", degradarlo a aviso— borra la razón de existir del proyecto.
2. **Un archivo, sin dependencias.** No se negocia por comodidad.
3. **Una promesa nueva llega con su caso plantado.** Desde hoy es verificable.
4. **Los valores guardados de los estados y las claves de las promesas son
   datos, no etiquetas.** Renombrar uno reinicia el "desde cuándo" de todo el
   mundo, en silencio, y la corrida que lo hace se ve perfectamente normal.
5. **Esto no es un sistema de monitoreo.** Se pone encima de lo que ya corres.
6. **Toda regla que este proyecto declare tiene que estar plantada contra su
   propio código, con la entrada que la regla nombra** — no solo contra el
   camino feliz. La auditoría del 2026-09-07 encontró la regla principal
   incumplida por un dedazo en el nombre de un estado, con veinte casos
   plantados en verde alrededor.

---

## Roadmap por horizontes

Nada de esto está aprobado; es el orden que se propone si se aprueba algo.

**Horizonte 1 — cerrar la tesis sobre sí misma. ✅ CERRADO 2026-09-07.** P1 (que
la báscula se pese a sí misma) y P2 (mecanismo para C13), construidas, sin
dependencias y sin archivos nuevos.

**Horizonte 2 — que el parte diario esté completo. ✅ CERRADO 2026-09-07.** P3,
lecturas caras guardadas con su edad, imposibles de mostrar sin decir de cuándo
son.

**Horizonte 3 — lo que decida el experimento.** Vence el **2026-10-02**. Si
llegan preguntas, contestan ellas qué falta y este archivo se refresca con lo
que digan. Si no llega ninguna, eso también contesta: el proyecto está terminado
como pieza de una sola persona, y puede quedarse quieta sin que eso sea un
abandono. **Es el único horizonte abierto.**

**Fuera de todos los horizontes:** PyPI, exportadores, notificaciones,
reintentos. Ver arriba.

---

## Lo IRREVERSIBLE, con el comando escrito y sin ejecutar

Sale hacia afuera y le pertenece a Heroldo. **No se ejecutó.**

**Cortar el release `v0.2.0`.** El código en disco dice `0.2.0` desde hoy; el
release más nuevo de GitHub sigue siendo `v0.1.0`. La brecha está **declarada**
en `CHANGELOG.md` en vez de escondida — que era la alternativa: dejar
`__version__` en `"0.1.0"` con tres capacidades nuevas encima, o sea un proyecto
sobre no redondear el propio estado hacia arriba, redondeando el suyo. El
comando, listo para pegar:

```bash
cd ~/proyectos/promise-scale
gh release create v0.2.0 --title "v0.2.0 — the scale weighs itself" \
  --notes "The scale now watches whether the scale ran, marks readings it did not take itself, and carries expensive readings forward with their age. See CHANGELOG.md."
```

Después de cortarlo, la primera línea de `CHANGELOG.md` deja de ser cierta y hay
que quitar esa sección: es una declaración de una brecha que ya no existe.

**Lo que la pasada anterior dejó `[NO VERIFICADO]`, ahora MEDIDO — y sale que
NO:** la imagen de vista previa social **no está asignada**. `social-preview.png`
está en el repo desde el 2026-09-02 y nunca se subió a los ajustes. La API no lo
expone, pero la página sí, y ahí se mide:

```
$ curl -sL https://github.com/heroldoe-create/promise-scale | grep og:image
  → https://opengraph.githubassets.com/<hash>/heroldoe-create/promise-scale
```

Ese dominio es la tarjeta que GitHub **genera solo**. Una imagen propia se sirve
desde `repository-images.githubusercontent.com`. Comprobado el discriminante
contra cuatro repos: `vercel/next.js` y `tailwindlabs/tailwindcss` (con imagen
propia) devuelven el segundo dominio; `facebook/react` y `astral-sh/ruff` (sin
ella) devuelven el primero, igual que este.

**Que el archivo exista en el repo no prueba que esté publicado.** Asignarla son
dos clics en *Settings → General → Social preview*, en el navegador, y le toca a
Heroldo: no hay endpoint público para hacerlo.

---

## Bitácora de refrescos

- **2026-09-07 (segunda pasada, cierre)** — Cerrado. Las cinco propuestas
  quedaron con destino: **P1, P2 y P3 CONSTRUIDAS** (cada una con la prueba que
  falla sin ella y con una mutación que demuestra que el caso muerde), **P4 y P5
  DESCARTADAS** con su medición. Se subió `__version__` a `0.2.0` y se creó
  `CHANGELOG.md` declarando que la etiqueta de GitHub va detrás; cortarla es lo
  único IRREVERSIBLE y quedó con el comando escrito, sin ejecutar. Arnés: 31 →
  80 casos. Se encontró y arregló un fallo callado propio, corriendo el ciclo
  entero en una máquina limpia, con los casos nuevos ya en verde.
- **2026-09-07** — Creado en modo DEFINIR, en el loop nocturno, con Heroldo
  dormido. Alcance COMPROMETIDO reconstruido del README, los docstrings, el
  workflow y los dos mensajes de commit. Todo lo minado entró como PROPUESTO.
  Estado del arte buscado con el MCP de Perplexity (perplexica agotada ese día)
  y con la API de GitHub. Nada aquí está confirmado por Heroldo.
