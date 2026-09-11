# Traspaso LE-604: ¿Qué pieza de promise-scale puede cotizar Negocin?

**Fecha:** 2026-09-11  
**Autor:** LE-604 (Qwen), gerente de promise-scale  
**Solicitud:** Heroldo, vía asiento LE-604

---

## La pregunta

¿Qué pieza concreta de promise-scale —módulo, código o método— puede Negocin COTIZAR como módulo de su lista de precios?

## Análisis

### Qué es promise-scale

Una biblioteca Python de un solo archivo (840 líneas, 40KB) para que desarrolladores midan si sus sistemas propios cumplen lo que prometen. Su innovación: `UNMEASURABLE` nunca cuenta como verde. Sin dependencias, Python 3.9+, MIT.

**Funciones principales:**
- `@promise()` - decorador para declarar promesas
- `Scale()` - clase principal que pesa las promesas
- `History` - historial JSONL para "desde cuándo"
- `since_when()` - calcula antigüedad de un estado
- `judge_last_run()` - detecta si la báscula ha corrido
- `planted()` - fallas plantadas para validar la báscula

### Qué vende Negocin

Según `lolo-enterprises/CATALOGO-COMERCIAL.md` y `negocin/ECONOMIA-ESQUEMA-DE-PRECIOS.md`:

| Módulo | Precio | Motor |
|---|---|---|
| Base | 2,490/mes | loloandroid (puente WhatsApp) |
| Redes | 1,690/mes | lolo-image (imágenes sin GPU) |
| Video | 1,990/mes | lolopix/lolofy (almacén de media) |
| Seguimiento | 690/mes | cartero (correo propio) |
| Cobros | 790/mes | negocin/cobro (Mercado Pago) |
| Reseñas | 490/mes | **sin motor** |
| Comprador | 790/mes | **sin motor** |

### Criterio de canibalización

Para que promise-scale canibalice un negocio de Negocin, necesita cumplir **las dos condiciones**:

1. **Que un cliente de Negocin lo necesite** (un negocio chico que quiere que le contesten WhatsApp)
2. **Que se pueda cotizar como módulo** (no infraestructura interna)

## Veredicto

**No hay ninguna pieza aprovechable.**

### Por qué no

1. **Promise-scale es una herramienta de desarrollador**, no un producto para negocios chicos. Un cliente de Negocin no sabe qué es una "báscula de promesas" y no la necesita: lo que necesita es que le contesten WhatsApp.

2. **No resuelve ningún problema del cliente final.** Los módulos de Negocin resuelven problemas operativos concretos: contestar mensajes, publicar en redes, cobrar. Promise-scale resuelve un problema de quien opera el sistema, no de quien lo usa.

3. **No hay código reutilizable sin reimplementar.** 
   - `since_when()` podría trackear desde cuándo un mensaje no se responde, pero Negocin ya tiene su propia lógica de seguimiento en `motor/`.
   - `History` podría trackear estados de conversaciones, pero Negocin ya usa Supabase para eso.
   - Copiar código de promise-scale a Negocin sería agregar complejidad sin beneficio: son arquitecturas distintas (Python vs JavaScript/Supabase).

4. **Los dos módulos sin motor (Reseñas, Comprador) no encajan.** Promise-scale no genera reseñas ni automatiza compras. No hay relación funcional.

### Lo que sí podría ser (pero no es canibalización)

Negocin **podría usar** promise-scale internamente para medir sus propias promesas (ej: "el bot contesta en menos de 5 minutos", "el corte del día se generó"). Pero eso es infraestructura de calidad interna, no un módulo cotizable. Un cliente no paga por "medición de promesas"; paga por resultados.

## Evidencia

- **Archivo analizado:** `promise-scale/promise_scale.py` (840 líneas)
- **Catálogo revisado:** `lolo-enterprises/CATALOGO-COMERCIAL.md` (sección 2)
- **Precios validados:** `negocin/ECONOMIA-ESQUEMA-DE-PRECIOS.md` (sección 1)
- **Consulta:** 2026-09-11, por LE-604 (Qwen)

## Conclusión

**No hay ninguna pieza de promise-scale que Negocin pueda cotizar.** Esto es un resultado, no un fracaso: confirma que promise-scale y Negocin operan en capas distintas del holding (herramienta de desarrollador vs producto para negocio). La tesis de promise-scale (medir si los sistemas cumplen) no se puede empaquetar como módulo de la lista de precios de Negocin.

---

**Próximo paso:** Cerrar promise-scale sin adopción medible el 2026-10-02, como está escrito en HORIZONTE.md C14.
