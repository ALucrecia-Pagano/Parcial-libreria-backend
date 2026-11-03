**CAPÍTULO 4 — GUÍA DE LECTURA**

**Persistencia**

SQLModel, PostgreSQL y el modelo de datos, en criollo

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
<p>Los tres capítulos anteriores construyeron un servicio que responde, valida y no bloquea. <strong>Le falta lo único que importa a largo plazo: recordar.</strong></p>
<p>Y con la persistencia aparece la primera decisión verdaderamente difícil del módulo — que <strong>no es técnica sino de traducción</strong>. Las actividades 5 y 6 de POO les dieron un vocabulario preciso: asociación, agregación, composición. <strong>Una base relacional no tiene ninguna de esas tres cosas:</strong> tiene tablas, filas y claves foráneas.</p>
<p>Equivocarse ahí cuesta más caro que en cualquier otra parte del sistema, y la razón es una sola:</p>
<p><strong>Los datos sobreviven al código.</strong></p>
<p>Un endpoint mal escrito se corrige con un despliegue. Un esquema mal pensado se arrastra durante años, y cada corrección tiene que llevarse consigo lo que ya está guardado.</p></td>
</tr>
</tbody>
</table>

4.1 — De qué se trata esta clase

Qué dice

El capítulo introduce el almacenamiento durable y **cobra dos deudas de la clase anterior**. **EA-04** —la sesión que no expira sus objetos al confirmar— y **EA-05** —la carga perezosa prohibida— dejan de ser advertencias sobre una excepción con nombre raro y pasan a ser **dos líneas de código concretas, con su motivo a la vista**.

Y hay una sección que el capítulo trata con especial cuidado **porque contradice lo que se enseña habitualmente**. Todo curso de bases de datos enseña a **normalizar**: que un dato viva en un solo lugar. El TPI declara **cinco redundancias deliberadas** y las justifica una por una. Entender por qué a veces copiar un dato es lo correcto —y qué hay que hacer para que esa copia no se convierta en una mentira— **es lo que separa aplicar una regla de tomar una decisión**.

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p><strong>El criterio con el que el TPI resuelve eso vale como enunciado de todo el capítulo</strong></p>
<p><strong>«Ninguna redundancia queda sostenida sólo por la disciplina del Service.»</strong></p>
<p>Dicho al revés: <strong>si tu única defensa es que alguien se acuerde de actualizar las dos copias, no tenés defensa.</strong></p></td>
</tr>
</tbody>
</table>

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p><strong>PARA EL PIZARRÓN</strong></p>
<p>Al terminar la clase tenés que poder hacer tres cosas:</p>
<ul>
<li><p><strong>Traducir un diagrama de clases a un esquema relacional</strong>, justificando cada decisión.</p></li>
<li><p><strong>Escribir los modelos con su carga anticipada declarada.</strong></p></li>
<li><p><strong>Generar y leer una migración antes de aplicarla.</strong></p></li>
</ul>
<p>La tercera es la que más gente saltea, y es la única cuyo error <strong>no se puede deshacer</strong>.</p></td>
</tr>
</tbody>
</table>

4.2 — Por qué relacional, y qué esconde un ORM

Qué dice

El modelo relacional es de **1970** y nació de un artículo de Edgar Codd que proponía algo entonces radical: **separar cómo se guardan los datos de cómo se consultan**. Los sistemas de la época obligaban al programa a conocer la estructura física del almacenamiento —punteros, orden de los registros— y por lo tanto **cualquier cambio en esa estructura rompía todos los programas**.

La propuesta de Codd fue describir los datos como **relaciones** —conjuntos de tuplas— y consultarlos con un lenguaje **declarativo** donde uno dice **qué quiere, no cómo obtenerlo**. El motor decide el cómo. Esa separación es la razón por la que un esquema puede reorganizarse, agregar índices o cambiar su almacenamiento **sin que las consultas cambien**.

Sobre eso se construyeron **dos garantías** que el resto del módulo da por sentadas: las **restricciones declaradas** —una clave foránea, una unicidad, una comprobación— que el motor impone **sin que ningún programa colabore**, y las **transacciones**, que la clase 6 estudia.

El desajuste: por qué los dos mundos no encajan

Cuando los lenguajes orientados a objetos se volvieron dominantes, apareció un problema conocido como **desajuste de impedancia objeto-relacional**. Conviene enunciarlo con precisión porque explica todo lo que sigue.

<img src="media/e7a96299ffe2550538c388dda5c7d02d4618d7b8.png" style="width:5.79167in;height:3.30208in" />

**Figura 4.2** *— Las cinco diferencias del desajuste, y la que más cuesta.*

Los mapeadores, y la advertencia que sostiene el capítulo entero

Un ORM traduce entre los dos modelos. Hibernate lo popularizó en Java a partir de 2001, y SQLAlchemy hizo lo propio en Python desde 2006. **La promesa es escribir objetos y que alguien más se ocupe del SQL.**

Y acá va la advertencia: **un ORM no elimina el desajuste, lo esconde.** Todo lo de esa tabla sigue ahí abajo. Quien no lo sabe **escribe código que parece correcto** y emite ciento una consultas donde debía emitir dos, o que modifica un objeto y no entiende por qué eso disparó cinco sentencias.

| **Las cuatro decisiones de diseño del capítulo**                   | **Qué significa**                                                                                                                          |
|--------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------|
| **1. El almacén durable es uno solo**                              | PostgreSQL es el único almacén durable; **Redis es efímero**. Ningún dato de negocio vive sólo en Redis                                    |
| **2. Las garantías se declaran en la base cuando se puede**        | **Una restricción que el motor impone no depende de que ningún programa se acuerde.** Es el mismo principio que atraviesa todo el material |
| **3. Lo que la base no puede garantizar, lo garantiza una prueba** | Es la frase del TPI sobre las redundancias. **No hay una tercera opción llamada «tener cuidado»**                                          |
| **4. El esquema es código versionado**                             | Las migraciones viven en el repositorio, **se revisan** y se aplican en orden                                                              |

4.3 — De las actividades 5 y 6 al esquema

Acá se cobra lo que ya saben. Las tres relaciones que estudiaron en POO tienen traducción al esquema, y **la diferencia entre ellas no está en la clave foránea sino en qué pasa al borrar**.

<img src="media/e273df5ba7f9239e61afa903f458f2629d8d5386.png" style="width:5.79167in;height:5.01042in" />

**Figura 4.1** *— Las tres relaciones de POO traducidas al esquema, y qué las diferencia.*

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p>class Pedido(SQLModel, table=True):</p>
<p>id: int | None = Field(default=None, primary_key=True)</p>
<p>usuario_id: int = Field(foreign_key="usuario.id") # la FK vive acá</p></td>
</tr>
</tbody>
</table>

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p><strong>El detalle que confunde a todo el que viene de objetos</strong></p>
<p><strong>La clave foránea va del lado «muchos», que es el contrario al que uno esperaría.</strong></p>
<p>En tu cabeza —y en el diagrama de clases— el usuario <em>tiene</em> una lista de pedidos. Parece que la relación viviera en el usuario. <strong>En la base es al revés: cada pedido guarda a quién pertenece.</strong> La tabla de usuarios no sabe nada de pedidos.</p>
<p><strong>¿Y por qué?</strong> Porque una columna guarda <strong>un</strong> valor, no una lista. Para que el usuario «tuviera» sus pedidos habría que guardar una cantidad variable de referencias en una fila, y <strong>eso el modelo relacional no lo hace</strong>.</p>
<p>El ORM después te deja escribir usuario.pedidos y parece que la lista estuviera ahí. <strong>No está: es una consulta</strong> que va a buscar los pedidos cuyo usuario_id coincide. Y por eso hay que declararla — otra vez EA-05.</p></td>
</tr>
</tbody>
</table>

4.4 — SQLModel: qué une, y qué no conviene unir

El Capítulo 2 declaró modelos con Pydantic para validar peticiones. Este capítulo necesita modelos que **representen tablas**. **SQLModel** —publicado en 2021 por el mismo autor del marco de trabajo— une las dos cosas: un modelo de SQLModel **es** un modelo de Pydantic **y** una tabla de SQLAlchemy. El parámetro table=True es el que hace la diferencia.

Y acá conviene una advertencia que evita un error frecuente: **que se puedan unir no significa que convenga usar el mismo modelo para todo.** El modelo de tabla y los schemas de entrada y salida **siguen siendo cosas distintas**, por las tres razones de la sección 2.5. Lo que SQLModel evita es **reescribir los campos comunes**, no la segregación.

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p>class ProductoBase(SQLModel): # sin table=True: sólo campos</p>
<p>nombre: str = Field(max_length=120)</p>
<p>precio: Decimal = Field(max_digits=10, decimal_places=2)</p>
<p>class Producto(ProductoBase, table=True): # LA TABLA</p>
<p>id: int | None = Field(default=None, primary_key=True)</p>
<p>costo_interno: Decimal # sólo en la tabla</p>
<p>deleted_at: datetime | None = Field(default=None)</p>
<p>class ProductoCreate(ProductoBase): # entrada</p>
<p>categoria_id: int</p>
<p>class ProductoPublic(ProductoBase): # salida</p>
<p>id: int</p></td>
</tr>
</tbody>
</table>

**Fijate qué campo está en cuál.** costo_interno vive **sólo en la tabla**: no entra por ProductoCreate y no sale por ProductoPublic. deleted_at tampoco sale. Y id no está en la entrada, **porque lo asigna la base**.

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p><strong>OJO ACÁ: la herencia ahorra tipeo y trae una trampa</strong></p>
<p><strong>Si agregás un campo a ProductoBase, aparece en los tres lugares a la vez.</strong></p>
<p>Hoy agregás costo_proveedor a la base porque lo necesitás en la tabla. Y sin darte cuenta acabás de hacer <strong>dos cosas más</strong>: <strong>el cliente ahora lo puede mandar</strong> —está en Create— y <strong>el cliente ahora lo puede ver</strong> —está en Public—.</p>
<p><strong>No hay error, no hay advertencia.</strong> El campo simplemente empieza a viajar en las dos direcciones.</p>
<p><strong>La regla: a la base van sólo los campos que van en los tres.</strong> Todo lo demás se declara en el modelo que corresponde. Si dudás, ponelo en la tabla y agregalo después donde haga falta — <strong>el error de que falte se ve enseguida; el de que sobre, no</strong>.</p></td>
</tr>
</tbody>
</table>

4.5 — El motor y la sesión

Acá se cobran dos reglas de la clase anterior, y **las dos son una línea de código**.

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p># EA-08: se crean en el ciclo de vida, ni por petición ni a nivel de módulo</p>
<p>engine = create_async_engine(</p>
<p>settings.DATABASE_URL, # postgresql+psycopg://...</p>
<p>pool_size=settings.DB_POOL_SIZE,</p>
<p>pool_timeout=settings.DB_POOL_TIMEOUT,</p>
<p>)</p>
<p># EA-04: expire_on_commit=False, y no es una optimización</p>
<p>async_session = async_sessionmaker(engine, expire_on_commit=False,</p>
<p>class_=AsyncSession)</p></td>
</tr>
</tbody>
</table>

Un detalle del TPI que conviene notar: **la dirección de la base declara el dialecto asincrónico** —postgresql+psycopg://— y a partir de ahí el motor elige solo la variante correcta. **Es EA-03 expresada en configuración.**

Sobre pool_size y pool_timeout, la sección 3.11 ya explicó por qué son **variables declaradas y no valores por defecto**: con corrutinas, el techo natural que ponía el grupo de hilos desapareció, y **el pool es el primer recurso que se agota**.

Y sobre expire_on_commit=False, vale la pena ver **el caso concreto que evita**:

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p>pedido = await uow.pedidos.crear(datos)</p>
<p>await uow.commit()</p>
<p>return PedidoResponse(id=pedido.id, total=pedido.total) # ← acá explotaría</p></td>
</tr>
</tbody>
</table>

Con el valor por defecto, **el commit marca el objeto como expirado**. Esa lectura de pedido.id intentaría ir a buscar el dato de nuevo, **desde una línea común sin await**, y ahí **no hay a dónde saltar**: es exactamente la situación de la sección 3.8. Con False, el objeto conserva sus valores y **la lectura es un acceso a memoria**.

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p><strong>Y por qué el valor por defecto es True, que no es un capricho</strong></p>
<p><strong>En un mundo sincrónico tiene todo el sentido.</strong> Después de un commit, otra transacción pudo haber cambiado esos datos. Expirar el objeto garantiza que la próxima lectura traiga <strong>lo que hay en la base ahora</strong>, y no lo que había antes. Es una decisión conservadora y correcta.</p>
<p><strong>Lo que cambia en asincrónico no es la conveniencia: es la posibilidad.</strong> Esa relectura implícita necesita emitir una consulta, y como ocurre en una línea común sin await, <strong>no tiene desde dónde hacerlo</strong>.</p>
<p>O sea: el valor por defecto <strong>no es un error de la biblioteca</strong>. Es una opción pensada para otro modelo de ejecución, <strong>que en este directamente no funciona</strong>.</p>
<p>Y de ahí sale un criterio general que te va a servir: <strong>cuando una biblioteca soporta dos modelos de ejecución, sus valores por defecto suelen estar pensados para el más viejo. Revisalos.</strong></p></td>
</tr>
</tbody>
</table>

4.6 — Relaciones y carga anticipada

Las relaciones se declaran **en los dos extremos**:

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p>class Pedido(SQLModel, table=True):</p>
<p>usuario_id: int = Field(foreign_key="usuario.id")</p>
<p>usuario: "Usuario" = Relationship(back_populates="pedidos")</p>
<p>detalles: list["DetallePedido"] = Relationship(back_populates="pedido")</p>
<p>class Usuario(SQLModel, table=True):</p>
<p>pedidos: list["Pedido"] = Relationship(back_populates="usuario")</p></td>
</tr>
</tbody>
</table>

back_populates le dice al ORM que esos dos atributos son **los dos lados de la misma relación**, de modo que agregar un pedido a la lista del usuario también completa el usuario del pedido. **Sin eso, los dos lados pueden quedar inconsistentes en memoria.**

Ahora bien: **declarar la relación no la carga.** Y acá aparece EA-05 en código.

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p># El repositorio DECLARA qué relaciones va a necesitar la respuesta</p>
<p>async def obtener_con_detalles(self, pedido_id: int) -&gt; Pedido | None:</p>
<p>consulta = (</p>
<p>select(Pedido)</p>
<p>.where(Pedido.id == pedido_id)</p>
<p>.options(</p>
<p>selectinload(Pedido.detalles),</p>
<p>selectinload(Pedido.usuario),</p>
<p>)</p>
<p>)</p>
<p>return (await self.session.exec(consulta)).first()</p></td>
</tr>
</tbody>
</table>

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p><strong>PARA ENTENDER: dónde vive esa declaración es una decisión de arquitectura</strong></p>
<p><strong>La precarga se declara en el repositorio, no en el Service ni en la vista.</strong></p>
<p>Y tiene lógica: <strong>el repositorio es el único que sabe cómo se traen los datos.</strong> El Service dice <em>qué</em> necesita —«dame el pedido con sus líneas»— y el repositorio decide <strong>cómo lo trae</strong>.</p>
<p>Eso tiene una consecuencia práctica que vale oro: <strong>cuando te explota una excepción de greenlet, ya sabés dónde mirar.</strong> No es en la vista, no es en el Service: <strong>es en el método del repositorio que trajo ese objeto, y le falta una línea.</strong></p>
<p>Es el mismo principio de las capas de la clase 1: <strong>cada cosa en el lugar donde se sabe lo que hace falta saber.</strong> Si la precarga se declarara en el Service, el Service tendría que conocer detalles del acceso a datos — y ahí se rompe el flujo Router → Service → UoW → Repository → Model.</p></td>
</tr>
</tbody>
</table>

<img src="media/90bbb80f01708ca7778d57d59e732ed4694f47c9.png" style="width:5.79167in;height:3.80208in" />

**Figura 4.3** *— Carga perezosa y anticipada: las consultas que emite cada una, y las dos estrategias.*

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p><strong>OJO ACÁ: dale vuelta la lectura antes de escribir tu primer repositorio</strong></p>
<p>Al principio esto se siente como un castigo: estás escribiendo un endpoint y <strong>te explota una excepción con un nombre que no dice nada</strong>.</p>
<p><strong>El sincrónico no te avisa nunca.</strong> Te deja mandar a producción un endpoint que emite ciento una consultas, y te enterás <strong>dentro de seis meses</strong>, cuando ya hay diez mil pedidos y nadie se acuerda de quién escribió eso.</p>
<p>Acá el problema aparece <strong>en tu máquina, con tres registros de prueba, el día que lo escribís.</strong> Es <strong>el mejor momento posible</strong> para enterarse.</p></td>
</tr>
</tbody>
</table>

4.7 — Los tres dominios

El TPI organiza sus **veintitrés entidades** en tres dominios, y esa división **no es sólo de presentación: agrupa cosas que cambian juntas**.

| **Dominio**               | **De qué trata**                 | **Entidades características**                        |
|---------------------------|----------------------------------|------------------------------------------------------|
| **Identidad y acceso**    | Quién es quién y qué puede hacer | Usuario, UsuarioRol, DireccionEntrega, IntentoAcceso |
| **Catálogo y stock**      | Qué se vende y cuánto hay        | Categoria, Producto, Ingrediente, MovimientoStock    |
| **Ventas y trazabilidad** | Qué se vendió y qué pasó con eso | Pedido, DetallePedido, Pago, HistorialEstadoPedido   |

A eso se suman las **cinco tablas catálogo** —roles, estados de pedido, formas de pago, modalidades de entrega y unidades—, que merecen un comentario **porque su existencia es una decisión**.

Un estado de pedido **podría ser** una columna de texto, o una enumeración del lenguaje. El TPI lo modela como **una tabla**, y eso permite algo que las otras dos opciones no: **que el estado tenga atributos propios**. EstadoPedido tiene una columna es_terminal, y **RN-01 dice que un estado terminal no admite transiciones salientes**. Con una enumeración del lenguaje, esa propiedad tendría que vivir en el código.

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p><strong>El costo y el beneficio de modelar los catálogos como tablas</strong></p>
<p><strong>El costo:</strong> cada lectura de un pedido necesita también su estado, así que hay <strong>una relación más que precargar</strong>. Y agregar un estado nuevo exige <strong>una migración</strong>, no un cambio de código.</p>
<p><strong>El beneficio:</strong> el estado <strong>tiene atributos propios</strong>. Con una enumeración del lenguaje, saber si un estado es terminal sería <strong>un if en algún lado</strong> — y ese if <strong>habría que repetirlo</strong> en cada lugar que lo necesite.</p>
<p>El criterio para decidir es <strong>una sola pregunta: ¿esto va a necesitar atributos además del nombre?</strong> Si la respuesta es sí —o si no estás seguro— va como tabla. Si es un conjunto cerrado que sólo necesita distinguirse a sí mismo, una enumeración alcanza.</p>
<p>Y ojo: los cinco catálogos <strong>también aparecen como enumeración en el frontend</strong>, porque del otro lado son valores cerrados de una unión literal. <strong>Los dos lados modelan lo mismo con la herramienta de su mundo.</strong></p></td>
</tr>
</tbody>
</table>

4.8 — Normalización, y las cinco redundancias declaradas

Todo curso de bases de datos enseña a normalizar: **que cada dato viva en un solo lugar**, de modo que no pueda haber dos versiones contradictorias. Es una regla excelente **y este sistema la rompe cinco veces, a propósito**.

<img src="media/8551134c42f7703ebbc8b0f697a6b2af00d405e8.png" style="width:5.79167in;height:4.36458in" />

**Figura 4.4** *— Las cinco redundancias declaradas y qué sostiene a cada una.*

Las filas 4 y 5 muestran **el criterio en acción**. El monto del pago duplica el total del pedido, y esa igualdad **no se puede expresar como una comprobación de la base porque cruza dos tablas**: su garante es una prueba, y el TPI lo dice así. En la portada del producto, la parte que **sí** es expresable —que exista una sola portada por producto— **la impone un índice único**; la parte que cruza tablas —que la dirección copiada coincida con la original— **la sostiene una prueba**.

Fijate lo que eso significa: **el TPI no elige entre restricción y prueba por comodidad**. Usa la restricción **siempre que sea expresable**, y recurre a la prueba **sólo donde la base no llega**. Nunca deja el hueco.

4.9 — Borrado lógico: una enumeración taxativa

El **borrado lógico** consiste en no borrar: **marcar la fila con una fecha de eliminación y filtrarla en las consultas**. Se usa cuando el dato tiene valor histórico o cuando otras filas lo referencian.

Y acá el TPI hace algo que conviene destacar antes que nada, **porque es una lección de honestidad técnica**: «La enumeración de esta sección **es taxativa**. Enunciar que *todas las consultas filtran deleted_at* **sería falso**.»

**En lugar de una regla cómoda y mentirosa, el documento enumera.** Cinco entidades tienen borrado lógico —usuario, dirección de entrega, categoría, producto e ingrediente—; **dieciocho no lo tienen**, y **seis admiten borrado físico**, cada una con su razón:

| **Entidad**                                    | **Por qué se puede borrar de verdad**              |
|------------------------------------------------|----------------------------------------------------|
| ProductoCategoria, ProductoIngrediente         | **Ningún pedido las referencia**                   |
| ProductoImagen                                 | La galería es del producto; **nada más la apunta** |
| IntentoAcceso, ClaveIdempotencia, EventoSalida | Tienen **purgas de retención declaradas**          |

Y una frase que resume la política: **«Las entidades de negocio no se borran nunca, y UsuarioRol tampoco: su baja es una revocación lógica.»**

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p><strong>PARA ENTENDER: la distinción que vale para cualquier sistema que hagas</strong></p>
<p><strong>Hay datos que describen cómo son las cosas, y datos que registran qué pasó.</strong></p>
<p>Un producto <strong>describe</strong>: su precio es el de hoy, y si mañana cambia, el de hoy ya no importa. Se puede modificar y —con cuidado— se puede dar de baja.</p>
<p>Un pedido <strong>registra</strong>: es el hecho de que alguien compró algo un martes a las ocho. <strong>Ese hecho ocurrió, y no hay ninguna operación futura que pueda hacer que no haya ocurrido.</strong> Modificarlo no es corregir un dato: <strong>es falsificar la historia</strong>.</p>
<p>Por eso el TPI no borra pedidos ni movimientos de stock, y por eso RN-03 dice que el historial es de <strong>sólo agregado</strong>. <strong>Cancelar un pedido no lo borra: agrega un registro que dice que se canceló.</strong></p>
<p>Cuando modeles algo, la pregunta es esa: <strong>¿esto describe o registra?</strong> Lo que registra no se toca. Y si tenés que «corregir» un registro, <strong>lo correcto casi siempre es agregar otro que lo compense</strong>, no editar el que está.</p></td>
</tr>
</tbody>
</table>

Las cinco excepciones de lectura, y por qué tres son de corrección

El TPI enumera además **cinco casos donde una consulta no filtra las filas borradas** —también taxativos—. Tres merecen comentario porque cada una enseña algo distinto:

| **La excepción**              | **Por qué no filtra**                                                                                                                                                                                                                                                                                          |
|-------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **La lectura histórica**      | Al abrir un pedido viejo, la resolución del producto de cada línea no filtra: **un producto retirado del catálogo sigue siendo legible desde un pedido anterior**. Es la contracara de la primera redundancia — el snapshot conserva el nombre y el precio, y esta excepción permite además llegar al producto |
| **La confirmación de pedido** | La revalidación de stock consulta sin filtrar porque **necesita distinguir «eliminado» de «sin stock»** para devolver el error correcto. Filtrar haría que un producto borrado se reportara como faltante, y **el usuario recibiría un mensaje equivocado**                                                    |
| **El árbol de categorías**    | La más sutil. El cálculo de profundidad recorre los ancestros sin filtrar porque —en palabras del TPI— *«si filtrara, una rama con un ancestro eliminado parecería más corta de lo que es y admitiría un nivel de más»*. **No es una excepción por comodidad: filtrar produciría un resultado incorrecto**     |

Y un detalle final que conviene conocer: **ninguna entidad con borrado lógico tiene endpoint de restauración.** Revertir un borrado accidental **es una operación de base de datos**, hecha a mano por quien tenga acceso.

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p><strong>OJO ACÁ: un índice único común rompe el borrado lógico</strong></p>
<p>Esta trampa se descubre siempre tarde. Pensala:</p>
<p>Tenés UNIQUE(email) en usuarios. Alguien se da de baja —su fila queda con deleted_at cargado— y después <strong>quiere volver a registrarse con el mismo correo</strong>. <strong>La base lo rechaza</strong>, porque para el índice único <strong>esa fila sigue estando</strong>.</p>
<p>Y el mensaje que te llega es <em>«el email ya existe»</em>, <strong>cuando en la aplicación ese usuario no existe</strong>. Vas a buscarlo, no aparece en ningún listado, y no entendés nada.</p>
<p>La solución es un <strong>índice único parcial</strong>, que PostgreSQL sí soporta:</p>
<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p>CREATE UNIQUE INDEX ux_usuario_email_activo</p>
<p>ON usuario (email) WHERE deleted_at IS NULL;</p></td>
</tr>
</tbody>
</table>
<p>Así la unicidad aplica <strong>sólo entre los vivos</strong>. Por eso el TPI declara que usa índices únicos parciales, y por eso ese detalle está en el stack: <strong>no es un lujo, es lo que hace que el borrado lógico funcione.</strong></p></td>
</tr>
</tbody>
</table>

4.10 — Índices y restricciones

Un **índice** es una estructura auxiliar que permite encontrar filas **sin recorrer la tabla entera**. El TPI declara **treinta y uno, cada uno con su motivo**, y esa enumeración explícita es coherente con el resto del documento: **un índice sin motivo declarado es un costo sin beneficio conocido**, porque cada índice **hace más lentas las escrituras**.

| **El criterio**                                        | **Por qué**                                                                                                                                                                                                                                                     |
|--------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Las claves foráneas se indexan**                     | Sin índice, buscar los pedidos de un usuario **recorre la tabla de pedidos completa**. Y ojo: **PostgreSQL no crea ese índice automáticamente**, a diferencia de otros motores                                                                                  |
| **Lo que se filtra u ordena seguido se indexa**        | Si el listado de productos ordena por fecha de creación, esa columna necesita índice                                                                                                                                                                            |
| **La unicidad de negocio se declara como restricción** | Que un correo no se repita **no es algo que el Service deba verificar: es algo que la base debe impedir**. Verificar en el Service **deja una ventana** entre la comprobación y la inserción — y en esa ventana **otra petición puede insertar el mismo valor** |

Y las **comprobaciones** —los CHECK— son el otro mecanismo declarativo, el que la sección 4.8 usa como garante de **tres de las cinco redundancias**. Una comprobación de que el total es igual al subtotal menos el descuento más el envío **se cumple siempre, venga la escritura de donde venga**: desde un endpoint, desde una tarea del worker, o desde alguien escribiendo SQL a mano.

**Su límite es el que el TPI señala: no puede cruzar tablas.** De ahí que la cuarta redundancia —el monto del pago— tenga como garante una prueba y no un CHECK.

4.11 — Migraciones: el esquema como código versionado

El esquema de la base cambia con el tiempo, y ese cambio necesita **las mismas garantías que el código**: quedar registrado, revisarse, aplicarse en orden y **poder reproducirse en otra máquina**.

**Alembic** resuelve eso con migraciones versionadas: cada cambio es un archivo con su función de aplicación y su función de reversión, y **cada uno declara a cuál sigue**. El TPI exige inicializarlo con la plantilla asincrónica, coherente con EA-03.

Alembic puede **generar** una migración comparando los modelos con el esquema actual. Y acá va la advertencia que el TPI convierte en **práctica obligatoria**: **una migración generada se lee antes de aplicarse. Siempre.**

<img src="media/a93f26cebacd3adaa97a5a94b8efd8656a528161.png" style="width:5.79167in;height:4.22917in" />

**Figura 4.6** *— Una migración generada, con lo que hay que revisar señalado.*

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p><strong>EXPERIMENTO — mejor comerse el susto acá que en producción</strong></p>
<ul>
<li><p><strong>Uno.</strong> Creá un modelo con un campo nombre y generá la migración. Aplicala.</p></li>
<li><p><strong>Dos.</strong> Insertá <strong>tres filas con datos</strong>.</p></li>
<li><p><strong>Tres.</strong> Ahora <strong>renombrá</strong> el campo a nombre_completo en el modelo y generá la migración de nuevo.</p></li>
<li><p><strong>Cuatro. Abrí el archivo generado y leelo antes de aplicar nada.</strong></p></li>
</ul>
<p>Vas a ver drop_column('nombre') seguido de add_column('nombre_completo'). <strong>Eso no es un renombre: es borrar los datos y crear una columna vacía.</strong> Si lo aplicás, tus tres filas <strong>pierden el nombre para siempre</strong>.</p>
<ul>
<li><p><strong>Cinco.</strong> Corregí la migración a mano por alter_column con new_column_name, aplicala, y <strong>verificá que los datos siguen</strong>.</p></li>
</ul>
<p><strong>La herramienta no se equivocó:</strong> comparó dos esquemas y <strong>no puede adivinar tu intención</strong>. Vos sabés que renombraste; ella ve una columna que ya no está y otra que apareció.</p></td>
</tr>
</tbody>
</table>

4.12 — Herramientas de diagnóstico

| **Herramienta**                            | **Qué te dice**                                                                                                                                            | **Cuándo**                                                                                                                                         |
|--------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------|
| **El registro de sentencias del motor**    | **Cada consulta que el ORM emite** — y por lo tanto responde la pregunta que un ORM vuelve difícil: **qué SQL produjo realmente el código que escribiste** | Es **la herramienta central de este capítulo**. Para verificar que una consulta con precarga emite **dos sentencias y no ciento una**              |
| **El plan de ejecución** (EXPLAIN ANALYZE) | Cómo resolvió el motor una consulta: **si usó un índice o recorrió la tabla entera**, y cuánto tardó cada paso                                             | Cuando una consulta es lenta — **antes de agregar índices a ciegas**                                                                               |
| **El estado del pool**                     | Cuántas conexiones están en uso                                                                                                                            | Si está lleno de forma sostenida, **el problema es el de la sección 3.11** y no una consulta lenta                                                 |
| **Un cliente de base de datos**            | El esquema tal como quedó                                                                                                                                  | Para verificar que **una migración hizo lo que se esperaba**: que el índice existe, que la comprobación está declarada, que el tipo es el correcto |

<img src="media/5b669fd4b26ed37f77000b1d75bd5942bced5736.png" style="width:5.79167in;height:3.96875in" />

**Figura 4.5** *— El esquema de un dominio visto desde un cliente, y qué verificar después de una migración.*

4.13 — Seguridad y evolución

| **La consideración**                                 | **Por qué importa**                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
|------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Los dos roles de base de datos**                   | El sistema usa **dos**: un **propietario**, que es el único que aplica migraciones y puede alterar el esquema, y un **rol de aplicación**, que sólo puede leer y escribir datos. La consecuencia es concreta: **aunque el código de la aplicación sea comprometido, no puede alterar el esquema ni borrar tablas**. Y es además uno de los dos mecanismos que garantizan las tablas de sólo agregado de RN-03 — **el rol de aplicación no tiene permiso** de actualizar ni borrar sobre ellas |
| **Los datos personales tienen requisitos propios**   | Un correo, una dirección y un teléfono son datos personales, y **el borrado lógico los conserva**. Es una decisión legítima —hay razones de trazabilidad— y **conviene saber que existe una tensión** con las normativas de protección de datos, que en general reconocen un derecho a la supresión                                                                                                                                                                                           |
| **El esquema es una superficie de ataque indirecta** | Un mensaje de error que revela **nombres de tablas y columnas** le entrega a un atacante **el mapa del sistema**. Es otra razón del manejador global de errores que la clase 8 estudia                                                                                                                                                                                                                                                                                                        |

Sobre la evolución, dos observaciones. **La primera:** el modelo relacional **lleva más de cincuenta años** y las alternativas que iban a reemplazarlo **terminaron conviviendo con él**. La razón es la de la sección 4.2: **las garantías declaradas —las restricciones y las transacciones— son difíciles de reponer en la aplicación, y casi siempre se reponen peor**.

**La segunda:** PostgreSQL viene incorporando capacidades que antes obligaban a sumar otro motor —documentos JSON con índices, búsqueda de texto, tipos geométricos—. Eso hace más defendible la decisión del TPI de tener **un solo almacén durable**, que es **siempre más simple de operar que dos**.

4.14 — Verificación: el checklist honesto

1.  Traducir un diagrama con las tres relaciones de POO a un esquema, **justificando dónde va cada clave foránea** y qué comportamiento de borrado corresponde. *(4.3)*

2.  Declarar una relación uno a uno y **verificar que sin la restricción de unicidad no lo es**. *(4.3)*

3.  Provocar la excepción de la sección 3.8 **olvidando la precarga**, y corregirla. *(4.6)*

4.  Contar con el registro de sentencias las consultas que emite un listado de veinte elementos, **con y sin precarga**. *(4.12)*

5.  Comparar selectinload y joinedload en una colección, y **contar las filas transferidas** por cada uno. *(4.6)*

6.  Quitar expire_on_commit=False y **reproducir el error** que EA-04 previene. *(4.5)*

7.  Identificar en el TPI las cinco redundancias y **nombrar el garante de cada una**. *(4.8)*

8.  Crear un usuario, darlo de baja lógicamente, e intentar registrar el mismo correo. **Corregirlo con un índice único parcial.** *(4.9)*

9.  Generar la migración de un renombre y **encontrar el problema antes de aplicarla**. *(4.11)*

4.15 — Los doce errores frecuentes

| **El error**                                                          | **Por qué duele**                                                                              | **Sección** |
|-----------------------------------------------------------------------|------------------------------------------------------------------------------------------------|-------------|
| **Poner la clave foránea del lado equivocado**                        | En uno a muchos vive **en el lado «muchos»**, al revés de lo que sugiere el diagrama de clases | 4.3         |
| **Declarar uno a uno sin restricción de unicidad**                    | Sin ella **es uno a muchos con un solo elemento por casualidad**                               | 4.3         |
| **Usar el modelo de tabla como schema de entrada y de salida**        | Son cosas distintas por las tres razones de la clase 2 — y expone campos que no deben salir    | 4.4         |
| **Olvidar expire_on_commit=False**                                    | El objeto queda expirado tras el commit y **la primera lectura falla**. Viola EA-04            | 4.5         |
| **Declarar la relación y no precargarla**                             | **Declarar no es cargar:** acceder lanza la excepción de greenlet. Viola EA-05                 | 4.6         |
| **Usar joinedload para una colección grande**                         | Devuelve **los datos del padre repetidos una vez por hijo**                                    | 4.6         |
| **Desnormalizar sin garante**                                         | Una redundancia sin restricción ni prueba es **una inconsistencia esperando ocurrir**          | 4.8         |
| **Suponer que todas las consultas filtran el borrado lógico**         | El TPI enumera **cinco excepciones taxativas**, y tres son **de corrección y no de comodidad** | 4.9         |
| **Declarar un índice único común sobre una tabla con borrado lógico** | Impide reusar un valor de una fila dada de baja. **Corresponde un índice parcial**             | 4.9         |
| **Verificar la unicidad en el Service**                               | Deja **una ventana** entre la comprobación y la inserción                                      | 4.10        |
| **Olvidar el índice de una clave foránea**                            | **PostgreSQL no lo crea solo**                                                                 | 4.10        |
| **Aplicar una migración generada sin leerla**                         | La comparación automática **ve un renombre como borrar y crear** — y eso pierde los datos      | 4.11        |

4.16 — Las actividades, y qué busca cada una

1\. Del diagrama al esquema

Tomar el dominio de catálogo del TPI —producto, categoría, ingrediente y sus vínculos— y escribir sus **modelos completos** con relaciones, comportamiento de borrado e índices. **Justificar cada decisión contra las actividades 5 y 6 de POO.**

***Qué busca:** que la traducción sea explícita. La mitad de las decisiones no las resuelve el diagrama: las resolvés vos.*

2\. Las consultas contadas

Implementar un endpoint que liste pedidos con su usuario y sus líneas. Medir con el registro de sentencias cuántas emite **sin precarga, con selectinload y con joinedload**, y documentar además **las filas transferidas** en cada caso.

***Qué busca:** la segunda métrica. Contar consultas es lo obvio; contar filas es lo que explica por qué joinedload no sirve para colecciones.*

3\. Las cinco redundancias

Para cada una, documentar **qué duplica, qué la garantiza, y qué pasaría si esa garantía no existiera**. Proponer para la cuarta —el monto del pago— **una forma de detectar la inconsistencia si la prueba no existiera**.

***Qué busca:** la última parte. Cuando no hay garante, lo único que queda es una consulta de auditoría que alguien tiene que acordarse de correr. Ese es exactamente el problema.*

4\. El índice parcial

Implementar borrado lógico sobre usuarios con unicidad de correo. **Demostrar el problema con un índice único común** y resolverlo con uno parcial. Verificar los dos casos: registrar un correo dado de baja, **y no poder duplicar uno activo**.

***Qué busca:** que verifiques los dos lados. Un índice parcial mal escrito arregla el primer caso y rompe el segundo.*

5\. Migraciones que se leen

Generar tres migraciones —**agregar columna, renombrar columna y cambiar un tipo con conversión**— y documentar para cada una **qué generó la herramienta, qué hacía falta corregir y por qué**.

***Qué busca:** que veas que la primera está perfecta y las otras dos no. La herramienta no es mala: tiene un límite conocido.*

6\. Exploración: qué esconde el ORM

Escribir cinco operaciones habituales —insertar, actualizar, borrar, listar con filtro y navegar una relación— y **capturar el SQL que cada una emite**. Documentar **los casos donde el SQL sorprendió**, y relacionarlo con la afirmación de la sección 4.2.

***Qué busca:** las sorpresas. Casi siempre aparecen en el update y en la navegación, que son justamente las dos que el ORM disimula mejor.*

7\. Exploración: el plan de ejecución

Sobre una tabla con **varios miles de filas** de prueba, ejecutar una consulta filtrada por una columna **sin índice** y capturar su plan. Agregar el índice, repetir, y comparar. Documentar **qué cambió en el plan y cuánto en el tiempo**, y explicar por qué el TPI declara el motivo de cada uno de sus treinta y un índices.

***Qué busca:** que veas el cambio de «recorrido secuencial» a «búsqueda por índice» con tus ojos, y que el número te dé la escala real.*

4.17 — Síntesis: las once frases

1.  El modelo relacional separó **cómo se guardan los datos de cómo se consultan**, y de esa separación salen las garantías que el resto del módulo da por sentadas: **las restricciones declaradas y las transacciones**.

2.  **Un ORM no elimina el desajuste objeto-relacional: lo esconde.** La diferencia más costosa es que en objetos navegar es gratis y contra una base **cada navegación es una consulta**.

3.  La clave foránea vive **del lado «muchos»**, al revés de lo que sugiere el diagrama de clases, **porque una columna guarda un valor y no una lista**.

4.  **La diferencia entre agregación y composición no está en la clave foránea sino en qué pasa al borrar** — y en este sistema esa cascada casi nunca se ejecuta, porque las entidades de negocio no se borran.

5.  expire_on_commit=False **no es una optimización**: sin él, la primera lectura después del commit **intenta emitir entrada y salida donde no puede**.

6.  **Declarar una relación no la carga.** La precarga se declara **por consulta y en el repositorio**, y la tabla del TPI es **una condición para que el endpoint funcione**, no una guía de rendimiento.

7.  Normalizar es la regla, y el TPI la rompe **cinco veces con criterio declarado**. Lo que separa una redundancia de un descuido es que **ninguna queda sostenida sólo por la disciplina del Service**.

8.  El **snapshot de línea** no es una optimización sino **una necesidad del dominio**: sin él, cambiar un precio **reescribiría la historia**.

9.  El TPI **enumera en vez de generalizar**, y lo dice: afirmar que «todas las consultas filtran el borrado lógico» **sería falso**. Tres de sus cinco excepciones **son de corrección, no de comodidad**.

10. **Un índice único común rompe el borrado lógico.** El índice parcial es lo que hace que las dos cosas convivan.

11. **Una migración generada se lee antes de aplicarse:** la comparación automática ve un renombre como borrar y crear, **y eso pierde los datos**.

4.18 — Qué leer, y en qué orden

Si leés una sola cosa

**Winand**, *SQL Performance Explained* (2012, con contenido libre en use-the-index-luke.com) — **la mejor introducción a los índices que existe**, y explica los planes de ejecución de la sección 4.12 **desde el problema y no desde la herramienta**.

Si leés tres

- La documentación de **PostgreSQL** en postgresql.org/docs: es **de las mejores de su categoría**, y sus capítulos sobre índices, restricciones y niveles de aislamiento cubren las secciones 4.9 y 4.10 **y anticipan la clase 6**.

- La documentación de **SQLAlchemy** sobre **estrategias de carga de relaciones**: es la fuente directa de la sección 4.6 y explica **cuándo conviene cada estrategia y por qué**.

- **Kleppmann**, *Designing Data-Intensive Applications* (O'Reilly, 2017), **capítulo 2**: la comparación entre modelos de datos, y **por qué el relacional sobrevivió a sus reemplazos anunciados**.

Las fuentes fundacionales y de herramienta

- **E. F. Codd**, *A Relational Model of Data for Large Shared Data Banks* (1970): **de lectura sorprendentemente accesible**, y muestra con claridad **qué problema se estaba resolviendo**.

- **ISO/IEC 9075** norma el lenguaje de consulta, aunque **en la práctica la referencia útil es la del motor**.

- **SQLModel** (sqlmodel.tiangolo.com) para la unión de los dos mundos de la sección 4.4, y **Alembic** para las limitaciones de la comparación automática que la sección 4.11 vuelve práctica obligatoria.

- **Fowler**, *Patterns of Enterprise Application Architecture* (2002): donde quedaron nombrados los patrones de acceso a datos que **la clase 6 va a usar**, y cuyo capítulo sobre mapeo objeto-relacional enuncia el desajuste **con más rigor que la mayoría de los textos posteriores**.

Del TPI

Este capítulo se apoya en **la sección 3 completa** —sus nueve subsecciones, de las que **la 3.7 y la 3.8 son las que más discusión merecen en clase**—, en la **8.3** por su tabla de precarga, y en la **16.1** por las variables de conexión que la sección 4.5 usa.

Cierre: las seis cosas que hay que recordar

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p><strong>LAS SEIS</strong></p>
<p><strong>1.</strong> <strong>Los datos sobreviven al código.</strong> Un endpoint mal escrito se arregla con un despliegue; un esquema mal pensado se arrastra años.</p>
<p><strong>2.</strong> <strong>El ORM esconde el desajuste, no lo elimina.</strong> La misma línea cuesta nanosegundos en memoria y tres viajes de red contra la base.</p>
<p><strong>3.</strong> <strong>La clave foránea va del lado «muchos»</strong>, porque una columna guarda un valor y no una lista.</p>
<p><strong>4.</strong> <strong>Declarar una relación no la carga.</strong> Y la precarga se declara <strong>en el repositorio</strong>, que es el único que sabe cómo se traen los datos.</p>
<p><strong>5.</strong> <strong>Una redundancia sin garante no es una optimización: es una bomba de tiempo.</strong> Restricción si la base puede; prueba si no. Nunca «tener cuidado».</p>
<p><strong>6.</strong> <strong>Una migración generada se lee antes de aplicarse.</strong> Es el único error del sistema que no se deshace con un despliegue.</p></td>
</tr>
</tbody>
</table>

Y una séptima, que es la pregunta con la que conviene modelar cualquier cosa de acá en adelante: **¿esto describe cómo son las cosas, o registra qué pasó?** Lo que describe se edita. **Lo que registra no se toca** — y si hay que corregirlo, se agrega otro registro que lo compense.
