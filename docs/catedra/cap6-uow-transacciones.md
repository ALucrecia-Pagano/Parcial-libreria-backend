**CAPÍTULO 6 — GUÍA DE LECTURA**

**Repositorios y Unit of Work**

Transacciones, y la operación que no tiene sentido a medias

*Traducción didáctica del texto académico, sección por sección. Mismos conceptos, otro idioma.*

Antes de empezar: cómo usar esta guía

Cada sección tiene **Qué dice** (la idea comprimida), **En criollo** (la explicación larga con la analogía) y **Para el pizarrón** (la frase que hay que llevarse). **No se pierde ni un concepto**: lo que cambia es el idioma.

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p><strong>LA IDEA MADRE DE TODO EL CAPÍTULO</strong></p>
<p><strong>El problema no es que las operaciones fallen. Es que fallen por la mitad.</strong></p>
<p>Si crear un usuario falla entero, <strong>no pasa nada</strong>: el cliente ve un error y vuelve a intentar. <strong>Un fallo limpio es un no-evento.</strong></p>
<p>Lo grave es lo otro: <strong>el usuario se creó y el rol no.</strong> Nadie ve un error —la petición puede haber respondido 500, pero <strong>el usuario quedó guardado</strong>—. Y ese usuario existe, inicia sesión, <strong>y no puede hacer nada</strong>. El sistema quedó en <strong>un estado que ninguna parte del código contempla</strong>.</p>
<p>Todo este capítulo es sobre eso. <strong>La transacción no evita que las cosas fallen: evita que queden a medias.</strong> Es una garantía mucho más modesta y mucho más útil.</p></td>
</tr>
</tbody>
</table>

6.1 — Por qué esta clase llega sexta y no segunda

Qué dice

Este capítulo llega sexto **a propósito**. En las clases 4 y 5 escribiste servicios que tocan varias tablas **usando la sesión directamente**, y en la clase anterior apareció una operación que el TPI describe con una frase que vale como enunciado de toda esta clase:

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p><strong>La frase</strong></p>
<p>El registro inserta la asignación del rol de cliente <strong>en la misma transacción</strong> que crea el usuario. <strong>Sin esa inserción, el usuario recién registrado no puede comprar.</strong></p></td>
</tr>
</tbody>
</table>

Ahí hay **dos escrituras que no tienen sentido por separado**. Un usuario sin rol existe, puede iniciar sesión, y **no puede hacer absolutamente nada**. Es **peor que si no existiera**, porque nadie lo va a notar **hasta que esa persona intente comprar**.

Ese es el problema que este capítulo resuelve, y **presentarlo antes —cuando todavía no dolía— habría convertido el patrón en una ceremonia que se copia sin entender**. Ahora el problema ya se sintió.

El capítulo estudia **dos patrones que Martin Fowler nombró en 2002** y que el TPI declara como capas obligatorias de su flujo Router → Service → UoW → Repository → Model. Y estudia también **las dos excepciones declaradas** al ciclo de vida, que son lo más instructivo de la sección 8.4: una de ellas es **la única operación de escritura del sistema que no comparte la transacción de su petición**, y **la razón por la que debe escapar es de una elegancia que merece detenerse**.

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p><strong>PARA EL PIZARRÓN</strong></p>
<p>Al terminar la clase tenés que poder hacer tres cosas:</p>
<ul>
<li><p><strong>Escribir un repositorio con su precarga declarada.</strong></p></li>
<li><p><strong>Componer un Unit of Work.</strong></p></li>
<li><p><strong>Explicar quién crea la sesión, quién la abre, quién confirma y quién cierra</strong> — que son <strong>cuatro responsabilidades distintas</strong> y en este sistema <strong>están en cuatro lugares distintos</strong>.</p></li>
</ul></td>
</tr>
</tbody>
</table>

6.2 — Por qué existen estos patrones

Qué dice

El problema es **tan viejo como las bases de datos** y se enuncia en una línea: **una operación de negocio casi nunca corresponde a una sola escritura, y las escrituras pueden fallar en el medio.**

La respuesta del motor es **la transacción**: un conjunto de operaciones que **se aplican todas o ninguna**. El concepto se formalizó en los años setenta y ochenta —Jim Gray sentó las bases y el acrónimo que las resume se acuñó en 1983— y sigue siendo **una de las garantías más valiosas que un motor relacional ofrece**, precisamente porque **es muy difícil de reponer en la aplicación**.

**Pero la transacción resuelve el *qué* y deja abierto el *dónde*.** ¿Quién decide que estas cinco escrituras van juntas? ¿Dónde empieza y dónde termina?

La respuesta ingenua es que **cada función que escribe abra su propia transacción y la confirme**. Y eso **rompe exactamente lo que se quería garantizar**: si crear el usuario confirma y después falla la asignación del rol, **el usuario ya está guardado**. Cada pieza fue correcta **y el conjunto quedó inconsistente**.

| **Los dos patrones que Fowler nombró en 2002** | **Qué resuelve**                                                                                                                                                                                                                                                                                                              |
|------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **El repositorio**                             | Separa *«qué datos necesito»* de *«cómo se los pido a este motor»*. El servicio pide **«el pedido con sus líneas»**; el repositorio decide **con qué consulta lo trae**. Eso vuelve al servicio **probable sin base de datos** —se le puede pasar otro repositorio— y **concentra en un solo lugar las decisiones de acceso** |
| **El Unit of Work**                            | Hace de la transacción **un objeto explícito**: alguien la abre, las escrituras se acumulan, y al terminar **se confirma entera o se descarta entera**. **Deja de ser algo implícito que ocurre en algún lado**                                                                                                               |

| **Las cuatro decisiones de diseño del capítulo**                          | **Qué significa**                                                                                    |
|---------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------|
| **1. La transacción es de la operación de negocio, no de cada escritura** | **Quien sabe qué va junto es el servicio**, no el repositorio                                        |
| **2. El repositorio no tiene lógica de negocio**                          | **Sabe traer y guardar; no sabe si se puede**                                                        |
| **3. Quien crea un recurso lo cierra**                                    | Y en este sistema eso significa que **el Unit of Work no cierra la sesión, porque no la creó**       |
| **4. Las excepciones se declaran**                                        | El TPI enumera **dos operaciones que se salen del ciclo de vida general**, con su razón y su alcance |

6.3 — Las cuatro propiedades de una transacción

El acrónimo que resume lo que una transacción garantiza tiene cuatro letras, y **cada una responde a un problema distinto**. Vale verlas **con un ejemplo del dominio**, porque así dejan de ser una definición para memorizar.

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p><strong>OJO ACÁ: de las cuatro letras, hay una que hay que pedir</strong></p>
<p><strong>El aislamiento tiene grados, y el que viene por defecto no alcanza para todo.</strong></p>
<p>PostgreSQL usa por defecto un nivel donde tu transacción <strong>ve sólo lo que otras ya confirmaron</strong>. Suena suficiente. Y no lo es para la secuencia de la figura: <strong>las dos transacciones leen un valor confirmado y escriben sobre él, y el resultado es −3</strong>.</p>
<p><strong>No es un bug del motor: es el grado de aislamiento que elegiste sin saber que estabas eligiendo.</strong></p>
<p><strong>La clase 7 es enteramente sobre este párrafo.</strong></p></td>
</tr>
</tbody>
</table>

<img src="media/d63d96daf43595f72c32f67d3b7b1413e119ba14.png" style="width:5.79167in;height:3.9375in" />

**Figura 6.1** *— Las cuatro propiedades con su caso del dominio, y la que no viene gratis.*

6.4 — El repositorio

6.4.1 — Qué separa

Un repositorio es una clase que **concentra el acceso a datos de una entidad**. El servicio le pide lo que necesita **por su significado**; el repositorio decide **con qué consulta** lo consigue.

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p># El Service pide por significado</p>
<p>pedido = await uow.pedidos.get_by_id(pedido_id, cargar=("items", "usuario"))</p>
<p># El Repository decide cómo</p>
<p>async def get_by_id(self, entity_id: int, cargar: tuple = ()) -&gt; T | None:</p>
<p>consulta = select(self.model).where(self.model.id == entity_id)</p>
<p>for relacion in cargar:</p>
<p>consulta = consulta.options(selectinload(getattr(self.model, relacion)))</p>
<p>return (await self.session.exec(consulta)).first()</p></td>
</tr>
</tbody>
</table>

Esa separación tiene **tres consecuencias**, y la tercera es la que más importa en este proyecto:

- **El servicio se puede probar sin base de datos**, pasándole un repositorio sustituto. Es **la actividad 4 de POO aplicada**: alcanza con que tenga la misma forma.

- **Las decisiones de acceso viven en un solo lugar.** Si hay que agregar un índice o cambiar una consulta, se toca el repositorio y nada más.

- **La precarga se declara donde se sabe cómo se traen los datos.** Y de ahí sale algo práctico: cuando salta la excepción de carga perezosa, **ya se sabe dónde mirar** — en el método del repositorio que trajo ese objeto.

6.4.2 — Dos jerarquías, y por qué no una

El TPI declara **dos** clases base, y da la razón: **un único genérico que filtrara la columna de borrado produciría un error de SQL sobre las tablas que no la tienen.**

<img src="media/c1a64a6316341d31af6cca2e32a0141e756a5aee.png" style="width:5.79167in;height:3.47917in" />

**Figura 6.5** *— Las dos jerarquías, qué modelos hereda cada una, y por qué no alcanza con una.*

Es **una consecuencia directa de la enumeración taxativa de la clase 4**: como **sólo cinco entidades** tienen borrado lógico, un filtro universal **rompería sobre las otras dieciocho**. La alternativa —un condicional que verifique si el modelo tiene la columna— **funcionaría y sería peor**: mueve **a tiempo de ejecución** una distinción que **el sistema de tipos puede expresar**.

6.4.3 — Los genéricos que se borran

Hay un detalle de la firma del constructor que el TPI explica y **que vale por sí solo**: \_\_init\_\_(session, model: type\[T\]) recibe **la clase del modelo de forma explícita**, porque **los genéricos de Python se borran en tiempo de ejecución y select(T) no existe**.

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p>class BaseRepository(Generic[T]):</p>
<p>def __init__(self, session: AsyncSession, model: type[T]):</p>
<p>self.session = session</p>
<p>self.model = model # esto SÍ existe en ejecución</p></td>
</tr>
</tbody>
</table>

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p><strong>PARA ENTENDER: el mejor puente del módulo con lo que ven en el otro turno</strong></p>
<p><strong>Es exactamente el mismo fenómeno que la otra mitad de la cursada estudió como borrado de tipos en TypeScript:</strong> la anotación genérica <strong>existe para el verificador y no llega a la ejecución</strong>. Cuando el código corre, T <strong>no es nada</strong>.</p>
<ul>
<li><p><strong>Los tipos genéricos:</strong> en TypeScript <strong>se borran al compilar</strong>; en Python <strong>se borran en tiempo de ejecución</strong>.</p></li>
<li><p><strong>La consecuencia:</strong> allá <strong>no podés preguntar if (x is Pedido)</strong>; acá <strong>no podés escribir select(T)</strong>.</p></li>
<li><p><strong>La salida es la misma:</strong> <strong>pasar el dato explícitamente</strong> — allá el dato, acá la clase.</p></li>
</ul>
<p>Y la lección general es la que ellos ven en su clase 6: <strong>una anotación de tipo es información para la herramienta, no un objeto que exista cuando el programa corre.</strong> Si alguna vez escribís un genérico y necesitás usar el tipo <em>de verdad</em> —para construir una consulta, para instanciar algo, para comparar— <strong>vas a tener que pasarlo como dato</strong>.</p></td>
</tr>
</tbody>
</table>

6.4.4 — El catálogo de métodos, donde cada uno esconde una decisión

| **Método**                               | **Qué hace**                  | **La decisión que esconde**                                                    |
|------------------------------------------|-------------------------------|--------------------------------------------------------------------------------|
| get_by_id(id, cargar)                    | Obtiene por clave primaria    | El parámetro cargar **es la precarga de EA-05**                                |
| get_by_id_including_deleted(id)          | Sin filtrar el borrado        | Es **la vía de las excepciones de lectura** de la clase 4                      |
| get_for_update(id)                       | Como el anterior, con bloqueo | **Sin filtrar** el borrado: hay que **distinguir borrado de sin stock**        |
| get_many_for_update(ids)                 | Bloquea varias filas          | **Ordena los identificadores** antes de emitir — ver abajo                     |
| list(filters, skip, limit, sort, cargar) | Listado completo              | Lleva **la paginación y el orden** de la clase 2                               |
| count(filters)                           | Cantidad                      | **Los mismos filtros que list**: es el total que respeta filtros de la clase 2 |
| create / update                          | Agrega a la sesión            | Ejecutan **flush() y refresh(), no commit()**                                  |
| soft_delete / hard_delete                | Baja lógica o física          | El físico **sólo** en tablas pivote, galería y purgas                          |
| descendientes / ancestros                | Subárbol de categorías        | Consultas recursivas del motor                                                 |
| tomar_pendientes(limite)                 | Toma eventos del outbox       | Usa un mecanismo que la clase 8 estudia                                        |

**Dos filas merecen desarrollo inmediato.**

**create y update hacen flush(), no commit().** La distinción es central: flush() **emite el SQL** —de modo que la base ya conoce el cambio y **asigna identificadores**— pero **no confirma la transacción**. **El repositorio escribe; el repositorio no decide que la operación terminó.** Esa decisión es del Unit of Work, y por eso **el commit no aparece en ningún repositorio**.

**get_many_for_update ordena los identificadores** de forma ascendente antes de emitir la sentencia. Eso, que parece un detalle de implementación, **es la regla RN-18**: la que evita los interbloqueos. La clase 7 explica por qué; por ahora alcanza con notar que **la regla vive dentro del método**.

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p><strong>PARA ENTENDER: dónde vive una regla decide si se cumple</strong></p>
<p>Ese ordenamiento escondido adentro del método es <strong>una de las mejores decisiones de diseño del TPI</strong>, y todavía no sabés por qué. <strong>Fijate igual en la forma:</strong></p>
<p><strong>La regla no está escrita en ningún lado que alguien tenga que leer. Está adentro del único método que puede violarla.</strong></p>
<p>La alternativa habría sido una nota en la documentación: <em>«acordate de bloquear las filas en orden ascendente de identificador»</em>. Y esa nota <strong>funciona hasta que alguien escribe el bloqueo a mano, apurado, sin haberla leído</strong>.</p>
<p>Poniéndolo adentro de get_many_for_update, <strong>quien usa el método cumple la regla sin saber que existe</strong>. Y quien no lo usa —quien escribe el bloqueo a mano— <strong>es exactamente el caso que hay que revisar en el código</strong>.</p>
<p>Es el mismo patrón que venís viendo desde el primer capítulo de los dos módulos: <strong>la regla que se cumple sola le gana a la regla que hay que recordar.</strong></p></td>
</tr>
</tbody>
</table>

6.5 — La tabla de precarga es parte del contrato

La sección 8.3 del TPI incluye una tabla que indica, **endpoint por endpoint**, qué relaciones hay que precargar. Y la introduce con una frase que conviene citar entera:

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p><strong>Lo que declara el TPI</strong></p>
<p><strong>Esta tabla no es documentación de apoyo: es parte del contrato del endpoint.</strong> Omitir una precarga produce <strong>una excepción en tiempo de ejecución</strong> (EA-05), <strong>no un N+1 silencioso.</strong></p></td>
</tr>
</tbody>
</table>

| **Endpoint**               | **Precarga**                                                            | **Qué revela la decisión**                                                                                                          |
|----------------------------|-------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------|
| GET /productos             | Sólo la unidad de venta                                                 | **No trae categorías ni galería**: no se devuelven en el listado, y la portada viaja en **la columna desnormalizada de la clase 4** |
| GET /productos/{id}        | Unidad, categorías, ingredientes con su unidad, imágenes                | El detalle **sí las devuelve**, así que sí se precargan                                                                             |
| GET /pedidos               | Sólo el usuario                                                         | El listado **no muestra las líneas**                                                                                                |
| GET /pedidos/{id}          | Usuario, ítems con producto e ingredientes, historial con usuario, pago | El detalle completo                                                                                                                 |
| **Confirmación de pedido** | **Por cada producto, su receta con ingrediente y unidad**               | Sin esto, el descuento **emite una consulta por línea, en el punto más caliente del sistema**                                       |

La primera y la segunda fila muestran algo importante: **la precarga no es del modelo, es del endpoint.** El mismo Producto **se trae distinto según qué se vaya a devolver**, y por eso **la tabla se organiza por endpoint y no por entidad**.

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p><strong>OJO ACÁ: la tentación es enorme y hay que resistirla</strong></p>
<p><strong>«Precargo todo siempre y me olvido del problema.»</strong></p>
<p><strong>No funciona</strong>, y el listado de productos lo muestra: si GET /productos precargara categorías y galería como hace el detalle, cada página de veinte productos traería <strong>veinte categorías y ochenta imágenes que nadie va a mostrar</strong>.</p>
<p>Y eso es <strong>peor de lo que parece</strong>, porque ese endpoint es <strong>el más consultado del sistema y el que se cachea</strong>. Estarías <strong>multiplicando por cinco el peso de la respuesta más pedida para no tener que pensar</strong>.</p>
<p><strong>La regla es al revés: precargá exactamente lo que la respuesta va a leer.</strong> Ni más ni menos. Y el que te dice cuánto es exactamente <strong>es el modelo de salida del Capítulo 2</strong>: si un campo no está en el Public, <strong>no hace falta precargarlo</strong>.</p></td>
</tr>
</tbody>
</table>

La última fila conecta con la clase 7: el descuento de stock por receta recorre las líneas del pedido y, por cada una, sus ingredientes. **Sin precarga son tantas consultas como líneas, dentro de una transacción con filas bloqueadas.** Es **el peor lugar posible** para emitir consultas de más.

6.6 — El Unit of Work

El Unit of Work **compone repositorios** —es la actividad 6 de POO— **y gestiona la transacción**:

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p>class UnitOfWork:</p>
<p>def __init__(self, session: AsyncSession):</p>
<p>self.session = session</p>
<p>self.usuarios = UsuarioRepository(session, Usuario)</p>
<p>self.pedidos = PedidoRepository(session, Pedido)</p>
<p># ... un repositorio por entidad, todos con LA MISMA sesión</p>
<p>async def __aenter__(self) -&gt; "UnitOfWork":</p>
<p>return self</p>
<p>async def __aexit__(self, exc_type, exc, tb) -&gt; None:</p>
<p>if exc_type:</p>
<p>await self.session.rollback()</p>
<p>else:</p>
<p>await self.session.commit()</p>
<p># NO cierra la sesión: no la creó</p></td>
</tr>
</tbody>
</table>

**Tres cosas de ese código.**

- **Todos los repositorios comparten la sesión.** Eso **no es un detalle de eficiencia**: es lo que hace que **todo lo que escriban esté en la misma transacción**. Si cada repositorio tuviera su propia sesión, **el Unit of Work no garantizaría nada**.

- **Es un gestor de contexto asincrónico**, y el async with **marca el límite de la transacción de manera visible**. No hay que acordarse de confirmar: **salir del bloque confirma**.

- **Y no cierra la sesión.** El TPI lo declara con esas palabras: *«\_\_aexit\_\_ hace commit o rollback y nada más. El cierre lo hace get_session()»*.

Con eso, **el registro de usuario de la clase anterior** se escribe así:

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p>async def registrar(uow: UnitOfWork, datos: RegistroRequest) -&gt; Usuario:</p>
<p>async with uow:</p>
<p>usuario = await uow.usuarios.create(Usuario(...))</p>
<p>await uow.roles.create(UsuarioRol(usuario_id=usuario.id, rol_id=ROL_CLIENT))</p>
<p>return usuario</p>
<p># salir del bloque confirma las DOS escrituras, o ninguna</p></td>
</tr>
</tbody>
</table>

<img src="media/b58a247e73e015ec92a037827dde687cbe64497e.png" style="width:5.79167in;height:3.5in" />

**Figura 6.2** *— La operación a medias, antes y después. Y la respuesta HTTP, que en los dos casos se ve igual.*

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p><strong>Qué hace el async with, que es el principio que atraviesa los dos módulos</strong></p>
<p><strong>La transacción tiene un límite visible en el código, y confirmarla no depende de que alguien se acuerde.</strong></p>
<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p># Confiando en la memoria</p>
<p>usuario = await crear_usuario(...)</p>
<p>await asignar_rol(...)</p>
<p>await session.commit() # ¿y si alguien lo olvida? ¿y si hay un return antes?</p>
<p># Con el límite declarado</p>
<p>async with uow:</p>
<p>usuario = await uow.usuarios.create(...)</p>
<p>await uow.roles.create(...)</p>
<p># salir confirma. Salir con excepción revierte. No hay tercera opción.</p></td>
</tr>
</tbody>
</table>
<p>Es exactamente la misma idea que tus compañeros del turno de frontend ven con la clase base que da de baja las suscripciones: <strong>el mecanismo hace lo correcto, y equivocarse exige salirse del camino.</strong></p></td>
</tr>
</tbody>
</table>

6.7 — Quién crea, quién abre, quién confirma y quién cierra

Son **cuatro responsabilidades distintas**, y en este sistema **están en cuatro lugares**. Conviene verlas juntas porque **es lo que más se confunde**.

<img src="media/a1013f87e9d74a022555db522856bb88a6fa3bf4.png" style="width:5.79167in;height:4.375in" />

**Figura 6.3** *— El ciclo completo, de la dependencia a la respuesta.*

La regla que ordena todo eso es la tercera decisión de la sección 6.2: **quien crea un recurso lo cierra.** El Unit of Work **no creó la sesión, así que no la cierra**. Si la cerrara, **la dependencia que sí la creó intentaría cerrarla de nuevo**.

La firma uniforme del servicio

El TPI declara además una convención que **parece cosmética y no lo es**: toda función de servicio es una corrutina que recibe **el UoW primero y el actor segundo** —async def crear_pedido(uow, actor, body, clave)—. El actor es un objeto con el identificador del usuario y sus roles vigentes, **o el actor sintético SISTEMA cuando la llamada viene de una tarea**.

**La última parte cierra el círculo con la clase 5.** Ahí se estableció que SISTEMA es **un dato y no una identidad**; acá se ve **dónde vive ese dato**: es un valor que se le pasa al servicio cuando quien llama no es una persona. Y por eso **el servicio funciona igual llamado desde un Router o desde una tarea del worker**: recibe lo mismo, **no averigua nada por su cuenta**.

Una prohibición explícita, y la razón enseña

El TPI declara además **un caso donde NO poner una verificación de rol**: la ruta de avance de estado de un pedido. Ponerla **contradiría la matriz** —el propietario puede cancelar desde pendiente— **e invertiría el orden de errores**.

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p><strong>OJO ACÁ: el orden de los errores cambia qué entiende el usuario</strong></p>
<p>Con una verificación de rol en la ruta, <strong>un cliente que intenta cancelar su propio pedido recibiría un 403 antes de que nadie evalúe si la transición es válida</strong>. El mensaje diría <strong>«no tenés permiso» cuando en realidad sí lo tiene</strong>, por ser el propietario.</p>
<p><strong>El orden correcto es al revés:</strong> primero se resuelve <strong>quién es y qué relación tiene con el recurso</strong>, y <strong>después</strong> la matriz decide si esa transición está permitida para ese actor.</p>
<p>Poner el filtro antes <strong>cambia qué error ve el usuario</strong> — y <strong>un error equivocado es peor que ninguno</strong>: manda a la persona a resolver un problema que no tiene.</p></td>
</tr>
</tbody>
</table>

6.8 — Las dos excepciones declaradas

Acá está **lo más instructivo de la sección 8.4**. El TPI enumera **dos operaciones que se salen del ciclo de vida general**, y **las declara con su razón y su alcance** en lugar de dejarlas como rarezas del código.

6.8.1 — El intento de acceso que debe sobrevivir al rollback

<img src="media/f5e50bb79a362a3d6fe5188bbc8eb9f44e8bbcef.png" style="width:5.79167in;height:3.9375in" />

**Figura 6.4** *— Por qué el registro del intento necesita su propia transacción.*

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p><strong>PARA ENTENDER: lo que importa es el método, no el caso</strong></p>
<p><strong>El TPI declara la excepción, su razón, y lo que complica.</strong> No dice «usá una sesión aparte acá». <strong>Dice por qué</strong>, y <strong>dice qué precio se paga</strong> — estado externo que hay que limpiar en los tests.</p>
<p><strong>Eso es lo que separa una excepción legítima de un parche: un parche no explica por qué es necesario ni qué rompe.</strong></p>
<p>Cuando en tu TPI tengas que salirte de una regla, <strong>escribí las tres cosas</strong>. Y si no podés escribir la segunda —la razón—, <strong>probablemente no era una excepción</strong>.</p></td>
</tr>
</tbody>
</table>

6.8.2 — Las cuatro sesiones del panel

La segunda excepción es **de lectura** y su justificación es **de otro tipo**: el resumen de indicadores lanza sus **cuatro consultas concurrentemente sobre cuatro sesiones del pool**. Es **la única lectura del sistema que usa más de una conexión por petición**, y es aceptable **porque el panel lo consulta un puñado de administradores**.

Acá **no hay una imposibilidad lógica: hay un intercambio medido.** Cuatro consultas independientes en paralelo responden mucho más rápido que en serie —es exactamente lo que la clase 3 mostró con los grupos de tareas— y el costo es **cuatro conexiones del pool en lugar de una**. Lo que vuelve aceptable ese costo es **quién usa el endpoint**: unos pocos administradores, no todos los clientes. **Si el catálogo público hiciera lo mismo, el pool se agotaría con la carga normal.**

|                             | **El intento de acceso**               | **El panel de indicadores**   |
|-----------------------------|----------------------------------------|-------------------------------|
| **Tipo de razón**           | **Lógica**: es imposible de otra forma | **Medida**: es un intercambio |
| **Qué pasa si no se hace**  | El sistema **no funciona**             | El panel es más lento         |
| **Qué la vuelve aceptable** | No hay alternativa                     | **Quién y cuántos lo usan**   |

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p><strong>Comparar las dos excepciones enseña más que cada una por separado</strong></p>
<p><strong>Las dos son válidas y no se justifican igual.</strong> La primera se defiende <strong>con un razonamiento</strong>; la segunda, <strong>con un dato sobre el uso real</strong>.</p>
<p>Cuando propongas una excepción a una regla de tu proyecto, <strong>fijate de cuál de los dos tipos es</strong>. Si es del segundo, <strong>necesitás el dato</strong>: quién lo usa, cuántas veces, qué cuesta.</p>
<p><strong>«Es más rápido» no alcanza</strong> — más rápido siempre es más rápido; <strong>la pregunta es a cambio de qué y para cuántos</strong>.</p></td>
</tr>
</tbody>
</table>

6.9 — Sólo agregado: dos mecanismos independientes

La regla **RN-03** establece algo que **ninguna capa puede violar**: HistorialEstadoPedido y MovimientoStock son de **sólo agregado**. Y la garantía la imponen **dos mecanismos independientes**: **un disparador de la base** y **los permisos del rol de aplicación**.

**Lo interesante es que sean dos, y que sean independientes.** El disparador vive en la base y **rechaza la operación venga de donde venga**. Los permisos —los dos roles de base de datos de la clase 4— hacen que el usuario con el que la aplicación se conecta **directamente no tenga permiso** de modificar ni borrar esas tablas.

**Cualquiera de los dos alcanzaría.** Tener los dos significa que **el fallo de uno no deja el sistema desprotegido**: si alguien reemplaza el disparador en una migración mal revisada, **los permisos siguen**; si alguien despliega con el rol equivocado, **el disparador sigue**.

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p><strong>PARA ENTENDER: defensa en profundidad, y por qué no es paranoia</strong></p>
<p><strong>Dos mecanismos independientes para la misma garantía.</strong> No es desconfianza: es reconocer que <strong>cada mecanismo tiene su propia forma de fallar</strong>, y que <strong>si las dos formas son distintas, es muy improbable que fallen juntas</strong>.</p>
<ul>
<li><p>El disparador falla <strong>si alguien lo elimina en una migración mal revisada</strong>.</p></li>
<li><p>Los permisos fallan <strong>si alguien despliega con el rol equivocado</strong>.</p></li>
</ul>
<p><strong>Son dos errores humanos completamente distintos</strong>, cometidos por personas distintas en momentos distintos. Que ocurran los dos a la vez <strong>es mucho menos probable que cualquiera de ellos por separado</strong>.</p>
<p>Y fijate lo más importante, que ya viste en la clase 4 con las redundancias: <strong>ninguno de los dos está en el código de la aplicación.</strong> Podés escribir un repositorio que intente actualizar el historial <strong>y la operación va a fallar igual</strong>. <strong>La regla no depende de que tu código se porte bien.</strong></p></td>
</tr>
</tbody>
</table>

6.10 — Herramientas de diagnóstico

**El registro de sentencias** vuelve a ser la herramienta central, y en este capítulo sirve para algo específico: **ver dónde empieza y dónde termina cada transacción**.

| **La verificación**                                                  | **Qué comprueba**                                                                                                                                                                       |
|----------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Buscar confirmaciones en los repositorios**                        | Es **una comprobación de texto**: buscar la palabra en esa capa **no debería devolver nada**. Es del mismo tipo que la de EA-03 en la clase 3 — **y por lo tanto se puede automatizar** |
| **Contar las conexiones en uso durante una petición**                | Una petición autenticada debería tomar **una** conexión, **no dos**. Si toma dos, **la unificación de la sesión no está funcionando**                                                   |
| **Provocar un fallo en medio de una operación de varias escrituras** | Y verificar que **ninguna quedó**. Es **la verificación más simple del capítulo y la que más tranquilidad da**                                                                          |

<img src="media/901cad4424a6b3252e3f127bc79f7e62e740b764.png" style="width:5.79167in;height:4.26042in" />

**Figura 6.6** *— El registro de una transacción completa, con sus límites, y el mismo caso con un fallo.*

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p><strong>EXPERIMENTO — el que hace visible por qué existe todo este capítulo</strong></p>
<ul>
<li><p><strong>Uno.</strong> Escribí el registro de usuario <strong>sin</strong> Unit of Work: crear el usuario, confirmar, asignar el rol, confirmar.</p></li>
<li><p><strong>Dos.</strong> Provocá un fallo <strong>entre las dos confirmaciones</strong> — lanzá una excepción a mano.</p></li>
<li><p><strong>Tres.</strong> Mirá la base. <strong>El usuario está. El rol no.</strong></p></li>
<li><p><strong>Cuatro.</strong> Intentá iniciar sesión con ese usuario. <strong>Funciona.</strong> Ahora intentá comprar algo. <strong>No podés, y el error no dice nada útil.</strong> Ese usuario va a estar ahí para siempre, y <strong>nadie lo va a notar hasta que esa persona escriba preguntando por qué no puede hacer un pedido</strong>.</p></li>
<li><p><strong>Cinco.</strong> Ahora envolvé las dos escrituras en async with uow: y repetí el fallo.</p></li>
<li><p><strong>Seis.</strong> Mirá la base. <strong>No hay nada.</strong></p></li>
</ul>
<p><strong>Fijate el detalle que importa: en los dos casos la petición respondió con un error.</strong> Desde afuera se ven iguales. La diferencia está en <strong>lo que quedó adentro</strong>, y es exactamente la diferencia entre <strong>un fallo limpio y un dato corrupto que nadie sabe que existe</strong>.</p></td>
</tr>
</tbody>
</table>

6.11 — Seguridad y evolución

| **La consideración**                                            | **Por qué importa**                                                                                                                                                                                                                                                                                                                                                        |
|-----------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Una transacción abierta demasiado tiempo es un problema**     | Mientras dura, **mantiene bloqueos y ocupa una conexión del pool**. Una operación que abre la transacción y después **hace una llamada a un servicio externo** puede tenerla abierta **segundos** — y con suficiente concurrencia **eso agota el pool**. **El trabajo lento va fuera de la transacción**, y esa es una de las razones de la cola de tareas de la clase 8   |
| **El rollback no revierte lo que ocurrió afuera**               | Si una operación escribió en Redis, envió un correo o llamó a otro servicio, **eso no vuelve atrás**. Es el problema que el patrón de la clase 8 resuelve — y **la razón por la que la excepción de la sección 6.8.1 tiene que declarar el estado externo que introduce**                                                                                                  |
| **Las restricciones de la base son la última línea de defensa** | Un servicio que **verifica y después escribe** deja **una ventana** entre las dos cosas, y en esa ventana otra petición puede haber cambiado el estado. La verificación en el código evita **el noventa y nueve por ciento** de los casos; **la restricción declarada evita el resto** — que es el que ocurre bajo concurrencia. **La clase 7 estudia ese uno por ciento** |

Sobre la evolución, dos observaciones. **La primera:** estos patrones **tienen más de veinte años y siguen siendo la respuesta correcta**. Se los ha declarado innecesarios varias veces —porque el ORM ya hace algo parecido, porque agregan una capa— **y vuelven**, porque lo que resuelven **no desaparece**: alguien tiene que decidir **qué escrituras van juntas**, y ese alguien **no puede ser cada escritura por su cuenta**.

**La segunda:** el nombre importa menos que la responsabilidad. Hay marcos donde el equivalente del Unit of Work es un decorador, o un gestor de contexto de la propia biblioteca. **Lo que no cambia es la pregunta: ¿dónde empieza y dónde termina esta transacción, y quién lo decide?**

6.12 — Verificación: el checklist honesto

1.  Escribir una operación de dos escrituras **sin** Unit of Work, provocar un fallo en el medio, y **documentar qué quedó en la base**. *(6.6)*

2.  Repetir **con** Unit of Work y verificar que **no quedó nada**. *(6.6)*

3.  Ubicar en el registro de sentencias **dónde empieza y dónde termina** una transacción. *(6.10)*

4.  Verificar que **ningún repositorio confirma**: buscar la palabra en esa capa. *(6.10)*

5.  Explicar la diferencia entre **emitir el SQL y confirmar**, y por qué el repositorio hace lo primero y no lo segundo. *(6.4.4)*

6.  Contar las conexiones que toma una petición autenticada y **verificar que es una**. *(6.7)*

7.  Escribir un repositorio genérico y **explicar por qué recibe la clase del modelo**. *(6.4.3)*

8.  Justificar **por qué hay dos jerarquías de repositorio y no una**. *(6.4.2)*

9.  Explicar por qué el registro del intento de acceso **no puede** estar en la transacción de su petición. *(6.8.1)*

6.13 — Los once errores frecuentes

| **El error**                                             | **Por qué duele**                                                                                           | **Sección** |
|----------------------------------------------------------|-------------------------------------------------------------------------------------------------------------|-------------|
| **Confirmar dentro del repositorio**                     | El repositorio escribe; **quien decide que la operación terminó es el Unit of Work**                        | 6.4.4       |
| **Abrir una transacción por escritura**                  | **Cada pieza queda correcta y el conjunto inconsistente**: es el problema que el capítulo entero resuelve   | 6.2         |
| **Que el Unit of Work cierre la sesión**                 | **No la creó.** Quien la creó la cierra — y si la cierra el UoW, la dependencia intentará cerrarla de nuevo | 6.7         |
| **Construir el Unit of Work dentro del Service**         | El Service **lo recibe y lo abre; nunca lo construye**. Es la regla de la sección 2.1 del TPI               | 6.7         |
| **Darle a cada repositorio su propia sesión**            | Entonces **el Unit of Work no garantiza nada**: cada uno escribe en su propia transacción                   | 6.6         |
| **No unificar la sesión entre dependencias**             | Cada petición autenticada consume **dos conexiones del pool en lugar de una**                               | 6.7         |
| **Olvidar la precarga declarada**                        | **No es un N+1 silencioso: es una excepción en tiempo de ejecución**                                        | 6.5         |
| **Precargar por entidad en lugar de por endpoint**       | **El mismo modelo se trae distinto** según qué se vaya a devolver                                           | 6.5         |
| **Poner una verificación de rol donde la matriz decide** | **Invierte el orden de errores**: el usuario recibe «no tenés permiso» cuando sí lo tiene                   | 6.7         |
| **Hacer trabajo lento con la transacción abierta**       | Mantiene bloqueos y ocupa una conexión; **con concurrencia agota el pool**                                  | 6.11        |
| **Suponer que el rollback revierte lo que pasó afuera**  | Lo escrito en Redis o enviado por correo **no vuelve**                                                      | 6.11        |

6.14 — Las actividades, y qué busca cada una

1\. El problema, medido

Implementar el registro de usuario **de las dos formas** y documentar el estado de la base tras un fallo en cada caso. **Explicar por qué las dos respuestas HTTP son indistinguibles desde afuera.**

***Qué busca:** la última parte. Que el error se vea igual es exactamente lo que hace que este bug sobreviva meses.*

2\. El repositorio genérico

Implementar BaseRepository\[T\] y SoftDeleteRepository\[T\] con al menos **seis** de los métodos que el TPI declara. Justificar por qué son dos clases **y verificar el error que produciría una sola**.

***Qué busca:** que veas el error de SQL con tus ojos. La justificación deja de ser una opinión cuando la base te la confirma.*

3\. La precarga por endpoint

Tomar **tres filas** de la tabla de precarga e implementarlas. Para cada una, ejecutar el endpoint **sin** la precarga y documentar la excepción; después **contar las consultas** con la precarga puesta.

***Qué busca:** las dos mitades. La excepción muestra que la tabla es un contrato; el conteo muestra qué se ganó.*

4\. Los cuatro roles del ciclo de vida

Implementar la cadena completa —dependencia de sesión, dependencia de UoW, Router, Service— y agregar registros que muestren **el orden exacto** en que ocurre cada paso, **incluido el cierre después de la respuesta**.

***Qué busca:** ver el cierre ocurrir después de que la respuesta salió. Es lo que hace que la dependencia con yield deje de parecer magia.*

5\. La excepción del intento fallido

Implementar el registro del intento **dentro** de la transacción de la petición y **demostrar que no queda ninguno**. Corregirlo con una sesión propia y verificar que ahora sí. **Documentar además el estado externo que eso introduce.**

***Qué busca:** la última frase. Declarar el costo es la mitad de la excepción — sin eso es un parche.*

6\. Exploración: los límites de la transacción

Con el registro de sentencias activado, capturar el ciclo completo de **tres operaciones distintas** —una lectura, una escritura simple y una de varias escrituras— y documentar **dónde empieza y termina la transacción en cada caso**. Relacionarlo con la tabla de responsabilidades de la sección 6.7.

***Qué busca:** que descubras que hasta una lectura abre transacción. Casi nadie lo espera.*

7\. Exploración: los tipos que se borran, en dos lenguajes

Junto con alguien del turno de frontend, comparar **el borrado de genéricos de Python con el borrado de tipos de TypeScript**. Escribir en cada lenguaje un caso donde el tipo genérico **haga falta en ejecución**, documentar cómo lo resuelve cada uno, y **explicar por qué los dos llegan a la misma solución**.

***Qué busca:** que la coincidencia no parezca casualidad. Los dos lenguajes borran los tipos por la misma razón, y por eso la salida es la misma.*

6.15 — Síntesis: las doce frases

1.  El problema no es que las operaciones fallen sino que **fallen por la mitad**. Un fallo limpio es un no-evento; **un dato a medias es un estado que ninguna parte del código contempla**.

2.  La transacción resuelve el *qué* y deja abierto el *dónde*. **Quien sabe qué escrituras van juntas es el servicio**, no cada escritura por su cuenta.

3.  El repositorio separa **«qué datos necesito» de «cómo se los pido»**, y por eso la precarga se declara ahí: **es el único que sabe cómo se traen**.

4.  Hay **dos jerarquías de repositorio** porque sólo cinco entidades tienen borrado lógico: **un filtro universal fallaría sobre las otras dieciocho**.

5.  **Los genéricos de Python se borran en tiempo de ejecución**, igual que los tipos de TypeScript. Por eso el repositorio **recibe la clase del modelo como dato**: T no existe cuando el programa corre.

6.  create y update **emiten el SQL pero no confirman**. El repositorio escribe; **quien decide que la operación terminó es el Unit of Work**.

7.  La tabla de precarga **es parte del contrato del endpoint**, no documentación de apoyo. Y se organiza **por endpoint y no por entidad**, porque el mismo modelo se trae distinto según qué se devuelva.

8.  **Cuatro responsabilidades, cuatro lugares:** la dependencia crea y cierra la sesión, otra construye el Unit of Work sin abrirlo, el Router lo transporta, **y el Service lo abre y lo confirma**.

9.  **Quien crea un recurso lo cierra.** Por eso el Unit of Work **no cierra la sesión**.

10. Una verificación de rol puesta donde la matriz decide **invierte el orden de errores**: el usuario recibe «no tenés permiso» cuando en realidad lo tiene.

11. La excepción del intento de acceso es **lógicamente necesaria**: **lo que se quiere registrar es exactamente lo que destruye el registro.** Y el TPI declara además **qué complica** — que es lo que separa una excepción de un parche.

12. RN-03 se garantiza con **dos mecanismos independientes, y ninguno está en el código de la aplicación**. La regla se cumple **aunque alguien escriba código que intente violarla**.

6.16 — Qué leer, y en qué orden

Si leés una sola cosa

**Kleppmann**, *Designing Data-Intensive Applications* (O'Reilly, 2017), **capítulo 7** — dedicado a las transacciones, y **la mejor explicación disponible de por qué el aislamiento es difícil**. Su tratamiento de los fenómenos de concurrencia **es la preparación ideal para la clase siguiente**.

Si leés tres

- **Fowler**, *Patterns of Enterprise Application Architecture* (2002): las entradas sobre **Repository** y **Unit of Work** son **breves y conviene leerlas completas**, porque enuncian las responsabilidades **con más precisión de la que suele circular**.

- La documentación de **SQLAlchemy** sobre **la sesión y su ciclo de vida**: es la referencia directa de las secciones 6.6 y 6.7, y **su discusión sobre cuándo emitir y cuándo confirmar cubre exactamente la distinción de la sección 6.4.4**.

- **Evans**, *Domain-Driven Design* (2003): explica **por qué el repositorio devuelve objetos del dominio y no filas** — que es la distinción que vuelve al servicio **independiente del motor**.

Las fuentes fundacionales

- **Härder y Reuter**, *Principles of Transaction-Oriented Database Recovery* (ACM Computing Surveys, 1983): **acuñó el acrónimo** sobre el trabajo previo de Jim Gray. Su lectura muestra que **las cuatro letras no son igual de fundamentales** y que **el aislamiento es la que más grados admite**.

- La documentación de **PostgreSQL** sobre **control de concurrencia**: detalla los niveles de aislamiento que la sección 6.3 apenas menciona **y que la clase 7 va a necesitar enteros**.

Del TPI

Este capítulo se apoya en la **8.3** —con su catálogo de métodos y su tabla de precarga— y en la **8.4**, que declara el ciclo de vida completo y las dos excepciones. Toca además la **16.4** por los dos mecanismos que garantizan RN-03, y **anticipa la 9.2**, donde el bloqueo que aparece en get_many_for_update **encuentra su explicación**.

Cierre: las seis cosas que hay que recordar

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p><strong>LAS SEIS</strong></p>
<p><strong>1.</strong> <strong>El problema no es fallar: es fallar por la mitad.</strong> Un 500 limpio no le hace daño a nadie; un usuario sin rol vive en la base para siempre.</p>
<p><strong>2.</strong> <strong>La transacción es de la operación de negocio.</strong> Quien sabe qué va junto es el Service — por eso el commit no aparece en ningún repositorio.</p>
<p><strong>3.</strong> <strong>Emitir no es confirmar.</strong> flush() manda el SQL y consigue el identificador; commit() decide que la operación terminó.</p>
<p><strong>4.</strong> <strong>Cuatro responsabilidades, cuatro lugares.</strong> Y la regla que las ordena: <strong>quien crea un recurso lo cierra</strong>.</p>
<p><strong>5.</strong> <strong>La regla que vive adentro del método le gana a la que hay que recordar.</strong> get_many_for_update ordena los identificadores solo, y quien lo usa cumple RN-18 sin enterarse.</p>
<p><strong>6.</strong> <strong>Una excepción se declara con tres cosas: qué es, por qué es necesaria, y qué complica.</strong> Si no podés escribir la segunda, no era una excepción: era un parche.</p></td>
</tr>
</tbody>
</table>

Y una séptima, que es el hilo que conecta este capítulo con los cuatro anteriores: **ninguna garantía importante de este sistema depende de que alguien se acuerde.** El async with confirma solo, el índice parcial impide el duplicado, el disparador rechaza la escritura, el tipo hace que select(T) ni siquiera compile. **Cuando algo depende de la memoria de quien escribe, todavía no está resuelto.**
