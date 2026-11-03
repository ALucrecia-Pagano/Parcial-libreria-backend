**qCAPÍTULO 3 — GUÍA DE LECTURA**

**El bucle de eventos**

Las ocho reglas de ejecución asincrónica, explicadas en criollo

*Traducción didáctica del texto académico, sección por sección. Mismos conceptos, otro idioma.*

# Antes de empezar: cómo usar esta guía

Cada sección tiene **Qué dice** (la idea comprimida), **En criollo** (la explicación larga con la analogía) y **Para el pizarrón** (la frase que hay que llevarse). **No se pierde ni un concepto**: lo que cambia es el idioma.

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>LA IDEA MADRE DE TODO EL CAPÍTULO</strong></p>
<p>Una sola frase, y de ella se deducen las ocho reglas:</p>
<p><strong>Nadie te interrumpe. Vos cedés.</strong></p>
<p>Con hilos, el sistema operativo te saca del procesador cuando se le da la gana. Podés escribir un bucle infinito y el resto del programa sigue andando, porque <strong>alguien más te va a interrumpir</strong>.</p>
<p>Con corrutinas <strong>no hay nadie que te interrumpa</strong>. Si tu código no llega a un await, el bucle de eventos <strong>no puede hacer absolutamente nada</strong> hasta que termines. <strong>No es que sea lento: no existe el mecanismo.</strong></p>
<p>Por eso la palabra «bloquear» significa algo mucho más grave de este lado. Y por eso hay <strong>ocho reglas</strong> dedicadas a que nunca pase.</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

# 3.1 — Por qué esta es la clase más importante del módulo

### Qué dice

Conviene decirlo con las palabras del propio TPI. Su sección 1.4 se abre así: **«Esta sección es normativa y es la que más consecuencias tiene sobre el código; todo lo demás del documento la presupone.»**

**Ocho de las treinta y siete reglas del backend viven ahí**, identificadas como **EA-01 a EA-08**, y este capítulo las funda todas. Y no están repartidas por el documento: están **juntas, en una sola sección**, porque responden a un mismo hecho.

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>El hecho, que el Capítulo 1 dejó enunciado y no desarrolló</strong></p>
<p><strong>El servidor atiende todas las peticiones sobre un único bucle de eventos, y una sola línea que no ceda el control lo detiene para todos.</strong></p>
<p>No para el usuario que la disparó: <strong>para todos los usuarios conectados, al mismo tiempo.</strong></p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

### En criollo: la coincidencia que hay que aprovechar

**Esta misma semana, la otra mitad de la cursada estudia el bucle de eventos del navegador**: un solo hilo que ejecuta y dibuja, y que al bloquearse deja la página muerta. **Es el mismo modelo mental, en otro lenguaje y del otro lado del cable.** Verlo dos veces el mismo día lo fija de una manera que una sola exposición no consigue — y conviene que los dos docentes usen el mismo dibujo.

El capítulo también estudia el error que el TPI señala como **«el que más tiempo hace perder»**: la excepción que aparece cuando el ORM intenta emitir una consulta desde un lugar donde no puede. Su nombre no dice nada —MissingGreenlet— y **su causa está siempre lejos de donde salta**.

Y hay una sección que rara vez se enseña y que este capítulo incluye porque el TPI la declara: **qué hacía bien el modelo sincrónico que ahora hay que reponer a mano.** El modelo asincrónico no es gratis, y **saber qué se resignó es lo que separa usarlo de padecerlo**.

### Las ocho reglas, todas juntas, para tener a mano

| **Regla** | **Qué exige**                                                                                                                                                                    | **Qué problema previene**                                                                                         |
|-----------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------|
| **EA-01** | Todos los handlers con async def. **Ninguno con def**                                                                                                                            | La mezcla —handler asincrónico con línea bloqueante adentro— **detiene el proceso entero**, no un hilo de un pool |
| **EA-02** | Las tres bloqueantes del sistema —**bcrypt**, lectura de archivos de configuración y cualquier librería sin variante asincrónica— salen a un hilo con anyio.to_thread.run_sync() | Que el bucle se quede haciendo trabajo que no cede                                                                |
| **EA-03** | Toda la I/O con clientes asincrónicos. **El módulo redis síncrono no aparece en ningún import**                                                                                  | La biblioteca sincrónica que sale en todos los ejemplos de internet                                               |
| **EA-04** | async_sessionmaker(expire_on_commit=False)                                                                                                                                       | Que el objeto quede expirado tras el commit y su primera lectura lance MissingGreenlet                            |
| **EA-05** | **Carga perezosa prohibida.** Toda relación que una respuesta lea se precarga con selectinload()                                                                                 | La misma excepción, por la otra causa — y de paso, el N+1                                                         |
| **EA-06** | Ninguna corrutina hace **más de un milisegundo** de trabajo de CPU sin ceder                                                                                                     | Que el cálculo consuma el hilo que todos comparten                                                                |
| **EA-07** | Las tareas en segundo plano **no se lanzan con asyncio.create_task()**: se encolan, o van al outbox                                                                              | Que el trabajo se pierda al reiniciar, falle en silencio y no se reintente                                        |
| **EA-08** | El pool y el cliente de Redis se crean **en el lifespan**. No por petición ni a nivel de módulo                                                                                  | Los errores desconcertantes que aparecen sólo en los tests, o sólo al levantar                                    |

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>PARA EL PIZARRÓN</strong></p>
<p>Al terminar la clase tenés que poder hacer tres cosas:</p>
<ul>
<li><p><strong>Explicar qué hace cada una de las ocho reglas EA y qué problema previene.</strong></p></li>
<li><p><strong>Reconocer una llamada bloqueante en código ajeno.</strong></p></li>
<li><p><strong>Diagnosticar una excepción de greenlet a partir de su traza.</strong></p></li>
</ul></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

# 3.2 — Cómo Python llegó a poder expresar esto

### Qué dice

El Capítulo 1 estableció el problema: un servidor pasa su tiempo esperando, y un hilo por conexión no escala. Falta la otra mitad de la historia — **cómo Python llegó a poder expresar eso**, porque el camino explica la forma que tiene hoy.

| **Etapa**                                                          | **Qué aportó**                                                                                                                                 | **Qué le faltaba**                                                                                                                                                                   |
|--------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Las funciones de retorno** Twisted (2002), Tornado (2009)        | Resolvieron la concurrencia con el mismo mecanismo que el navegador usó durante años: registrar una función que se ejecuta cuando algo termina | El código **se anidaba** y **los errores no se podían capturar desde afuera**. Es exactamente lo que la otra mitad de la cursada estudia con el mismo nombre                         |
| **Los generadores como corrutinas** PEP 342 (2005), PEP 380 (2009) | Python ya tenía desde 2001 algo que **puede suspenderse y reanudarse**. El 342 lo hizo bidireccional; el 380 agregó yield from para delegar    | Se podía escribir código asincrónico que **se leía como secuencial** — pero **la sintaxis mentía**: lo que parecía un generador era una corrutina, y no había forma de distinguirlos |
| **La biblioteca estándar** PEP 3156 (2012), Python 3.4             | Por primera vez hubo **un bucle de eventos estándar**, lo que permitió que bibliotecas de distintos autores funcionaran juntas                 | Seguía faltando sintaxis propia                                                                                                                                                      |
| **La sintaxis propia** PEP 492 (2015), Python 3.5                  | async y await como palabras del lenguaje. **Una corrutina se declara como tal y los puntos donde cede el control se ven a simple vista**       | Faltaba qué hacer cuando varias tareas concurrentes fallan a la vez                                                                                                                  |
| **Los grupos de tareas** PEP 654, Python 3.11 (2022)               | Grupos de tareas y except\* con los grupos de excepciones                                                                                      | **Es la razón por la que el TPI fija Python 3.12 como piso** y no una versión anterior                                                                                               |

### Las cuatro decisiones que salen de ese recorrido

1.  **La concurrencia es cooperativa, no preventiva.** Nadie interrumpe a una corrutina: **ella cede el control cuando quiere**. De ahí se deduce todo lo demás del capítulo, incluida la razón por la que una línea bloqueante es tan grave.

2.  **Los puntos de cesión son visibles.** Cada await es un lugar donde el control puede irse a otra parte. Eso permite **razonar sobre qué puede ocurrir entre dos líneas**, algo que con hilos es imposible.

3.  **Una corrutina no hace nada hasta que se la agenda.** Llamar a una función asincrónica **no la ejecuta**: devuelve un objeto. Es **lo contrario** de lo que ocurre del otro lado del cable, donde una promesa arranca su operación al crearse.

4.  **Las excepciones se propagan por el árbol de tareas.** Con los grupos de tareas, una tarea que falla cancela a sus hermanas y su error llega a quien las lanzó. Sin eso, **una tarea suelta que falla desaparece en silencio** — que es lo que EA-07 previene.

# 3.3 — Concurrencia no es paralelismo

Esta distinción se confunde permanentemente y **sin ella nada de lo que sigue se entiende**.

**Paralelismo** es hacer dos cosas **al mismo tiempo**, lo que exige dos unidades de ejecución: dos núcleos, dos procesos. **Concurrencia** es **avanzar en varias cosas** durante el mismo período, sin que necesariamente ocurran a la vez. Una sola unidad de ejecución que alterna entre tareas **es concurrente y no es paralela**.

<img src="media/image1.png" style="width:5.79167in;height:3.47917in" />

**Figura 3.1** *— Concurrencia frente a paralelismo, y dónde entra el bloqueo global del intérprete.*

El modelo asincrónico de Python es **concurrente y no paralelo**: hay un solo hilo, que va alternando. Y para un servidor web **eso alcanza**, por la razón del Capítulo 1: si el trabajo dominante es esperar, no hace falta ejecutar en paralelo. Hace falta **no quedarse quieto mientras se espera**.

De ahí que el modelo asincrónico **no sea una manera de esquivar el bloqueo global del intérprete**, sino algo mejor: **una manera de no necesitar hilos en absoluto** para lo que un servidor hace la mayor parte del tiempo.

# 3.4 — Anatomía del bucle de eventos

El bucle de eventos es **un ciclo con cuatro pasos**: preguntarle al sistema operativo qué operaciones de entrada y salida están listas, despertar las corrutinas que las esperaban, ejecutar cada una **hasta su próximo punto de cesión**, y volver a empezar.

**Toda la clase está en el tercer paso**, en esas palabras. Si una corrutina no llega a un await, el paso 3 no termina, y el bucle **nunca vuelve al paso 1**. Nadie más es atendido.

<img src="media/image2.png" style="width:5.79167in;height:4.40625in" />

**Figura 3.2** *— Cómo una petición cede el control y vuelve, línea por línea y en el tiempo.*

Esa es la forma correcta. **La incorrecta se ve igual y no lo es:**

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p>@router.get("/pedidos/{pedido_id}")</p>
<p>async def obtener_pedido(pedido_id: int):</p>
<p>pedido = requests.get(f"{URL}/pedidos/{pedido_id}").json() # NO cede</p>
<p>return pedido</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

Esa línea usa **un cliente sincrónico**. No hay await, así que **no hay punto de cesión**: el bucle se queda ahí, esperando la red, sin atender nada. Es **EA-03**, y la sección 3.7 la desarrolla.

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>PARA ENTENDER: cómo leer código asincrónico, mecánicamente</strong></p>
<p><strong>Buscá los await. Esos son los únicos lugares donde tu función puede pausarse.</strong></p>
<p>Entre dos await consecutivos, tu código corre <strong>sin que nadie lo interrumpa</strong>. Nadie más toca nada. Eso tiene dos caras:</p>
<ul>
<li><p><strong>La buena:</strong> no necesitás candados para proteger una variable compartida entre dos líneas sin await. <strong>Con hilos sí los necesitarías</strong>, porque el sistema operativo te puede sacar en cualquier momento.</p></li>
<li><p><strong>La mala:</strong> si entre dos await hay algo que tarda, <strong>nadie más existe</strong> hasta que termine.</p></li>
</ul>
<p>Y de ahí sale el criterio para leer código ajeno: <strong>una función async sin ningún await adentro es sospechosa.</strong> O no hace entrada y salida —y entonces no necesitaba ser async— o la hace de forma bloqueante, <strong>que es el problema de este capítulo entero</strong>.</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

# 3.5 — Corrutinas y tareas

Una función declarada con async def es **una función corrutina**. Llamarla **no la ejecuta**:

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p>resultado = calcular_total(pedido) # NO se ejecutó: es un objeto corrutina</p>
<p>resultado = await calcular_total(pedido) # ahora sí</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

Esa es la tercera decisión de diseño de la sección anterior, y merece atención porque es **lo contrario de lo que ocurre del otro lado del cable**: en el navegador, llamar a una función que devuelve una promesa **dispara la operación de inmediato**. Acá **no pasa nada hasta que alguien la agenda**.

Para ejecutar varias cosas a la vez hacen falta **tareas**, y el TPI exige armarlas con **un grupo**:

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p>async with asyncio.TaskGroup() as tg:</p>
<p>t_productos = tg.create_task(listar_productos())</p>
<p>t_categorias = tg.create_task(listar_categorias())</p>
<p>productos = t_productos.result()</p>
<p>categorias = t_categorias.result()</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

El grupo hace **tres cosas que una tarea suelta no hace**: espera a todas antes de salir del bloque; si una falla, **cancela a las demás**; y **propaga los errores** a quien abrió el grupo, agrupados si fueron varios —para eso existe la sintaxis except\*—.

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>OJO ACÁ: este error no falla con estruendo — falla siendo lento</strong></p>
<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p># Serializa: la segunda no arranca hasta que termina la primera</p>
<p>productos = await listar_productos()</p>
<p>categorias = await listar_categorias()</p>
<p># Concurrente: las dos salen juntas</p>
<p>async with asyncio.TaskGroup() as tg:</p>
<p>tp = tg.create_task(listar_productos())</p>
<p>tc = tg.create_task(listar_categorias())</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>
<p>Si cada consulta tarda 40 ms, la primera versión tarda <strong>80</strong> y la segunda <strong>40</strong>. Con cuatro consultas independientes, <strong>160 contra 40</strong>.</p>
<p>Y acá va lo importante: <strong>el código serializado no está mal escrito.</strong> Es perfectamente correcto, hace lo que dice y <strong>pasa cualquier test</strong>. Simplemente tarda el doble sin necesidad.</p>
<p><strong>La pregunta que te tenés que hacer en cada await es una sola: ¿lo que viene después necesita este resultado?</strong> Si la respuesta es no, esas dos operaciones van juntas.</p>
<p>Fijate el paralelo con lo que ve la otra mitad esta semana: <strong>dos operaciones independientes se lanzan juntas y se esperan juntas.</strong> El tiempo total pasa a ser <strong>el máximo</strong> en lugar de la suma.</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

# 3.6 — Qué significa bloquear, y las tres del sistema

Una operación **bloquea** cuando ocupa el hilo **sin ceder el control**. Hay dos formas de hacerlo, y conviene distinguirlas porque **tienen soluciones distintas**:

- **Entrada y salida sincrónica.** Leer un archivo, consultar la base con un cliente sincrónico, hacer una petición HTTP con una biblioteca sincrónica. **El hilo espera una respuesta externa sin ceder.**

- **Trabajo de procesador.** Un cálculo largo, un cifrado, procesar una imagen. **No hay espera: hay trabajo**, y mientras dure, no hay cesión posible.

El TPI enumera **las tres operaciones bloqueantes del sistema** en EA-02, y **la lista es corta a propósito**: bcrypt, la lectura de archivos de configuración, y cualquier llamada de librería sin variante asincrónica. **La solución para las tres es la misma: sacarlas a un hilo aparte.** El hilo se bloquea; el bucle, no.

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p>from anyio import to_thread</p>
<p>hash_almacenado = await to_thread.run_sync(bcrypt.hashpw, password, salt)</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

Esa línea **sí tiene await**: la corrutina cede mientras el trabajo ocurre en otro lado, y se reanuda cuando termina.

Sobre el trabajo de procesador, **EA-06 pone un umbral concreto** que vale la pena citar porque casi nadie da un número: **ninguna corrutina hace trabajo de CPU de más de un milisegundo sin ceder.**

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>OJO ACÁ: el umbral de un milisegundo suena exagerado hasta que hacés la cuenta</strong></p>
<ul>
<li><p><strong>1 ms</strong> por petición × 100 peticiones/s = <strong>10 %</strong> del hilo consumido en calcular.</p></li>
<li><p><strong>10 ms</strong> × 100 = <strong>100 %</strong>. El servidor no hace otra cosa.</p></li>
<li><p><strong>bcrypt con factor 12 tarda del orden de 250 ms.</strong> <strong>Cuatro logins por segundo saturan el proceso completo.</strong></p></li>
</ul>
<p>Ese último número explica por qué bcrypt tiene <strong>dos reglas dedicadas y un semáforo</strong>. Y ojo con el matiz: <strong>no es que bcrypt sea lento por estar mal hecho — es lento a propósito</strong>, justamente para que probar contraseñas por fuerza bruta sea caro. Lo que es una virtud contra un atacante es un problema contra tu bucle de eventos.</p>
<p>Y la trampa que engaña: <strong>en tu máquina, probando solo, cuatro logins por segundo no van a pasar nunca.</strong> Anda perfecto. El problema aparece el día que <strong>treinta personas entran a la vez al empezar el turno</strong>.</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

Falta explicar **el semáforo**, porque es la parte que sorprende. Sacar bcrypt a un hilo evita bloquear el bucle, **pero no evita que cien intentos de login simultáneos lancen cien hilos** haciendo un cálculo deliberadamente caro. El semáforo **acota cuántos pueden ejecutarse a la vez**. La clase 5 lo desarrolla.

### Y ahora la regla más contraintuitiva de las ocho: EA-01

El marco de trabajo **admite** handlers sincrónicos: si declarás uno con def, lo ejecuta en un hilo de un grupo reservado. **Eso es lento pero contenido**: bloquea un hilo de veinte, y el resto sigue.

Un handler async con una línea bloqueante adentro **no va a ningún hilo**. Corre en el bucle, y esa línea **detiene el proceso completo**.

<img src="media/image3.png" style="width:5.79167in;height:3.61458in" />

**Figura 3.3** *— Qué pasa cuando una línea bloquea, en los tres casos.*

# 3.7 — Clientes asincrónicos para toda entrada y salida

De todo lo anterior sale **EA-03**, que es la regla **más mecánica** de las ocho: toda la I/O usa clientes asincrónicos —psycopg asincrónico para PostgreSQL, redis.asyncio para Redis, httpx.AsyncClient para cualquier llamada saliente— y **el módulo redis síncrono no se importa en ninguna parte del backend**.

**Esa última frase es la que la vuelve verificable.** No dice «usá el cliente asincrónico»: dice que **el otro no aparece en ningún import**, y eso se puede comprobar con una búsqueda de texto.

El problema práctico que previene es que muchas bibliotecas ofrecen las dos variantes **con nombres parecidos**, y la sincrónica suele ser **la que aparece en los ejemplos de internet**:

| **Sincrónico — prohibido** | **Asincrónico — el del TPI**                |
|----------------------------|---------------------------------------------|
| import redis               | import redis.asyncio as redis               |
| import requests            | import httpx con AsyncClient                |
| psycopg.connect(...)       | psycopg asincrónico vía create_async_engine |
| time.sleep(n)              | await asyncio.sleep(n)                      |

**La última fila merece mención porque aparece en código de prueba todo el tiempo:** time.sleep **bloquea el bucle** durante el tiempo indicado. Su equivalente asincrónico cede el control y permite atender otras peticiones mientras tanto.

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>EA-03 tiene una virtud que la separa de las otras siete: se verifica con un grep</strong></p>
<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th>grep -rn "^import requests\|^import redis$\|time.sleep" app/</th>
</tr>
</thead>
<tbody>
</tbody>
</table>
<p>Si eso devuelve algo, <strong>hay una violación</strong>. Sin discusión, sin criterio, sin revisión humana.</p>
<p>Fijate por qué eso importa: <strong>una regla que se puede verificar automáticamente es una regla que se cumple.</strong> Una que depende de que alguien revise, <strong>se cumple hasta que hay apuro</strong>.</p>
<p>Cuando armes el proyecto, ese grep va <strong>en el mismo lugar donde corren los tests</strong>. Y lo mismo vale para el resto: cada vez que puedas convertir una regla en una verificación automática, hacelo.</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

# 3.8 — La regla del greenlet: la que más tiempo hace perder

Acá está lo que el TPI señala con ese nombre, y **lo explica en detalle en lugar de limitarse a prohibirlo**. Vale la pena seguir su razonamiento completo, porque **entender el mecanismo es lo que permite diagnosticar el error**.

## 3.8.1 — Cómo funciona la capa asincrónica del ORM

SQLAlchemy implementa su capa asincrónica **ejecutando el ORM sincrónico dentro de un greenlet** y saltando al bucle de eventos cada vez que necesita I/O.

Un **greenlet** es una corrutina de bajo nivel: una unidad de ejecución que puede suspenderse y reanudarse, implementada por fuera del lenguaje. Lo que SQLAlchemy hace es **no reescribir su ORM** —que tiene años de trabajo y es sincrónico— sino **ejecutarlo adentro de uno de estos greenlets**, y cada vez que ese código sincrónico necesita hablar con la base, saltar al bucle, esperar ahí, y volver.

Y sigue la parte importante: **el mecanismo es transparente mientras la I/O ocurra donde SQLAlchemy la espera** — dentro de un await sobre uno de sus métodos. Ahí está la condición: **el salto al bucle sólo es posible desde adentro del greenlet**, y sólo se entra al greenlet cuando se hace await sobre un método del ORM.

## 3.8.2 — Cuándo falla, y por qué el mensaje no ayuda

Cuando el ORM intenta emitir una consulta **desde un lugar donde no hay await** —al leer un atributo de una relación no cargada, o al tocar un objeto expirado después del commit— **no hay a dónde saltar**, y la excepción es MissingGreenlet.

<img src="media/image4.png" style="width:5.79167in;height:3.94792in" />

**Figura 3.4** *— Dónde el ORM puede saltar al bucle y dónde no: las dos causas y sus dos reglas.*

Y como el mensaje no menciona la causa, **hay que aprender a leer la traza** — la Figura 3.6, en la sección 3.12, la desarma línea por línea.

## 3.8.3 — El N+1 que dejó de ser un problema de rendimiento

Y acá viene **lo mejor del razonamiento del TPI**, que conviene leer entero:

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>Lo que declara el TPI</strong></p>
<p>La consecuencia práctica es <strong>buena</strong> y conviene verla así: <strong>el N+1 deja de ser un problema de rendimiento y pasa a ser un error en tiempo de ejecución.</strong> La tabla de precarga de la sección 8.3 es <strong>una condición para que el endpoint funcione, no una recomendación</strong>. El sistema <strong>no puede tener un N+1 accidental</strong>: lo que tendría, tiene una excepción.</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

Conviene desarmar por qué eso es **una ventaja y no un castigo**. El problema conocido como **N+1** consiste en emitir una consulta para traer una lista y después **una consulta más por cada elemento** para traer su relación. Con cien pedidos son **ciento una consultas donde debía haber dos**.

En un sistema sincrónico eso **funciona**. Es lento, y sólo se descubre cuando alguien mira los registros de la base o cuando la lentitud molesta lo suficiente. **Es un problema silencioso, y los problemas silenciosos sobreviven años.**

En este sistema **no funciona**: lanza una excepción **en la primera iteración**. No hay forma de que un N+1 llegue a producción sin que nadie lo note, **porque no llega a producción en absoluto**.

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>PARA ENTENDER: el mejor ejemplo del módulo de una restricción que parece castigo y es regalo</strong></p>
<p><strong>En un sistema sincrónico, el N+1 anda.</strong> Lento, pero anda. Y por eso <strong>vive escondido durante años</strong>, hasta que un día la tabla creció y alguien nota que una pantalla tarda ocho segundos.</p>
<p><strong>Acá el N+1 no anda: explota.</strong> En la primera iteración, en tu máquina, mientras lo estás escribiendo.</p>
<p>Fijate lo que eso significa: <strong>no es que el sistema sea más frágil.</strong> Es que <strong>un problema de rendimiento invisible se convirtió en un error visible</strong> — y los errores visibles se arreglan.</p>
<p>Es la misma idea que atraviesa todo el material, del backend y del frontend: <strong>las reglas que dependen de que alguien se acuerde fallan; las que hacen que equivocarse sea imposible, no.</strong> Acá ni siquiera hay una regla que recordar: <strong>el sistema directamente no te deja</strong>.</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

# 3.9 — Tareas en segundo plano

**EA-07 prohíbe algo que parece la solución natural**: las tareas en segundo plano de una petición **no se lanzan con asyncio.create_task()**. Se encolan en la cola de tareas o, si deben ocurrir sin falta, se escriben en el outbox.

El razonamiento es directo cuando se ve el caso. Alguien confirma un pedido y hay que mandar un correo. El correo tarda, así que la tentación es lanzarlo suelto y responder de inmediato:

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p>asyncio.create_task(enviar_correo(pedido)) # prohibido por EA-07</p>
<p>return respuesta</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

Eso responde rápido y tiene **tres problemas, cada uno peor que el anterior**:

| **El problema**                                    | **Qué significa en la práctica**                                                                                                                                              |
|----------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Si el proceso se reinicia, la tarea desaparece** | Vive en la memoria de ese proceso. Un despliegue o una caída se la lleva, y **nadie se entera de que ese correo nunca salió**                                                 |
| **Si falla, el error no llega a ningún lado**      | Nadie está esperando ese resultado, y una excepción en una tarea suelta que nadie observa **se descarta con una advertencia en el registro** — si es que se descarta con algo |
| **No hay reintento**                               | **No existe nada que sepa que esa tarea existió**                                                                                                                             |

La alternativa que el TPI declara —**encolar**, o **escribir en el outbox** si el hecho no se puede perder— resuelve las tres: **el trabajo vive fuera del proceso**, alguien lo va a buscar, y si falla se reintenta. La clase 8 lo desarrolla junto con las siete reglas del trabajo diferido.

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>Una frase del TPI que invierte la carga de la prueba</strong></p>
<p><strong>«Una tarea que no se puede repetir sin daño es un defecto.»</strong></p>
<p>No dice «cuidado con reintentar». Dice que <strong>si tu tarea se rompe al ejecutarse dos veces, el problema es tu tarea</strong>, no el reintento.</p>
<p>Y hay una razón dura detrás: <strong>ningún sistema de colas garantiza que algo se ejecute exactamente una vez.</strong> Puede garantizar <strong>al menos una</strong> —que es lo que hacen casi todos— o <strong>como mucho una</strong>. «Exactamente una» es, en un sistema distribuido, <strong>un problema sin solución general</strong>.</p>
<p>Entonces el reintento <strong>no es una decisión que podés evitar: va a pasar</strong>, porque un worker puede morir después de hacer el trabajo y antes de confirmar el mensaje. <strong>Lo único que podés decidir es si tu tarea lo tolera.</strong></p>
<p>Del otro lado del cable pasa exactamente lo mismo: el checkout genera una clave de idempotencia justamente porque <strong>la red tampoco garantiza que algo llegue exactamente una vez</strong>.</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

# 3.10 — Recursos y ciclo de vida

**EA-08 cierra el conjunto**: el pool de conexiones y el cliente de Redis se crean **en el lifespan** de la aplicación y se cierran ahí. **No se crean por petición ni a nivel de módulo.** Y la suite de tests dispara el lifespan con una herramienta específica.

**Las dos prohibiciones responden a problemas distintos.**

**No por petición**, porque establecer una conexión es caro **y un pool existe justamente para evitarlo**. Crear uno por petición es tener un pool de uno — o sea, ninguno.

**No a nivel de módulo**, y esta es la que produce errores desconcertantes. Un cliente creado como variable global **se construye al importar el archivo**, que es un momento en el que **puede no haber un bucle de eventos corriendo**. El síntoma clásico es que **el servidor levanta bien y los tests fallan** —o al revés—, con mensajes sobre bucles distintos que **no señalan la causa**.

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>PARA ENTENDER: la cadena completa, de una regla a una línea del archivo de dependencias</strong></p>
<p><strong>EA-08</strong> dice que el pool va en el ciclo de vida →</p>
<p>los tests <strong>necesitan</strong> ese pool →</p>
<p>entonces <strong>los tests tienen que disparar el ciclo de vida</strong> →</p>
<p>y para eso hace falta <strong>una herramienta específica</strong> →</p>
<p><strong>por eso está asgi-lifespan en el stack.</strong></p>
<p>Si mirás la lista de diecinueve tecnologías del TPI, asgi-lifespan parece <strong>la más arbitraria de todas</strong>. No lo es: <strong>está ahí porque EA-08 la hace necesaria.</strong></p>
<p>Y esto vale como <strong>método de lectura para todo el documento</strong>: cuando algo del stack te parezca raro, <strong>buscá qué regla lo obliga</strong>. Casi siempre hay una.</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

# 3.11 — Lo que la sincronía hacía bien

Esta sección **rara vez se enseña**, y el TPI la declara. Es **la contracara** del modelo asincrónico, y saberla es lo que separa usarlo de padecerlo.

En un modelo sincrónico, el grupo de hilos **pone un techo natural** a la cantidad de operaciones concurrentes contra la base. Con corrutinas ese techo **desaparece** —se pueden tener diez mil tareas esperando— y el recurso que se agota primero pasa a ser **el pool de conexiones**, con un error mucho menos legible.

<img src="media/image5.png" style="width:5.79167in;height:3.96875in" />

**Figura 3.5** *— El techo que desaparece al pasar de hilos a corrutinas, y qué hay que reponer.*

Conviene subrayar el detalle que hace difícil este problema: **ese techo nadie lo puso a propósito**. Es una consecuencia del modelo, y **protege sin que nadie lo decida**. Cuando el modelo cambia, la protección se va **sin que nadie lo note** — porque nunca estuvo escrita en ningún lado.

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>La respuesta honesta a «¿asincrónico es mejor?»</strong></p>
<p><strong>No es mejor: es distinto, y el intercambio está declarado.</strong></p>
<p>Ganás que un servidor atienda miles de conexiones sin gastar un hilo en cada una. <strong>Perdés un techo que te venía de regalo y que ahora tenés que poner vos.</strong></p>
<p>Y fijate el detalle más importante: <strong>el sistema no te avisa que perdiste ese techo.</strong> Anda perfecto hasta que un día hay suficiente carga, y ahí falla con un error de pool agotado que <strong>no dice nada sobre la causa real</strong>.</p>
<p>Por eso el TPI declara esas dos variables en vez de dejarlas en su valor por defecto. <strong>Cuando algo deja de estar garantizado por el modelo, hay que garantizarlo explícitamente</strong> — o aceptar que un día te va a sorprender.</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

# 3.12 — Herramientas de diagnóstico

| **Herramienta**                          | **Qué te dice**                                                                                                                                                                                                                    | **Cuándo**                                                                                                                                            |
|------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------|
| **El modo de depuración de asyncio**     | **Avisa cuando una corrutina tardó demasiado sin ceder**, indicando cuál fue y cuánto tardó. También advierte sobre corrutinas que nunca se esperaron                                                                              | Es **la más útil y la que menos se usa**: convierte el problema de la sección 3.6 —que es invisible— en un mensaje concreto                           |
| **La traza de la excepción de greenlet** | Hay que **aprender a leerla**, porque su mensaje no menciona la causa. La causa real está en **el acceso a un atributo, unas líneas más arriba**, o en el repositorio que no declaró la precarga — que puede estar en otro archivo | Figura 3.6. El procedimiento: ubicar qué relación se estaba leyendo, buscar la consulta que trajo ese objeto, verificar si declaró su precarga        |
| **El registro de consultas del ORM**     | Muestra **cada sentencia emitida**                                                                                                                                                                                                 | Para verificar que una consulta con precarga emite **dos y no ciento una** — y para descubrir consultas que nadie esperaba                            |
| **Las conexiones en uso del pool**       | Cuántas hay ocupadas y por cuánto tiempo                                                                                                                                                                                           | Cuando aparecen errores de espera agotada. **Si el pool está lleno de forma sostenida, el problema es el de la sección 3.11 y no una consulta lenta** |

<img src="media/image6.png" style="width:5.79167in;height:4.625in" />

**Figura 3.6** *— Una traza de la excepción y dónde está su causa real.*

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>EXPERIMENTO — treinta segundos, y hace visible todo el capítulo</strong></p>
<p>Hacelo sí o sí.</p>
<ul>
<li><p><strong>Uno.</strong> Escribí dos endpoints: uno que haga await asyncio.sleep(5) y otro que responda de inmediato.</p></li>
<li><p><strong>Dos.</strong> Abrí dos pestañas. Pedí el lento en una y el rápido en la otra. <strong>El rápido responde al instante</strong>, aunque el lento siga esperando.</p></li>
<li><p><strong>Tres.</strong> Ahora cambiá el primero por time.sleep(5) —sin await— y repetí.</p></li>
</ul>
<p><strong>El rápido no responde hasta que el lento termina.</strong> Y no es que esté encolado detrás: <strong>el proceso entero está detenido.</strong></p>
<ul>
<li><p><strong>Cuatro.</strong> Abrí cinco pestañas más y pedí cualquier endpoint. <strong>Ninguno contesta.</strong></p></li>
<li><p><strong>Cinco.</strong> Probá también /docs. <strong>Tampoco.</strong></p></li>
</ul>
<p>Una línea. <strong>Un solo carácter de diferencia</strong> entre time.sleep y await asyncio.sleep. <strong>Y el servidor entero deja de existir durante cinco segundos.</strong></p>
<p>Eso es lo que EA-01, EA-02 y EA-06 previenen — <strong>y por eso son tres reglas y no una recomendación</strong>.</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

# 3.13 — Seguridad y evolución

| **La consideración**                                                    | **Por qué es de seguridad**                                                                                                                                                                                                                                                               |
|-------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Una operación bloqueante es una denegación de servicio sin atacante** | No hace falta mala intención: alcanza con un endpoint que procese un archivo subido por el usuario de forma sincrónica. Quien quiera tirar el servicio **sólo tiene que llamar a ese endpoint unas cuantas veces**, y el costo del ataque es **ridículamente bajo comparado con el daño** |
| **El plazo de espera es parte de la defensa**                           | Una llamada saliente sin plazo **puede quedar pendiente indefinidamente**, ocupando una conexión del pool. Con suficientes llamadas en ese estado, el pool se agota y **el sistema deja de responder sin que nadie haya hecho nada malo**                                                 |
| **Una tarea que falla en silencio es un problema de auditoría**         | Si una operación que debía ocurrir no ocurrió y nadie se enteró, **el sistema quedó en un estado que sus registros no reflejan**. Es una de las razones de EA-07                                                                                                                          |

Sobre la evolución, dos observaciones. **La primera:** el bloqueo global del intérprete **está siendo revisado** —existe una modalidad experimental sin él desde Python 3.13—. Eso **no cambia nada de este capítulo**, porque el modelo asincrónico **no se eligió por el bloqueo** sino por lo que estableció el Capítulo 1: un servidor pasa su tiempo esperando, y esperar no necesita un hilo por espera.

**La segunda:** la comunidad viene **reduciendo la cantidad de operaciones bloqueantes disponibles**. Cada vez más bibliotecas ofrecen variante asincrónica, y las herramientas de análisis estático detectan llamadas sincrónicas dentro de corrutinas. **Lo que hoy exige disciplina, mañana lo va a marcar una herramienta** — y esa es siempre la evolución deseable de una regla.

# 3.14 — Verificación: el checklist honesto

Nueve comprobaciones. **No son ejercicios: son el criterio para saber si el capítulo se entendió.**

1.  Reproducir el experimento de la sección 3.12 y **documentar la diferencia** entre las dos versiones. *(3.12)*

2.  Explicar por qué un handler def con código sincrónico es **menos grave** que uno async def con una línea sincrónica adentro. *(3.6)*

3.  Escribir una operación bloqueante y **sacarla a un hilo**, verificando que el bucle sigue atendiendo. *(3.6)*

4.  Enumerar **las tres operaciones bloqueantes** que el TPI declara y justificar por qué cada una lo es. *(3.6)*

5.  Buscar en un proyecto propio importaciones de clientes sincrónicos y **listar las violaciones de EA-03**. *(3.7)*

6.  **Provocar una excepción de greenlet** por relación no precargada, y corregirla. *(3.8)*

7.  Provocar **la misma excepción por objeto expirado** tras el commit, y corregirla con la opción que EA-04 declara. *(3.8.2)*

8.  Escribir dos consultas independientes con dos await seguidos y con un grupo de tareas, y **medir la diferencia**. *(3.5)*

9.  Explicar **qué techo desaparece** al pasar de hilos a corrutinas, y qué hay que configurar para reponerlo. *(3.11)*

# 3.15 — Los once errores frecuentes

Casi todos comparten una característica: **en tu máquina, probando solo, andan perfecto**.

| **El error**                                                                | **Por qué duele**                                                                            | **Sección** |
|-----------------------------------------------------------------------------|----------------------------------------------------------------------------------------------|-------------|
| **Declarar un handler async def y llamar adentro a una función sincrónica** | Es la mezcla que EA-01 declara **peor que la sincronía completa**: detiene el proceso entero | 3.6         |
| **Usar un cliente sincrónico «porque es el que sale en los ejemplos»**      | Viola EA-03, y **en desarrollo no se nota**                                                  | 3.7         |
| **Usar time.sleep en lugar de su equivalente asincrónico**                  | Bloquea el bucle **durante todo ese tiempo**                                                 | 3.7         |
| **Encadenar await de operaciones independientes**                           | No falla: **tarda el doble sin motivo** — y pasa cualquier test                              | 3.5         |
| **Llamar a una corrutina sin await y suponer que se ejecutó**               | No se ejecuta: **devuelve un objeto**                                                        | 3.5         |
| **Leer una relación que no se precargó**                                    | Excepción de greenlet, **con una traza que no menciona la causa**                            | 3.8         |
| **Dejar expire_on_commit en su valor por defecto**                          | El objeto queda expirado tras el commit y **la primera lectura falla**. Viola EA-04          | 3.8.2       |
| **Lanzar trabajo en segundo plano con una tarea suelta**                    | Se pierde al reiniciar, **el error no llega a nadie** y no hay reintento. Viola EA-07        | 3.9         |
| **Crear el pool o el cliente de Redis a nivel de módulo**                   | Se construyen al importar, **cuando puede no haber bucle**. Viola EA-08                      | 3.10        |
| **Calcular el tamaño del pool contra la cantidad de workers**               | Con corrutinas el techo lo pone **la concurrencia esperada**, no los procesos                | 3.11        |
| **Omitir el plazo de espera en una llamada saliente**                       | Una llamada colgada **ocupa una conexión del pool indefinidamente**                          | 3.13        |

# 3.16 — Las actividades, y qué busca cada una

### 1. El bloqueo medido

Implementar **tres endpoints** —uno correcto, uno con handler sincrónico y uno async con línea bloqueante— y medir, con **veinte peticiones simultáneas**, cuánto tarda cada configuración en responderlas todas. Explicar los tres resultados con la Figura 3.3.

***Qué busca:** que veas el número, no la explicación. La diferencia entre el caso 1 y el caso 3 es abismal y no se intuye.*

### 2. Las ocho reglas auditadas

Tomar un proyecto de ejemplo con FastAPI y revisar **una por una las ocho reglas EA**, documentando para cada una **si se cumple, cómo se verificó, y qué habría que cambiar si no**.

***Qué busca:** descubrir que algunas se verifican con un grep y otras exigen leer. Esa diferencia es la que después decide qué automatizás.*

### 3. La excepción de greenlet, las dos veces

Provocarla **por sus dos causas** —relación no precargada y objeto expirado—, capturar ambas trazas, y documentar **qué parte de cada traza señala la causa real y cuál despista**.

***Qué busca:** que la próxima vez que aparezca, en un parcial o en el TPI, sepas dónde mirar en vez de leer la última línea diez veces.*

### 4. El N+1 que no puede existir

Escribir un endpoint que liste pedidos con su usuario **sin declarar la precarga** y documentar qué ocurre. Corregirlo con selectinload y **contar las consultas emitidas** en ambos casos con el registro del ORM.

***Qué busca:** ver con los ojos que la versión rota no es «más lenta», es que **no existe**. Y que la corregida emite dos consultas, no ciento una.*

### 5. Serie contra concurrencia

Implementar un endpoint que necesite **cuatro consultas independientes**, resolverlo de las dos formas, y medir. **Justificar en qué casos la versión secuencial sería la correcta.**

***Qué busca:** la segunda mitad. Hay casos donde secuencial es lo correcto —cuando una consulta necesita el resultado de la anterior— y saber distinguirlos es el punto.*

### 6. Exploración: el techo que desaparece

Configurar un pool de **cinco conexiones** y lanzar **cincuenta peticiones concurrentes** contra un endpoint que consulte la base. Documentar **qué error aparece, en qué momento, y qué dice exactamente su mensaje**. Relacionarlo con la sección 3.11 y proponer los dos valores de configuración que el TPI declara.

***Qué busca:** leer con tus ojos un mensaje de error que no menciona la causa real. Es la experiencia completa de la sección 3.11 en cinco minutos.*

### 7. Exploración: los dos lados del mismo bucle

Junto con alguien del turno de frontend, comparar el modelo de ejecución de los dos lados: **qué es una corrutina acá y una promesa allá**, qué cede el control en cada caso, y qué pasa cuando algo bloquea. Armar **un solo diagrama que sirva para los dos** y documentar en qué se diferencian.

***Qué busca:** que descubran la diferencia que más confunde — una promesa arranca al crearse, una corrutina no hace nada hasta que se la agenda.*

# 3.17 — Síntesis: las once frases

1.  La sección 1.4 del TPI es **normativa y todo el resto del documento la presupone**. Sus ocho reglas no están repartidas: **están juntas porque responden a un mismo hecho**.

2.  La concurrencia asincrónica es **cooperativa**: nadie interrumpe a una corrutina, **ella cede**. De ahí se deduce todo lo demás, incluida la gravedad de una línea bloqueante.

3.  **Concurrencia no es paralelismo.** Un solo hilo alternando es concurrente y no paralelo, y para un servidor eso alcanza porque el trabajo dominante es esperar.

4.  Los puntos de cesión **son visibles**: cada await es un lugar donde el control puede irse. Eso permite razonar sobre qué puede pasar entre dos líneas.

5.  Una corrutina **no hace nada hasta que se la agenda**, al revés de lo que ocurre del otro lado del cable, donde una promesa arranca al crearse.

6.  **Un handler async con una línea bloqueante es peor que un handler sincrónico completo**: el segundo bloquea un hilo de un grupo, el primero **detiene el proceso entero**.

7.  El TPI enumera **tres operaciones bloqueantes** y les da una única solución: **sacarlas a un hilo**. Y pone un umbral concreto: **un milisegundo** de trabajo de procesador sin ceder.

8.  SQLAlchemy ejecuta su ORM sincrónico **dentro de un greenlet** y salta al bucle cuando necesita entrada y salida. Cuando el ORM intenta consultar desde un lugar sin await, **no hay a dónde saltar**.

9.  **El N+1 dejó de ser un problema de rendimiento y pasó a ser un error de ejecución.** Eso no es un castigo: **un problema silencioso se volvió visible**, y los problemas visibles se arreglan.

10. Una **tarea suelta** se pierde al reiniciar, falla en silencio y no se reintenta. Y **una tarea que no se puede repetir sin daño es un defecto**.

11. **El modelo asincrónico no es gratis.** El grupo de hilos ponía un techo que ahora desapareció, y el primer recurso que se agota es el pool. **Cuando algo deja de estar garantizado por el modelo, hay que garantizarlo explícitamente.**

# 3.18 — Qué leer, y en qué orden

### Si leés una sola cosa

**Ramalho**, *Fluent Python* (2.ª edición, O'Reilly, 2022) — dedica **tres capítulos** al modelo asincrónico y es **la mejor explicación disponible para quien ya programa**. Su tratamiento de la diferencia entre concurrencia y paralelismo es más claro que el de la documentación oficial.

### Si leés tres

- La documentación de **SQLAlchemy** sobre su **extensión asincrónica**: es **la fuente directa de la sección 3.8**. Documenta el mecanismo de greenlet, enumera las operaciones que no pueden ocurrir fuera de él, y explica por qué la carga perezosa es incompatible con ese modelo.

- **Nathaniel J. Smith**, *Notes on structured concurrency* (2018): el texto que introdujo las ideas que después llegaron al lenguaje **como grupos de tareas**.

- **David Beazley**, *Generators: The Final Frontier* (PyCon 2014): muestra cómo se construía código asincrónico con generadores **antes de que existiera la sintaxis propia**, y su lectura hace evidente qué resolvió el PEP 492.

### Las fuentes normativas: los PEP, todos en peps.python.org

- **PEP 342** (2005) y **PEP 380** (2009): convirtieron los generadores en corrutinas bidireccionales y agregaron la delegación. Explican **por qué la sintaxis previa a async/await era como era**.

- **PEP 3156** (2012): incorporó asyncio a la biblioteca estándar. **Su sección de fundamentos discute las alternativas que se descartaron.**

- **PEP 492** (2015): agregó async y await. Su motivación enuncia con claridad el problema que resolvía — **que una corrutina y un generador fueran indistinguibles**.

- **PEP 654** (2021): grupos de excepciones y except\*. **Sin ellos los grupos de tareas no podrían propagar varios errores a la vez** — es la razón directa del piso de versión que el TPI fija.

- **PEP 703**: documenta la modalidad experimental sin bloqueo global de la sección 3.13.

### Del TPI

Este capítulo se apoya **casi enteramente en la sección 1.4**, que conviene **leer completa y tener a mano durante todo el módulo**. Se anticipan además la **5.5** —bcrypt fuera del bucle y su semáforo—, la **8.3** con la tabla de precarga que EA-05 exige, y la **16.1** con las dos variables de configuración que la sección 3.11 justifica.

# Cierre: las seis cosas que hay que recordar

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>LAS SEIS</strong></p>
<p><strong>1.</strong> <strong>Nadie te interrumpe: vos cedés.</strong> No es que bloquear sea lento — es que <strong>no existe el mecanismo</strong> para sacarte del medio.</p>
<p><strong>2.</strong> <strong>Buscá los await.</strong> Son los únicos lugares donde tu función se pausa. Una async sin ningún await adentro es sospechosa.</p>
<p><strong>3.</strong> <strong>La mezcla es lo peor:</strong> un handler async con una línea sincrónica adentro <strong>detiene el proceso entero</strong>, mientras que uno def completo sólo bloquea un hilo de veinte.</p>
<p><strong>4.</strong> <strong>El greenlet explica el error que más tiempo hace perder.</strong> La causa nunca está en la última línea de la traza: está en el acceso a un atributo, o en el repositorio que no declaró la precarga.</p>
<p><strong>5.</strong> <strong>El N+1 dejó de ser lentitud y pasó a ser excepción.</strong> Eso es un regalo: los problemas visibles se arreglan, los silenciosos sobreviven años.</p>
<p><strong>6.</strong> <strong>Asincrónico no es mejor: es distinto.</strong> Perdiste un techo que te venía de regalo, y ahora lo tenés que poner vos.</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

Y una séptima, que es el método de lectura de todo el TPI: **cuando algo del stack o de las reglas te parezca arbitrario, buscá qué problema lo obliga.** asgi-lifespan en la lista de dependencias, el semáforo de bcrypt, el expire_on_commit=False. Ninguno está por gusto — **cada uno es la cicatriz de un problema que alguien ya tuvo.**
