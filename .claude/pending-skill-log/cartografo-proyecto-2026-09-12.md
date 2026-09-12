# [LOG-CANDIDATO B] — integrar en `support/cartografo-log.md` (ruta relativa)

- **Fecha:** 2026-09-12
- **Proyecto mapeado (ruta raíz):** `/mnt/respaldo/proyectos/promise-scale`
- **Nº de nodos / Nº de relaciones inferidas con "(?)":** 19 nodos en el grafo Mermaid, 20 aristas, **0 relaciones con "(?)"** — todas salen de un `import`, de una cita por nombre en un documento o de una línea del workflow.
- **Generación inicial o incremental:** **inicial** (v1.0). No existía `PROYECTO_MAPA.md`; `REVISION-2026-09-07.md:5-6` lo declaraba expresamente ausente. Atraso: todo el repositorio, 9 commits y 10 días (`4aa7c2d` 2026-09-02 → `bf3fadc` 2026-09-12).
- **¿Hubo error de calibración?:** No.
- **Tipo:** ninguno. La Fase 2.bis corrió con comprobador: 23 rutas citadas, 19 existen, 4 (`history.jsonl`, `last-full.json`, `setup.py`, `pyproject.toml`) declaradas inexistentes **a propósito** con su razón escrita. 0 nodos fantasma.
- **Regla aprendida:**
  - Cuando el repo sea **público y en un idioma distinto al del parque**, no asumir que «reparar la documentación» incluye traducirla: el reparto de idiomas es una frontera del proyecto y va escrita en el mapa y en la ley antes de tocar nada.
  - Cuando el repo sea **single-file por decisión escrita** (aquí `HORIZONTE.md` C10), no asumir que la ausencia de `setup.py`/`pyproject.toml`/`src/` es una omisión: exigir la cita que lo declara intencional antes de marcarlo como hueco, y registrarlo como «no existe a propósito», no como faltante.
  - Exigir como evidencia mínima de nodo: existencia en disco comprobada con `test -e` **más** una arista real (import, cita por nombre, o línea del CI). Un archivo que existe y que nadie nombra se marca "(?)", no se conecta.
- **Recurrencia detectada:** **histórico no leído** — `support/cartografo-log.md` vive en la carpeta instalada del plugin y esta corrida no lo abrió. No se afirma ninguna recurrencia.
- **Qué vigilar en la próxima corrida:** (1) si la contradicción interna de `ESTADO.md` sobre el release `v0.2.0` y la vista previa social (tabla: BLOQUEADA · veredicto del CEO: MATADAS) sigue abierta — el mapa la dejó como PENDIENTE DE CONFIRMAR porque describir no es decidir; (2) si el experimento C14 venció el 2026-10-02 y con qué resultado; (3) si apareció el verificador de la ley de crecimiento, que quedó PENDIENTE visible en `CLAUDE.md` porque el encargo prohibía tocar scripts.

**ESTADO: EMITIDA, NO PERSISTIDA EN EL LOG CANÓNICO (pendiente de integración).**
