# CLAUDE.md — promise-scale

**Qué es:** `promise-scale` es una **librería de Python de un solo archivo, sin
dependencias** (Python 3.9+, MIT), **publicada en GitHub** en
`github.com/heroldoe-create/promise-scale`, para que un sistema declare lo que
promete y se pese — con una sola tesis: **`unmeasurable` nunca cuenta como verde**.
**Dónde manda la ley de la máquina:** `~/CLAUDE.md` (la ley del servidor) está por
encima de este archivo; aquí solo se decide lo propio del proyecto (su árbol, su
stack, su ciclo). Si algo de aquí contradice al padre, **gana el padre**.

---

## ⚠️ El idioma no es cosmético: este repositorio es público y está en inglés

| Qué | Idioma | Por qué |
|---|---|---|
| `promise_scale.py`, `minimal.py`, `example.py`, `test_promise_scale.py` — código, docstrings y comentarios | **inglés** | El repositorio es público; lo lee gente que no habla español |
| `README.md`, `CONTRIBUTING.md`, `CHANGELOG.md`, `LICENSE`, `.github/**` | **inglés** | Son la cara pública del proyecto |
| `CLAUDE.md`, `PROYECTO_MAPA.md`, `HORIZONTE.md`, `ESTADO.md`, `BITACORA.md`, `REVISION-*.md`, `TRASPASO-*.md` | **español** | Son documentos internos del parque, como en los otros 20 proyectos del servidor |

**Traducir un documento de la columna de arriba es un defecto, no una mejora.**
Y al revés: escribir en inglés un documento interno del parque lo saca del lugar
donde las demás mesas lo leen.

---

## 🌱 Cómo crece este repositorio (el proceso, dictado)

*Dictada el **2026-09-12** por la cadena `/grafo` (modo NORMAR), leyendo el disco.
Rige desde esa fecha para toda sesión que toque esta carpeta.*

**Esta sección existe para que la sesión número veinte no invente su propio orden.**
Sin ella, cada pasada decide de nuevo dónde poner las cosas, y el repositorio
termina ordenado por quien lo tocó al último en vez de por el trabajo.

### 1 · El principio: la raíz es PLANA a propósito, y las carpetas son por QUIÉN LAS CORRE

Este es un **repositorio de software**, así que el eje es **por quién lo corre / qué
componente es** — pero con una restricción que manda sobre el eje y que está escrita
en `HORIZONTE.md` C10 y en `CONTRIBUTING.md`:

> **La librería es UN archivo.** `promise_scale.py` no se parte, no se mete en un
> paquete, no gana vecinos. «Copiar un archivo» es toda la instalación, y una
> carpeta `src/` o `promise_scale/` rompería esa promesa sin avisar.

De ahí sale el árbol real, y es todo el árbol:

```
promise-scale/
├── promise_scale.py          ← la librería. Un archivo. No se parte.
├── minimal.py  example.py  test_promise_scale.py   ← ejemplos y arnés, sueltos en la raíz
├── README.md  CONTRIBUTING.md  CHANGELOG.md  LICENSE   ← la cara pública (inglés)
├── CLAUDE.md  PROYECTO_MAPA.md  HORIZONTE.md  ESTADO.md  BITACORA.md
│   REVISION-2026-09-07.md  TRASPASO-NEGOCIN-2026-09-11.md   ← lo interno (español)
├── .github/                  ← lo que corre GitHub
└── .claude/                  ← lo que dejan las mesas
```

**El tema vive en el nombre del archivo, nunca en la ruta.**

### 2 · Qué va en cada carpeta — y qué NO va, que es la mitad que se olvida

*Un renglón por carpeta de primer nivel **que existe hoy en disco** (`ls -a`,
2026-09-12). No hay ninguna otra.*

| Carpeta | Sí va | **No va** |
|---|---|---|
| **la raíz** (`.`) | `promise_scale.py` y nada más que se le parezca; los ejemplos ejecutables (`minimal.py`, `example.py`), el arnés (`test_promise_scale.py`), los cuatro documentos públicos en inglés y los documentos internos en español | **Un segundo archivo de librería** (`CONTRIBUTING.md`: se rechaza por escrito) · `setup.py`, `pyproject.toml`, `requirements.txt` o cualquier empaquetado (C10 y el epitafio de PyPI en `HORIZONTE.md`) · archivos de salida de una corrida (`*.jsonl`, `last-full.json`: los escribe la báscula **fuera** del repo y `.gitignore` los excluye) · temporales y borradores |
| **`.github/`** | Lo que ejecuta o publica GitHub: el workflow de CI (`workflows/scale.yml`), la plantilla que se ofrece a otros repos (`workflow-templates/`) y los recursos de la ficha pública (`assets/`) | Pruebas propias (van en el arnés de la raíz, que corre sin CI) · documentación del proyecto · cualquier secreto o token — las llaves de GitHub Actions viven en *Settings → Secrets*, **nunca en un archivo** (`~/CLAUDE.md` §4.2) |
| **`.claude/`** | Los rastros que dejan las mesas del parque: `pending-skill-log/<skill>-<fecha>.md`, candidatos de log pendientes de integrar | Documentos del producto (van a la raíz, en español) · configuración que otra sesión necesite para trabajar (esa va aquí, en `CLAUDE.md`) · nada que deba leer un usuario del repositorio público |

*La columna de la derecha no es decorativa: una carpeta sin frontera escrita acumula
lo que nadie supo dónde poner.*

### 3 · Cuándo se abre una carpeta nueva — la prueba de tres

Se abre **solo si las tres se cumplen**:

1. **Es un “quién lo corre” que hoy no existe** — un ejecutor distinto de GitHub, de las mesas y del propio Python del repo. No un tema, no un subtema, no «los ejemplos».
2. **Va a tener más de tres o cuatro archivos.** Con menos, el archivo vive en la raíz con un prefijo en el nombre. *Hoy hay tres ejemplos/arneses sueltos en la raíz y por eso **no** hay `examples/`.*
3. **Se puede decir en una línea qué NO va en ella.** Si no puedes escribir esa línea, la carpeta no tiene frontera.

**Y una cuarta que aquí manda sobre las tres:** ninguna carpeta nueva puede hacer que
`promise_scale.py` deje de copiarse solo. Si la carpeta obliga al usuario a copiar
dos cosas, no se abre — se rechaza, como dice `CONTRIBUTING.md`.

**Al abrirla, en el mismo turno:** se agrega al árbol del §1, se agrega su renglón a
la tabla del §2 **con su columna de “no va”**, y se anota en `BITACORA.md` por qué se
abrió.

### 4 · Cuándo NO se abre una carpeta — y esto pasa más seguido

- **Para separar por tema.** El tema va en el nombre del archivo.
- **Para separar por fecha.** La fecha va en el nombre del archivo (`REVISION-2026-09-07.md`, `TRASPASO-NEGOCIN-2026-09-11.md` — así ya está hecho).
- **Para separar “lo viejo”.** Lo superado se marca en su encabezado y se queda donde está. *Medido el 2026-09-12: una mesa movió `REVISION-2026-09-07.md` a `90_superado/` y hubo que regresarlo con `git mv`, porque `HORIZONTE.md:43` y `BITACORA.md:169` lo citan por nombre.*
- **Para separar los documentos internos de los públicos.** Ya están separados por idioma y por nombre; una carpeta `docs/` o `es/` rompería los enlaces que ya existen entre ellos.
- **Porque otra taxonomía se ve más limpia.** Reorganizar rompe enlaces internos. **Se reorganiza cuando algo falla** —no encuentras un archivo, hay dos versiones en conflicto, no puedes rastrear una cifra— **nunca por estética.**
- **Más de dos niveles bajo la raíz.** El único que existe hoy es `.github/<sub>/<archivo>`. Si hace falta un tercero, casi siempre una carpeta está haciendo dos trabajos.

### 5 · Nombres

| Tipo de archivo | Cómo se nombra | Ejemplo real |
|---|---|---|
| Código y arnés | `snake_case.py`, en inglés | `promise_scale.py`, `test_promise_scale.py` |
| Documento público | `MAYUSCULAS.md`, en inglés, el nombre que espera GitHub | `README.md`, `CONTRIBUTING.md` |
| Documento interno vigente | `MAYUSCULAS.md`, en español, **sin fecha** — la versión va DENTRO | `HORIZONTE.md`, `ESTADO.md` |
| Documento interno de una corrida fechada | `TIPO-AAAA-MM-DD.md` o `TIPO-DESTINO-AAAA-MM-DD.md` | `REVISION-2026-09-07.md`, `TRASPASO-NEGOCIN-2026-09-11.md` |
| Rastro de una mesa | `.claude/pending-skill-log/<skill>-<fecha>.md` | `.claude/pending-skill-log/revision-2026-09-07.md` |

- **Sin espacios, sin acentos, sin `ñ`** en el nombre. Los acentos van en el CONTENIDO.
- **Prohibido:** `final` · `FINAL2` · `definitivo` · `bueno` · `este_si` · `Nueva carpeta` · `promise_scale_v2.py`.
- **Cuando el archivo es el documento vigente, la versión va DENTRO del documento**, no en el nombre. Versionar por nombre deja copias sueltas y nadie sabe cuál manda. La versión de la **librería** vive en `promise_scale.py:74` (`__version__`) y en `CHANGELOG.md`, en ningún otro lado.
- **Las llaves de estado (`kept`, `warning`, `broken`, `unmeasurable`, `unmeasured`) y las `key=` de cada promesa son DATOS, no etiquetas.** Cambiarles el texto reinicia el «desde cuándo» de todo el mundo y la corrida que lo hace se ve completamente normal. Ver `CONTRIBUTING.md` §*Renaming things*.

### 6 · El ciclo de una pasada de trabajo

Cada paso **deja un archivo. Si no dejó archivo, no pasó.**

| # | Paso | Deja en |
|---|---|---|
| 1 | La pregunta del turno, en una frase | `BITACORA.md` al cerrar |
| 2 | La fuente externa que se va a usar (un doc del estado del arte, una medición por API) → **se registra el mismo día, con su fecha y su buscador** | `HORIZONTE.md`, en el apartado que la usa |
| 3 | El caso plantado, **ANTES** que la promesa que lo necesita | `test_promise_scale.py` o `example.py` (`@planted`) |
| 4 | Lo hecho, con su método y su límite declarado | `BITACORA.md` |
| 5 | **El amarre: cada cifra que se cite a su comando y su salida** | el mismo documento donde se cita la cifra |
| 6 | Lo que se entrega, si cambia lo que el usuario ve | `README.md` y `CHANGELOG.md` (**en inglés**) |
| 7 | Lo que quedó sin contestar, y lo IRREVERSIBLE con su comando escrito y sin ejecutar | `HORIZONTE.md` |
| 8 | Qué cambió y qué se retiró | `BITACORA.md`; y `CHANGELOG.md` **solo** si el cambio lo ve quien usa la librería |
| 9 | La foto medida al cerrar | `ESTADO.md` |

**El paso 3 no es negociable y es la regla que este proyecto le exige a los demás:**
*una promesa nueva llega con su caso plantado, o no llega* (`CONTRIBUTING.md`).
**Y el paso 5 se hace en el paso 5, no al final.** Amarrar al cerrar es reconstruir
de memoria, y de memoria es exactamente como se pierde el comando.

**`CHANGELOG.md` es el historial de la LIBRERÍA, no el diario de las mesas.** El
diario es `BITACORA.md`. Meter ahí una pasada de gobierno interno ensucia lo único
que lee un desconocido para saber qué cambió en el archivo que copió.

### 7 · Nada se borra

- Lo superado **se marca en su propio encabezado** y se queda. Un documento que explica por qué dejó de valer enseña más que su ausencia.
- Cuando de verdad estorbe, pasa a `90_superado/` **dentro del repo** — pero antes se comprueba con `grep -rn "<nombre del archivo>" *.md` que ningún documento vivo lo cite por nombre. *Hoy esa carpeta NO existe, y no debe crearse hasta que haga falta de verdad.*
- **Los archivos temporales y de prueba se crean FUERA de esta carpeta.** La propia báscula ya lo hace: `history.jsonl` y `last-full.json` viven en `~/.local/share/…`, no aquí.
- **Prohibido cualquier borrado con comodín** (`rm -f *.py`). Un comodín no sabe qué es tuyo. (`~/CLAUDE.md` §4.1.)

### 8 · Cuando el proyecto crezca de tamaño

- **La librería NO crece en archivos, crece en líneas.** `promise_scale.py` va en 839 líneas (medido 2026-09-12). Si algún día estorba su tamaño, la salida **no** es partirlo: es quitarle alcance, y eso se decide en `HORIZONTE.md`, no en el árbol.
- **Ejemplos:** a partir de **cuatro** archivos de ejemplo sueltos en la raíz se abre `examples/` (hoy son dos: `minimal.py` y `example.py`).
- **Documentos fechados:** a partir de **seis** `REVISION-*`/`TRASPASO-*` en la raíz se abre `historial/`, y en ese mismo turno se corrigen las citas por nombre que existan en `HORIZONTE.md` y `BITACORA.md`.
- **Y lo que NO cambia al crecer:** el eje del §1 (un archivo de librería, raíz plana), la prueba de tres del §3, la regla del caso plantado del §6 y el reparto de idiomas de arriba.

### 9 · Antes de cerrar cualquier pasada

- [ ] ¿Cada archivo nuevo está donde le toca por el §1, y ningún documento público quedó en español ni ningún documento interno en inglés?
- [ ] ¿Si abrí una carpeta, agregué su renglón al §2 con su columna de “no va”?
- [ ] ¿Cada promesa nueva llegó con su caso plantado, y `--test` lo cuenta?
- [ ] ¿Corrí los tres arneses y pegué su salida? `python3 test_promise_scale.py` · `python3 example.py --test` · `python3 example.py --all --brief` dos veces (la primera **debe** salir 3).
- [ ] ¿Las cifras nuevas quedaron amarradas a su comando y su salida?
- [ ] ¿Anoté en `BITACORA.md` qué cambió y qué se retiró — y en `CHANGELOG.md` **solo** si lo ve quien usa la librería?
- [ ] ¿Quedó algo temporal dentro de la carpeta? Sácalo o decláralo. (`git status --porcelain` debe quedar limpio de lo que no es tuyo.)

### Lo que hace que esta sección no sea solo texto

**PENDIENTE: el verificador de esta ley no existe.** Lo mecanizable de arriba
—que exista lo que el §2 promete, que ningún nombre rompa el §5, que no haya
carpetas fuera del §1, que toda ruta citada en los `.md` exista en disco— se puede
comprobar con un script, pero **no se creó en la pasada del 2026-09-12 porque el
encargo de esa corrida prohibía expresamente tocar código y scripts**. Falta:
decidir dónde vive sin romper el §1 (un script de gobierno **no** es un segundo
archivo de librería, pero sí es un archivo más en la raíz pública de un repo cuyo
argumento es «copia un archivo»), y escribirlo. Mientras no exista, el §9 se corre
a mano y esta línea se queda visible.

---

## 🔗 Dónde vive cada verdad, en este proyecto

| Tema | La verdad vive en | Lo que NO manda |
|---|---|---|
| Qué hace la librería | `promise_scale.py` — **el código** | `README.md` y `PROYECTO_MAPA.md` describen; si discrepan, el que está mal es el documento |
| La versión | `promise_scale.py:74` (`__version__`) | El release de GitHub va detrás a propósito, y `CHANGELOG.md` lo declara |
| El alcance y lo irreversible | `HORIZONTE.md` | `BITACORA.md` y `REVISION-2026-09-07.md` son historia fechada |
| El estado medido | La máquina viva (correr los arneses, la API de GitHub) | `ESTADO.md` es una foto **con fecha**: se re-mide antes de confiar |
| Cómo está conectado todo | `PROYECTO_MAPA.md` | Ninguna otra copia; si aparece una, lo declara en su cabecera |
| Las llaves | El entorno y *Settings → Secrets* de GitHub | **Jamás** un archivo del repositorio — y aquí menos, porque es público |

## ⚖️ Lo que este proyecto NO puede decidir solo

`~/CLAUDE.md` §4 impone cinco cosas que ninguna regla de aquí cambia: nada se borra,
ningún secreto entra a un repositorio, se busca el paquete portable antes de
instalar, toda afirmación de estado se mide, y nada nuevo se publica al internet sin
candado probado.

**La quinta merece una línea, porque parece una contradicción y no lo es.** Este
repositorio **es público sin candado, a propósito y por decisión escrita de Heroldo**
(`HORIZONTE.md` C14: publicado el 2026-09-02 sin promoción, para medir si a alguien
le importa sin empujarlo). La regla del padre habla de **puertas vivas de la
máquina** —servicios que exponen datos o control— y este repositorio no es una: es
código MIT y no da acceso a nada de aquí. Lo que sí aplica con doble rigor es la
§4.2: **en un repositorio público, un secreto filtrado no se puede retirar**, y por
eso la columna «no va» del §2 lo prohíbe en las tres carpetas.
