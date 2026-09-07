# Bitácora

## 2026-09-07 — Cierre del horizonte

La pasada de la madrugada dejó el horizonte ESCRITO y tres cosas en backlog.
Esta lo CIERRA: las cinco propuestas tienen destino y ninguna quedó en
"PROPUESTO". Detalle por propuesta, con su evidencia, en `HORIZONTE.md`.

**Construido (P1, P2, P3), todo aditivo y sin dependencias ni archivos nuevos:**

1. **La báscula vigila que ELLA MISMA corrió.** `Scale(expect_every="24h")` pesa
   una promesa más, siempre, antes que las tuyas. Tarde sale `unmeasurable`,
   nunca `broken`: no aprendiste que el sistema está mal, aprendiste que dejaste
   de mirar. Era el mismo agujero de este proyecto un piso más arriba.
2. **`source=` y `--own`.** Una lectura que no tomaste tú se marca, y la marca
   viaja al parte, al `--json` y a la tabla de promesas; `--own` las tira todas.
   Con esto, "que una capa no certifique la lectura de otra" deja de ser el
   único consejo duro del README sin mecanismo.
3. **Lecturas caras acarreadas con su edad soldada al texto.** La corrida
   completa deja su lectura, la rápida la acarrea diciendo de cuándo es, y
   pasado el límite vuelve a `unmeasurable` — no a `unmeasured`.

**Descartado con medición:** el sexto estado "apagada a propósito" (el archivo
que lo alimenta en la implementación viva **nunca se creó** en cinco días con
catorce promesas corriendo) y los contratos de entrada como API (validar un
esquema es decenas de líneas que no miden nada, contra C10; entró como consejo
del README y como la promesa P6 del ejemplo, que juzga el parte ajeno antes de
creerlo).

**Medido, no citado:**

```
$ python3 test_promise_scale.py            31 → 80 casos, missed=0     EXIT=0
$ python3 example.py --test                13 → 19 casos, missed=0     EXIT=0
                                           every promise has a planted case
Python 3.9  SELFTEST=0  PLANTED=0  primera corrida=3  segunda=0   (docker)
Python 3.13 SELFTEST=0  PLANTED=0  primera corrida=3  segunda=0   (docker)
```

**Que las pruebas muerden, mutando el mecanismo** (no revisando marcadores):
apagar la promesa implícita → 8 casos cazados; apagar `--own` → 2; dejar que el
acarreo archive cualquier cosa → 2. Sin mutación, 80 en verde.

**El fallo callado que solo salió corriendo el ciclo entero.** Con los casos
nuevos ya verdes, el ejemplo corrido dos veces sobre un `HOME` limpio enseñó que
la primera corrida rápida archivaba su propia nota de *"todavía no hay lectura
guardada"* y la segunda la acarreaba como si fuera una medición. Una nota que
dice "no pude medir" no es una medición. Arreglado (solo se archiva lo que midió
una corrida que incluía ese modo) y plantado en tres casos. Es la segunda vez
seguida que el arnés está verde y el agujero aparece al correr el ciclo completo.

**La decisión que estaba sobre la mesa, cerrada.** `__version__` → `0.2.0`, y
`CHANGELOG.md` nuevo cuya primera sección **declara** que la etiqueta de GitHub
va detrás (`v0.1.0`). Cortar el release es de Heroldo y no se hizo: el comando
está escrito en `HORIZONTE.md` y en el CHANGELOG, listo para pegar. El código
deja de mentir sobre sí mismo y la brecha queda dicha en vez de escondida.

**En CI:** el ejemplo corre dos veces y se exige que la primera salga **3**. Es
la prueba de punta a punta de la vigilancia: si se calla, la primera corrida
sale verde y ese paso truena. Comprobado forzándolo antes de subirlo.

**El `[NO VERIFICADO]` de la pasada anterior, medido — y sale que NO.** La
imagen de vista previa social **no está asignada**: el `og:image` de la página
apunta a `opengraph.githubassets.com`, que es la tarjeta que GitHub genera solo;
una imagen propia se sirve desde `repository-images.githubusercontent.com`.
Discriminante comprobado contra cuatro repos (dos con imagen propia, dos sin
ella). La API no lo expone, pero la página sí — se declaró bloqueado sin haber
mirado ahí. Que el archivo esté en el repo no prueba que esté publicado.

**Lo que NO se hizo, y por qué:** cortar el release (**IRREVERSIBLE**, con el
comando escrito, excluido por escrito) y asignar la imagen de vista previa (dos
clics en *Settings → General*, sin endpoint público — le toca a Heroldo, pero
ya sabe que hace falta en vez de no saberlo).

## 2026-09-07 — Loop de revisión y cierre (mesa Claude, Heroldo dormido)

**Veredicto de /revision:** 🔴 al auditar — cobertura 14 de 25 · 🟡 al cerrar — 24 de 25

### Lo que se cerró hoy

**1. La regla del proyecto, que no se cumplía dentro del proyecto.**
Una sonda que devolvía un estado fuera de los cinco (un dedazo: `"KEPT"` en vez
de `"kept"`) contaba como medida, no casaba con ninguna falla, y el proceso
salía **0, en verde**. Medido antes:

```
verdict: {'kept': 1, 'measured': 2, 'broken': [], 'unmeasurable': [], 'exit_code': 0}
kept 1/2
PROCESS_EXIT=0
```

Y con la salida por defecto la misma entrada tumbaba el parte entero con
`KeyError: 'KEPT'` en `promise_scale.py:371`.

Tocado: `promise_scale.py` — se añadió `_STATES`; `weigh()` pliega cualquier
estado ilegible a `UNMEASURABLE` diciendo qué llegó; `verdict()` aplica la misma
regla a lecturas que no produjo la báscula; el parte usa `.get()` en la paleta.
Medido después:

```
verdict: {'kept': 1, 'measured': 2, 'unmeasurable': ['B'], 'exit_code': 3}
kept 1/2 · could not measure B
PROCESS_EXIT=3
```

**2. La regla de contribución más dura del proyecto, que era inaplicable.**
El README pide en negritas que *"una promesa nueva llega con su caso plantado, o
no llega"*, pero `@planted` recibía un nombre libre, no la clave de la promesa:
nada podía saber qué promesa estaba descubierta.

Tocado: `promise_scale.py` — `key=` opcional en `@planted`, `_coverage()`, y
`run_planted(..., registry=)`. Es **reporte, no falla**: no cambia el número de
fallos ni el código de salida, y la línea solo aparece si algún caso declara
`key`, así que una suite que no se apunte no ve ningún cambio.

**3. El ejemplo incumplía la regla que enseña.** `P5` era la única promesa sin
caso plantado, y no por descuido: tenía el juicio escrito *dentro* de la promesa,
que es justo lo que el README dice que hace imposible plantar.
Tocado: `example.py` — se extrajo `judge_suite()` siguiendo el patrón que ya
usaban las otras cuatro, y se añadieron sus dos casos. Salida real:

```
  [planted] cases=13 missed=0
  every promise has a planted case
PLANTED_EXIT=0
```

**4. Casos plantados nuevos en el arnés propio: 20 → 31.** Cubren el estado
ilegible (que no sea verde, que salga 3, que no cuente como cumplida, que
`verdict` la cace también en lecturas ajenas), que el parte sobreviva a un
estado que la paleta no conoce, y las tres formas del reporte de cobertura.

```
$ python3 test_promise_scale.py
  [scale-self-test] missed=0        SELFTEST_EXIT=0
```

**5. Verificado en las tres versiones del CI, corriendo, no citando.**

```
Python 3.9.25   SELFTEST_EXIT=0  PLANTED_EXIT=0  kept 5/5  BRIEF_EXIT=0
Python 3.13.15  SELFTEST_EXIT=0  PLANTED_EXIT=0
Python 3.14.4   SELFTEST_EXIT=0  PLANTED_EXIT=0   (local)
```
(3.9 y 3.13 en docker: `docker run --rm -v "$PWD":/w -w /w python:3.9-slim …`)

**6. Contradicción del ejemplo, medida y cerrada.** `example.py` decía *"Nothing
here touches your machine"* y escribe `~/.local/share/example-scale/history.jsonl`
— comprobado: el archivo existe, 593 bytes. Se añadió la frase que faltaba
(y que `--no-history` lo evita), sin quitar nada de lo que había.

**7. Seis capacidades construidas que nadie había escrito**, ahora en el README:
`check()`, los alias `KEPT`/`WARN`/`BROKEN`, `--no-history`,
`python3 -m promise_scale`, `Scale(history=None)`, `NO_COLOR`. Más dos
aclaraciones: que `scale` es *tu* archivo y no un binario, y que los códigos de
salida son de la corrida, no del estado.

**8. La afirmación "This part I could not find anywhere", matizada con fuentes
en vez de borrada.** El estado existe en Azure Monitor con el nombre `Unknown`;
lo que no existe es el orden. Documentado con enlaces y fechas — deja al
proyecto mejor parado, porque ahora la diferencia está medida y no declarada.

**9. `CONTRIBUTING.md`** — no existía, con Discussions abiertas. Corto: la regla
del caso plantado, cómo correr las tres cosas, qué se va a rechazar (una
dependencia, un estado que suavice `unmeasurable`, un segundo archivo de
librería), y por qué renombrar un estado o una clave rompe el historial de todos
en silencio.

**10. `REVISION-2026-09-07.md`, `HORIZONTE.md`** y el log de la fase A.

### Lo que NO se logró cerrar y por qué

- **`NO-AUTO-CERTIFICAR`** — que una capa no certifique la lectura de otra, el
  único de los tres consejos duros del README sin mecanismo.
  **BACKLOG DEL PROYECTO**: es API pública nueva, no un arreglo. El diseño ya
  está probado en la implementación viva (`del_parte` / `--propias`) y quedó
  propuesto en `HORIZONTE.md` con su forma.

- **La báscula no se pesa a sí misma** — si borran el cron, nada lo nota.
  **BACKLOG DEL PROYECTO**: capacidad nueva. Es el mismo agujero del proyecto un
  piso más arriba, y por eso encabeza el horizonte.

- **El parte de ejemplo del README no lo produce ningún comando** (muestra `P2
  BROKEN`; `example.py` da `kept 5/5`). **BACKLOG DEL PROYECTO**: no es un error
  que se resuelva midiendo, es decidir si el README enseña el caso verde o el
  roto. No se inventó cuál.

- **`git commit` / `git push`** — **EXCLUIDO** por escrito en las instrucciones
  de esta noche. Todo queda en el árbol de trabajo, sin `git add`.

- **`timedelta` importado y sin usar en los tres archivos** — **EXCLUIDO** por la
  regla de cambios quirúrgicos: es código muerto preexistente y nadie pidió
  limpiarlo. Anotado en la revisión.

- **Si la imagen de vista previa social está realmente asignada** — el archivo
  está en el repo, pero asignarla son dos clics en la web y la API no lo expone
  donde se buscó. **BLOQUEADO**, marcado `[NO VERIFICADO]`.

### La decisión que quedó sobre la mesa

**`__version__` sigue en `"0.1.0"` y ya no describe lo que hay en disco.** El
release `v0.1.0` de GitHub apunta al primer commit. Subirla a `0.2.0` crea una
versión sin release; dejarla crea código que miente sobre sí mismo — en un
proyecto sobre no mentir sobre uno mismo. Se dejó como está porque cortar
releases es de Heroldo. No hay `CHANGELOG.md`.

### La trampa para quien siga

**El arnés estaba verde porque solo le daban entradas válidas.** Veinte casos
plantados, CI en tres versiones de Python, todo en 0 — y ninguno preguntaba qué
pasa cuando una sonda contesta algo que la báscula *no sabe leer*, que es
literalmente el enunciado de la tesis del proyecto aplicado a sí mismo. La
próxima regla que este repo declare, plántala **contra su propio código y con la
entrada que la regla nombra**, no solo contra el camino feliz. Aquí ese camino
tenía veinte casos y el agujero estaba a un dedazo de distancia.

Y la segunda: **`_COLOR[...]` con corchete y `_COLOR.get(...)` se ven igual en
una revisión de código.** El primero convierte un dato raro en un traceback que
mata el parte completo. En un programa cuyo trabajo es seguir contestando cuando
algo sale mal, cada acceso directo a un diccionario indexado por dato ajeno es
una forma de callarse. Quedan pocos; míralos antes de añadir el siguiente.
