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
| C13 | Que ninguna capa certifique la lectura de otra | README, "Writing a good promise" — **advertido, sin mecanismo todavía** |
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

## Alcance PROPUESTO — nada de esto está confirmado

Minado el 2026-09-07. Buscado con el **MCP de Perplexity**
(`perplexity_search`), porque perplexica estaba agotada ese día; y con la **API
de GitHub** para el estado del repositorio. Cada punto trae su fuente y su fecha.

Están en orden de qué tan cerca están de la tesis del proyecto. **Los tres
primeros son los únicos que se recomiendan de verdad**; el resto está listado
para que se pueda decir que no a algo concreto.

### P1 — Que la báscula se pese a sí misma 🔴 el más importante

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

### P2 — Dar mecanismo a C13 (que una capa no se certifique a sí misma) 🟡

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

### P3 — Lecturas caras, guardadas con su edad 🟡

Hoy `--all` corre las promesas lentas y `scale` a secas las declara `unmeasured`.
El modo rápido nunca ve el resultado de las lentas, así que el parte de todos los
días está incompleto por diseño. La implementación viva ya resolvió esto: la
corrida completa de cada noche deja su resultado en un archivo, y el modo rápido
lo **lee con su hora** si tiene menos de 26 horas, mostrando la edad en el texto.

La trampa a evitar —y por eso esto va con P2 y no antes— es que una lectura
guardada que se muestra sin su edad es una lectura vieja disfrazada de fresca.
Se propone que **sea imposible mostrarla sin decir de cuándo es**, y que al pasar
del límite vuelva a `unmeasurable`, no a `unmeasured`.

### P4 — Un estado más: "apagada a propósito" ⚪ solo si hace falta

La implementación viva tiene un sexto estado para las promesas que su dueño pausó
a conciencia, ordenado **por debajo** de las cumplidas, para que algo apagado a
propósito no compita por el peor lugar del parte.

En una librería de un archivo esto es peso muerto hasta que alguien tenga una
promesa que quiera silenciar por semanas. **Se propone NO hacerlo todavía**, y
dejarlo escrito para que la próxima persona que lo piense sepa que ya se pensó.

### P5 — Contratos de entrada para las sondas ⚪

Cuando una promesa se mide leyendo la salida de otro programa, parsear texto con
expresiones regulares es frágil de una forma silenciosa: el otro programa cambia
un renglón y la promesa empieza a contestar mal sin romperse. La implementación
viva pasó de leer texto a exigir un JSON con número de esquema y campos
declarados; un campo renombrado sin subir el esquema **se declara**, no se
rellena a mano.

Es una buena idea y probablemente **no pertenece a este archivo**: es una
recomendación para el README ("no parsees texto de otro programa"), no una API.

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

**Lo que el estado del arte pide y aquí falta:** la vigilancia de que el chequeo
haya corrido (P1). Es el hueco real, y lo nombran las dos fuentes de arriba.

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

**Horizonte 1 — cerrar la tesis sobre sí misma.** P1 (que la báscula se pese a
sí misma) y P2 (mecanismo para C13). Son las dos capacidades que el propio
README implica y no tiene. Ninguna añade dependencias ni archivos.

**Horizonte 2 — que el parte diario esté completo.** P3, lecturas caras
guardadas con su edad, con la garantía de que no se puedan mostrar sin decir de
cuándo son. Solo tiene sentido después de P2.

**Horizonte 3 — lo que decida el experimento.** Vence el **2026-10-02**. Si
llegan preguntas, contestan ellas qué falta y este archivo se refresca con lo
que digan. Si no llega ninguna, eso también contesta: el proyecto está terminado
como pieza de una sola persona, y `v0.1.0` puede quedarse quieta sin que eso sea
un abandono.

**Fuera de todos los horizontes:** PyPI, exportadores, notificaciones,
reintentos. Ver arriba.

---

## Bitácora de refrescos

- **2026-09-07** — Creado en modo DEFINIR, en el loop nocturno, con Heroldo
  dormido. Alcance COMPROMETIDO reconstruido del README, los docstrings, el
  workflow y los dos mensajes de commit. Todo lo minado entró como PROPUESTO.
  Estado del arte buscado con el MCP de Perplexity (perplexica agotada ese día)
  y con la API de GitHub. Nada aquí está confirmado por Heroldo.
