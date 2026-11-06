# Design — CH-04 `catalogo-auxiliar-repo-uow`

## Context

Motivación: `proposal.md` § Why. Requisitos: `specs/catalogo-auxiliar/spec.md`. Base de partida: `main` con CH-01, CH-02 y CH-03 (commit `1a87fa5`). Las clases base (`BaseRepository`, `UnitOfWork`, `paginacion.py`, `errores.py`) se usan como están y no se modifican.

## Decisions

### D1. Un repositorio y un Unit of Work por módulo, sin métodos extra
Los tres repositorios solo pasan la clase del modelo a `BaseRepository`. No hacen falta métodos con nombre propio: ninguna lectura del catálogo auxiliar filtra ni precarga relaciones (las de libros son de CH-05). Si una operación los necesitara, el método se agrega en el repositorio hijo con su precarga adentro (§6.5).

### D2. El router construye el Unit of Work; el servicio lo abre
`get_uow(session: SessionDep)` vive en `router.py` (el UoW no sabe nada de HTTP). El servicio recibe el UoW y lo abre con `async with`; nunca lo construye (§6.7). Así la petición usa una sola sesión, que crea y cierra `get_session`.

### D3. Unicidad por la base, traducida en el router
No se consulta antes si el nombre existe (regla dura 11). El `IntegrityError` del `flush()` sale del bloque, el UoW revierte y el router responde 409 con el mensaje de `MENSAJES_CONSTRAINT` (RN-01, RN-15).

### D4. 404 desde el servicio
El servicio levanta `HTTPException(404)` cuando el recurso de la ruta no existe, igual que el código del TP. Al salir del bloque con esa excepción, el UoW revierte (no había nada escrito).

### D5. PATCH: ausente contra nulo
`exclude_unset=True` aplica solo lo enviado (§2.6). Un `null` explícito se rechaza con 422 en el contrato (`rechazar_nulos`), porque las columnas son `NOT NULL`: sin eso llegaría a la base y terminaría en 409.

### D6. Rutas que se quitan
`PATCH /generos/{id}` lo pide la ficha de CH-04. Los `DELETE` de editoriales, géneros y autores los decidió el integrante: la consigna no los lista y el parcial apuesta al historial (borrado lógico en libros, revocación sin borrar en roles). Se mantienen los `GET /{id}` y `GET /autores`, que no contradicen la consigna.

### D7. Puentes temporales hacia CH-05
Las rutas `/{x}/{id}/libros` siguen llamando al servicio viejo de libros con `uow.session`, y `autores/service.get_autor(session, id)` queda porque lo importa `libros/service.py`. Ambos están comentados como pendientes de CH-05; no se tocó ningún archivo de `libros/`.

## Risks / Trade-offs

- **Ids que saltan**: un INSERT rechazado por el UNIQUE consume el valor de la secuencia. Por eso los `.http` esperan id 5 después de un 409. No es un defecto: las secuencias de PostgreSQL no retroceden.
- **Lecturas dentro de `async with`**: los listados también abren el UoW y terminan con un `commit()` sin cambios. Es barato y mantiene una sola forma de trabajar en todos los servicios.
