**CAPÍTULO 1 — GUÍA DE LECTURA**

**Del objeto al servicio**

HTTP del lado del servidor, explicado en criollo

*Traducción didáctica del texto académico, sección por sección. Mismos conceptos, otro idioma.*

# Antes de empezar: cómo usar esta guía

Este documento no reemplaza al capítulo original. Lo traduce. El texto académico está bien escrito, pero está escrito en el idioma en el que se escriben los papers: denso, comprimido, con cada frase cargada. Esta guía lo desarma y lo cuenta como se lo contarías a alguien en un café.

La regla que seguí es una sola: **no se pierde ni un concepto**. Si el original dice ASGI, acá dice ASGI. Lo que cambia es que además te explico qué carajo es y por qué te importa.

Cada sección tiene tres partes:

- **Qué dice** — la idea del original, en dos o tres oraciones.

- **En criollo** — la explicación larga, con la analogía que la hace pegar.

- **Para el pizarrón** — la frase que te tenés que llevar. Si te acordás sólo de eso, ya ganaste algo.

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>LA IDEA MADRE DE TODO EL CAPÍTULO</strong></p>
<p>Si tuvieras que quedarte con una sola frase de las cuarenta páginas, es esta:</p>
<p><strong>Un servidor web se pasa la vida esperando, no calculando.</strong></p>
<p>Esperando que llegue un pedido. Esperando que la base de datos conteste. Esperando que el cliente termine de bajar la respuesta.</p>
<p>Todo lo demás del capítulo —por qué asincrónico y no hilos, por qué el GIL de Python no molesta, por qué bcrypt es un problema— se deduce de ahí. No es una curiosidad: es el eje.</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

# 1.1 — Esta clase no arranca de cero

### Qué dice

Las ocho actividades de Programación Orientada a Objetos que vinieron antes no eran trámite ni repaso. Eran el vocabulario. Y este capítulo lo empieza a usar desde la primera página.

### En criollo

Imaginate que estudiaste inglés dos años y recién ahora te sientan a leer un libro. No estás empezando de nuevo: estás **cobrando** lo que hiciste. Eso es esta clase respecto de POO.

El ejemplo concreto es la actividad 8, donde viste la diferencia entre dos formas de que una clase consiga lo que necesita:

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p>class Servicio:</p>
<p>def __init__(self):</p>
<p>self.repo = RepositorioSQL() # dependencia de CREACIÓN</p>
<p>class Servicio:</p>
<p>def __init__(self, repo: RepositorioProtocol):</p>
<p>self.repo = repo # dependencia de USO</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

La primera se va a buscar sola lo que necesita. La segunda espera que se lo den. Y la conclusión de aquella actividad era: la segunda se puede probar con un repositorio falso, la primera no, porque no hay forma de meterle otra cosa.

Bueno: eso, que ahí era un principio de diseño abstracto, acá tiene un nombre propio en el framework —se llama Depends()— y está escrito como **requisito obligatorio** del TPI:

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>LO QUE EXIGE EL TPI (sección 2.1)</strong></p>
<p>El Router importa el tipo UnitOfWork únicamente para anotar la dependencia que resuelve con Depends(get_uow), y lo transporta hacia el Service: <strong>no lo construye, no abre su contexto, no invoca ninguno de sus métodos y no conoce los repositorios que expone.</strong></p>
<p>Traducción: el Router es un mozo. Lleva el pedido a la cocina. No cocina, no abre la heladera, no sabe qué hay adentro.</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

### Los tres objetivos de la clase

1.  **Entender qué hace un servidor web**: qué recibe, qué devuelve, y por qué atender a mucha gente a la vez es un problema difícil que tuvo tres respuestas históricas distintas.

2.  **Construir el primer endpoint** y entender cada pieza de lo que escribiste (no copiar y que ande).

3.  **Ubicar cada archivo en su capa** — y este es el importante para las siete clases que siguen. El TPI declara un flujo de dependencias estricto. El que no lo tiene claro desde el día uno escribe código que funciona y que hay que reescribir.

Hay además una coincidencia buena: el módulo de frontend va en paralelo y esta misma semana estudia la anatomía de una petición HTTP desde el navegador. Lo que allá es una tabla —método, ruta, cuerpo, respuesta— acá es el código que la contesta. **Es la misma petición vista desde los dos extremos del cable, el mismo día.**

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>PARA EL PIZARRÓN</strong></p>
<p>Al terminar la clase tenés que poder hacer tres cosas: levantar un servicio con varios endpoints, explicar qué resuelve Depends(), y agarrar cualquier archivo del backend y decir en qué capa está y qué tiene permitido importar.</p>
<p>Si podés las tres, la clase la aprobaste. Si te falta la tercera, vas a escribir código que anda y que hay que tirar.</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

# 1.2 — Por qué atender a muchos es difícil

### Qué dice

Un servidor tiene un problema que un programa de escritorio no tiene: tiene que atender a muchos a la vez, y la mayor parte del tiempo no está haciendo nada. Está esperando. Ese detalle explica las tres respuestas históricas al problema y por qué ganó la tercera.

### En criollo: el restaurante

Pensá un restaurante. Un mozo toma el pedido, lo lleva a la cocina, y después... espera. La cocina tarda veinte minutos. Durante esos veinte minutos el mozo no cocina, no hace nada útil para esa mesa. Solamente espera.

Un servidor web es eso, todo el día. Espera que llegue una petición. Espera que Postgres devuelva las filas. Espera que Redis conteste. Espera que el cliente termine de recibir los bytes. **El trabajo dominante es esperar, no calcular.** Y de ahí salen las tres respuestas.

### Respuesta 1 (1993): un proceso por petición

La interfaz CGI funcionaba así: llega una petición, el servidor **crea un proceso nuevo** para atenderla, y ese proceso muere cuando termina.

En el restaurante: **contratás un mozo nuevo para cada cliente que entra, y lo echás cuando el cliente se va.** Cada contratación implica papeleo, uniforme, explicarle dónde está la cocina.

Era simple y era robusto —si un mozo se equivoca, no afecta a los demás— y era **carísimo**. Crear un proceso significa reservar memoria, copiar el espacio de direcciones y hacer que el sistema operativo lo planifique. Con decenas de peticiones por segundo, el servidor pasaba más tiempo contratando mozos que atendiendo mesas.

### Respuesta 2: un hilo por conexión

Un hilo es mucho más barato que un proceso: comparte memoria y se crea rápido. En el restaurante: **tenés una plantilla de mozos fijos y le asignás uno a cada mesa.** Ya no contratás y echás gente todo el tiempo.

Funcionó bien durante años y sigue funcionando hasta cierta escala. Pero tiene dos costos que aparecen al crecer:

- **Cada hilo reserva su propia pila**, del orden de un megabyte. Diez mil conexiones simultáneas son diez gigabytes solamente en pilas, sin haber hecho todavía nada útil.

- **El sistema operativo tiene que alternar entre esos hilos**, guardando y restaurando estado cada vez. Ese costo crece con la cantidad. Con muchísimos mozos, el encargado se pasa el día diciendo quién atiende qué.

Ese límite tuvo nombre propio. En 1999 Dan Kegel publicó un artículo llamado **el problema C10K**, y la pregunta era: cómo atender diez mil conexiones simultáneas en una sola máquina. Su respuesta fue que un hilo por conexión no escala, y que hacía falta otra cosa.

### Respuesta 3: un solo hilo que multiplexa

Acá está el truco, y es hermoso de simple: **si el trabajo dominante es esperar, un solo hilo puede esperar muchas cosas a la vez.**

En el restaurante: **un solo mozo, muy vivo.** Toma el pedido de la mesa 1, lo deja en la cocina, y en vez de quedarse parado ahí, va a la mesa 2. Toma ese pedido, lo deja, va a la 3. Cuando la cocina grita que está listo el de la mesa 1, va y lo lleva. Un mozo, quince mesas, y nadie espera de más.

El sistema operativo ofrece mecanismos para preguntar exactamente eso: «de todas estas conexiones, cuál tiene datos listos». Primero fue select, después poll, y finalmente epoll en Linux y kqueue en BSD, que fueron los que resolvieron el problema de escala. El programa mantiene un **bucle de eventos**: pregunta qué está listo, atiende eso, vuelve a preguntar.

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>LA CONTRACARA (y la fuente de casi todos los bugs)</strong></p>
<p>Si el mozo se sienta a pelar papas, <strong>nadie más es atendido</strong>.</p>
<p>Ese es el precio del modelo. Si el único hilo se queda haciendo algo que no cede el control, no se demora una petición: <strong>se demoran todas</strong>.</p>
<p>Este módulo te lo va a repetir hasta el cansancio porque es el origen de casi todos los errores de un backend asincrónico mal escrito.</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

### Y el GIL de Python, que acá juega a favor

Python tiene un bloqueo global —el GIL— que impide que dos hilos ejecuten instrucciones de Python al mismo tiempo. Para trabajo de procesador eso es una limitación real y molesta.

**Para trabajo de espera no molesta en absoluto, porque el bloqueo se libera mientras se espera.** Y un servidor web hace, sobre todo, trabajo de espera. O sea: el modelo asincrónico aprovecha exactamente lo que Python puede ofrecer, en lugar de pelearse con lo que no.

<img src="media/image1.png" style="width:5.79167in;height:5.5in" />

**Figura 1.1** *— Del proceso por petición al bucle de eventos: las tres respuestas históricas, y por qué ganó la tercera.*

### Las cuatro decisiones que salen de acá

| **Decisión**                                   | **Qué significa**                                                                                                                                                                            |
|------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Un solo hilo multiplexando espera              | La base del modelo asincrónico. Su contracara es que **nada puede bloquear**.                                                                                                                |
| El contrato es código, no un documento aparte  | El framework genera la especificación de la API a partir de las anotaciones de tipo del propio código. Una especificación escrita aparte se desactualiza; una derivada del código, no puede. |
| Las dependencias se declaran, no se construyen | Es la actividad 8 convertida en mecanismo del framework.                                                                                                                                     |
| Las capas tienen una dirección                 | El TPI la declara explícitamente y el resto del módulo la respeta sin excepción.                                                                                                             |

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>PARA EL PIZARRÓN</strong></p>
<p>Un servidor pasa casi todo su tiempo esperando, no calculando.</p>
<p>Si te acordás de eso, el resto se deduce solo:</p>
<ul>
<li><p><strong>¿Por qué asincrónico y no hilos?</strong> Porque esperar no necesita un hilo entero para cada espera.</p></li>
<li><p><strong>¿Por qué el GIL no molesta acá?</strong> Porque se libera justo mientras esperás.</p></li>
<li><p><strong>¿Por qué bcrypt es un problema?</strong> Porque bcrypt <strong>no espera: calcula</strong>. Es la excepción a todo lo anterior, y por eso el TPI le dedica una sección entera (5.5).</p></li>
</ul>
<p>Todo el modelo se apoya en esa suposición. Donde la suposición no vale, el modelo se rompe.</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

# 1.3 — De WSGI a ASGI: por qué hizo falta un contrato nuevo

### Qué dice

Python necesitó definir cómo se hablan un servidor y una aplicación. WSGI (2003) resolvió eso con un contrato sincrónico que, por su propia forma, no podía expresar ni asincronía ni conexiones largas. ASGI (2016) cambió el contrato.

### En criollo: el enchufe

Un contrato es un enchufe. Si cada framework inventara su propio enchufe, sólo andaría con su propio servidor y no podrías cambiar ninguna de las dos puntas. Por eso Python normó uno.

**WSGI es el teléfono fijo.** Llamás, hablás, cortás. Una petición, una respuesta, se terminó. El contrato dice: la aplicación es un objeto invocable que recibe un diccionario con el entorno de la petición y una función para empezar la respuesta, y devuelve un iterable de bytes. Notablemente simple.

Y tiene un límite estructural —ojo, **no es un descuido de sus autores, es una consecuencia inevitable de su forma**—: el contrato es sincrónico. La aplicación se llama, hace su trabajo, y devuelve. Mientras tanto, quien la llamó está bloqueado. **No hay ningún lugar en ese contrato donde la aplicación pueda decir «esto va a tardar, seguí atendiendo a otro y volvé después».** No es que no lo hayan implementado: no hay dónde escribirlo.

El segundo límite: WSGI modela una petición y una respuesta. No tiene forma de expresar una conversación que queda abierta e intercambia mensajes. No puede describir WebSockets ni el flujo de eventos que el TPI usa en su sección 11.

**ASGI es el WhatsApp.** Apareció alrededor de 2016, empujado por Andrew Godwin en el contexto de Django Channels, y resolvió las dos cosas: la aplicación pasa a ser una **corrutina** que recibe tres cosas —el ámbito de la conexión, una función para recibir mensajes y una función para enviarlos—.

| **Aspecto**       | **WSGI (2003)**                | **ASGI (2016)**                    |
|-------------------|--------------------------------|------------------------------------|
| La aplicación es  | Un invocable común             | Una corrutina                      |
| Modelo            | Una petición, una respuesta    | Un flujo de mensajes               |
| Conexiones largas | No las contempla               | WebSockets y eventos del servidor  |
| Concurrencia      | Del servidor: procesos o hilos | De la aplicación: bucle de eventos |

**La última fila es la que más consecuencias tiene.** Con WSGI la concurrencia era problema del servidor: vos escribías la aplicación como si atendiera a uno solo, y el servidor la corría en varios hilos. Con ASGI la concurrencia pasa a ser **problema tuyo**. Podés hacerlo mucho mejor... y también podés arruinarlo con una sola línea bloqueante.

De ahí sale la primera regla de ejecución asincrónica del TPI, que la clase 3 desarrolla entera pero conviene enunciar ya:

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>EA-01</strong></p>
<p>Todos los handlers de FastAPI se declaran con async def; no hay ningún handler con def.</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>CUIDADO CON UNA CONFUSIÓN MUY COMÚN</strong></p>
<p><strong>ASGI no reemplazó a WSGI, y WSGI no está «viejo».</strong></p>
<p>Si estás escribiendo un sistema donde cada petición hace una consulta y devuelve, con tráfico moderado, WSGI y un puñado de hilos anda perfecto y es más simple de razonar. Muchísimos sistemas en producción funcionan así hoy y están bien.</p>
<p>ASGI resuelve dos cosas que WSGI no puede expresar: conexiones que quedan abiertas intercambiando mensajes, y concurrencia manejada por la aplicación. El TPI necesita las dos: necesita el flujo de eventos de la sección 11 —que es una conexión abierta durante minutos— y necesita atender muchas de esas conexiones a la vez sin gastar un hilo en cada una.</p>
<p>O sea: <strong>el TPI no eligió ASGI porque sea lo nuevo. Lo eligió porque lo que pide no se puede hacer con lo otro.</strong> Esa es siempre la pregunta correcta cuando elegís una tecnología.</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

# 1.4 — Qué hay abajo del framework

### Qué dice

Antes de usar el framework conviene ver qué hay debajo. Después todo lo demás se entiende como comodidad y no como magia. Esta es una aplicación ASGI completa, sin ninguna dependencia:

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p>async def app(scope, receive, send):</p>
<p>assert scope["type"] == "http"</p>
<p>await send({</p>
<p>"type": "http.response.start",</p>
<p>"status": 200,</p>
<p>"headers": [(b"content-type", b"application/json")],</p>
<p>})</p>
<p>await send({</p>
<p>"type": "http.response.body",</p>
<p>"body": b'{"estado": "ok"}',</p>
<p>})</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

### En criollo: el sobre y los dos buzones

Pensalo como correspondencia. scope es el **sobre**: dice de dónde viene, a quién va, qué tipo de envío es. receive es el **buzón de entrada**: de ahí sacás lo que el cliente te manda. send es el **buzón de salida**: ahí ponés lo que le devolvés.

| **Parte**           | **Qué es**                  | **Contiene**                             |
|---------------------|-----------------------------|------------------------------------------|
| scope               | El contexto de la conexión  | Tipo, método, ruta, encabezados, cliente |
| receive             | Corrutina para recibir      | Los mensajes del cliente, como el cuerpo |
| send                | Corrutina para enviar       | Los mensajes hacia el cliente            |
| http.response.start | Primer mensaje de respuesta | Código de estado y encabezados           |
| http.response.body  | Segundo mensaje             | El cuerpo, que puede venir en varios     |

**Fijate que la respuesta se manda en dos mensajes separados, y eso no es un capricho.** Primero mandás los encabezados —«ahí va un paquete, es JSON, salió todo bien»— y después el contenido. Esa separación es exactamente lo que hace posible el flujo de eventos de la sección 11 del TPI: mandás el primer mensaje, y después vas mandando cuerpos a medida que tengas algo para mandar, **sin cerrar la conexión**. Es la diferencia entre entregar un paquete y dejar un canal abierto.

Y observá dos detalles del código que no son decorativos: la función es una **corrutina** y los envíos llevan await. **Cada await es un punto donde el mozo puede irse a atender otra mesa.** Un servidor ASGI que corre cien de estas aplicaciones a la vez lo hace en un solo hilo, alternando justo en esos puntos.

Ahora bien: escribir aplicaciones así sería insostenible. Habría que parsear rutas a mano, validar cuerpos a mano, serializar respuestas a mano. Sobre ese contrato se construyeron herramientas, y el TPI declara una de ellas —publicada en 2018, construida a su vez sobre una capa ASGI de bajo nivel y sobre una biblioteca de validación por anotaciones de tipo—. Esa combinación es la que permite la segunda decisión de diseño: **el contrato es código**.

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>PARA EL PIZARRÓN</strong></p>
<p>Todo lo que el framework hace, lo podrías hacer vos a mano sobre estas diez líneas. <strong>No hay magia: hay comodidad.</strong></p>
<p>Vale la pena escribir esta aplicación una vez en la vida, aunque nunca más la uses. Después, cuando el framework hace algo raro, sabés dónde mirar.</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

# 1.5 — El primer endpoint

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p>from fastapi import FastAPI</p>
<p>app = FastAPI(title="Food Store API", version="1.0.0")</p>
<p>@app.get("/health/live")</p>
<p>async def salud_del_proceso() -&gt; dict[str, str]:</p>
<p>return {"estado": "vivo"}</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

Tres líneas de contenido, y cada una merece explicación.

### 1) El decorador declara método y ruta

@app.get("/health/live") es lo que reemplaza todo el parseo manual de scope\["path"\] y scope\["method"\] que viste en la sección anterior. Es el **cartel en la puerta**: quien venga con un GET a esa dirección, entra acá.

### 2) async def no es opcional en este proyecto: es EA-01

Y conviene entender por qué existe la regla, porque el framework **sí admite** handlers sincrónicos: si declarás uno con def, lo ejecuta en un hilo aparte para no bloquear el bucle. Parece una comodidad, y es una trampa.

### 3) La anotación de retorno no es documentación

-\> dict\[str, str\] no está ahí para que vos leas. El framework la usa para **serializar la respuesta** y para **generar la especificación** de la sección 1.7. Un tipo mal declarado produce una especificación que miente, y el frontend —que esta misma semana está aprendiendo a leer esa especificación— va a escribir su cliente contra la mentira.

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>OJO ACÁ: la trampa del handler mezclado</strong></p>
<p>El framework te deja escribir un handler con def común. Y no falla: lo detecta y lo manda a un hilo aparte. Funciona. Entonces, ¿por qué el TPI lo prohíbe? <strong>Por lo que pasa en el medio:</strong></p>
<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p>@app.get("/productos")</p>
<p>async def listar(): # asincrónico...</p>
<p>datos = requests.get(URL) # ...y adentro, una llamada BLOQUEANTE</p>
<p>return datos.json()</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>
<p>Ese código <strong>no lo manda a ningún hilo</strong>. Es async, así que el framework confía en que vos sabés lo que hacés, y esa línea <strong>congela el bucle de eventos entero</strong> el tiempo que tarde la respuesta. Todos los demás usuarios esperan.</p>
<p>Volvé al restaurante: el mozo dijo «ya voy» y se metió en la cocina a pelar papas. Nadie lo puede reemplazar porque todos creen que está trabajando.</p>
<p>Por eso el TPI dice que <strong>la mezcla es peor que cualquiera de las dos formas puras</strong>: un handler sincrónico completo al menos va a un hilo. Uno asincrónico con una línea bloqueante adentro tiene <strong>la pinta de estar bien y el comportamiento de estar mal</strong>. La clase 3 le dedica el capítulo entero a esto.</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

### Los parámetros: de dónde los saca

Los parámetros se declaran como parámetros de la función, y el framework deduce de dónde sacarlos:

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p>@app.get("/productos/{producto_id}")</p>
<p>async def obtener_producto(</p>
<p>producto_id: int, # de la ruta: aparece en el path</p>
<p>incluir_ingredientes: bool = False, # de la consulta: no aparece en el path</p>
<p>) -&gt; ProductoResponse:</p>
<p>...</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

**La regla es de una sola línea:** si el nombre del parámetro aparece en la ruta declarada, viene de la ruta; si no aparece, viene de la cadena de consulta (el ?algo=valor). Y en los dos casos el tipo se valida: pedir /productos/abc con producto_id: int devuelve un **422** sin que vos hayas escrito una sola línea de validación.

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>LA IDEA CENTRAL DEL FRAMEWORK, y conviene verla ahora</strong></p>
<p><strong>Las anotaciones de tipo dejaron de ser documentación y pasaron a ser comportamiento.</strong></p>
<p>En las actividades de POO, un def sumar(a: int, b: int) -&gt; int era una ayuda para vos y para el editor. Python no verificaba nada: le pasabas dos strings y se las arreglaba como podía.</p>
<p>Acá el mismo producto_id: int hace <strong>tres cosas reales</strong>: valida la entrada, convierte el texto de la URL a entero, y documenta el endpoint en la especificación. Un solo lugar, tres efectos.</p>
<p>Y ojo con la contracara, que es de las que más tiempo hacen perder: <strong>si el tipo está mal, las tres cosas están mal a la vez.</strong> Declarás total: float en vez de Decimal y no sólo guardás mal el número: también le decís al frontend, en la especificación, que espere un número de punto flotante. Y el frontend te va a creer.</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

<img src="media/image2.png" style="width:5.79167in;height:7.32292in" />

**Figura 1.2** *— El recorrido de una petición del lado del servidor: dónde valida, dónde cede el control y dónde se limpia.*

# 1.6 — El cuerpo de la petición

### Qué dice

Para lo que viaja en el cuerpo de la petición, el parámetro se declara con un modelo de Pydantic:

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p>from pydantic import BaseModel, Field</p>
<p>class ProductoCreate(BaseModel):</p>
<p>nombre: str = Field(min_length=1, max_length=120)</p>
<p>precio: Decimal = Field(gt=0, max_digits=10, decimal_places=2)</p>
<p>categoria_id: int</p>
<p>@app.post("/productos", status_code=201)</p>
<p>async def crear_producto(datos: ProductoCreate) -&gt; ProductoResponse:</p>
<p>...</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

### En criollo: el guardia en la puerta

El framework lee el cuerpo, lo parsea, lo valida contra el modelo, y si algo no cumple devuelve un **422 con el detalle de qué campo falló y por qué**. El handler recibe un objeto ya validado, y por lo tanto **no tiene que verificar nada sobre su forma**.

Es el guardia de seguridad en la entrada del boliche. Adentro nadie vuelve a pedir documento, porque si estás adentro es porque pasaste. Toda la lógica del handler puede confiar en que los datos están bien.

Este es el tema completo de la clase 2, que es la que sigue, y el mecanismo que la sección 7 del TPI especifica endpoint por endpoint. Por ahora, **tres cosas para retener**:

1.  **La validación es declarativa.** Las restricciones se enuncian en el modelo, no se programan en el handler. Decís «esto tiene que ser mayor que cero», no escribís el if.

2.  **La validación ocurre antes de que el handler corra.** Adentro del handler los datos ya son confiables.

3.  **El modelo de entrada no es el mismo que el modelo de la tabla.** La clase 4 estudia el segundo, y confundirlos es uno de los errores clásicos que la clase 2 documenta.

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>El detalle del Decimal, que parece menor y no lo es</strong></p>
<p>Fijate que el precio se declara Decimal y no float. Es la decisión que el módulo de frontend estudia como <strong>RN-F08</strong> desde el otro lado: el importe se guarda con un tipo decimal exacto y <strong>viaja como cadena</strong> para que el cliente no lo convierta a punto flotante.</p>
<p>La razón es vieja y conocida: en punto flotante, 0.1 + 0.2 no da 0.3. Con plata eso no es una curiosidad académica: es una diferencia de centavos que se acumula y que después alguien tiene que explicar en una auditoría.</p>
<p>Acá estás viendo <strong>la mitad de arriba</strong> de esa regla. La mitad de abajo la están viendo tus compañeros de frontend esta misma semana.</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

# 1.7 — La documentación que no se puede desactualizar

### Qué dice

Como los tipos, las rutas y los modelos están declarados en el código, la especificación de la API se puede generar a partir de él. Y eso es exactamente lo que pasa: levantás el proyecto y ya tenés una especificación en formato **OpenAPI**, más dos interfaces navegables que la presentan. Una de ellas además te deja **ejecutar los endpoints desde el navegador**, cargando los parámetros a mano.

### En criollo: el manual que escribe la fábrica

Hay dos formas de tener el manual de un producto. Una es que alguien lo escriba mirando el producto. La otra es que la máquina que fabrica el producto escupa el manual como parte del proceso.

La primera se desactualiza el día que alguien cambia una pieza y se olvida de avisar. La segunda **no puede** desactualizarse, porque no existe separada del producto.

Y acá está por qué esto importa mucho más de lo que parece, y no es por comodidad:

El TPI especifica **setenta endpoints** en su sección 6, y **dos equipos trabajan contra esa especificación al mismo tiempo**. Una especificación escrita a mano se desactualiza el día que alguien cambia un campo y se olvida de actualizarla, y a partir de ese momento **miente sin avisar**. El frontend implementa contra un documento que ya no describe al servidor, y el error aparece en integración —que es el momento en que corregirlo cuesta diez veces más—.

Una especificación derivada del código no puede desactualizarse. **Eso no es una comodidad: es la eliminación de una clase entera de errores.**

<img src="media/image3.png" style="width:5.79167in;height:4.14583in" />

**Figura 1.5** *— La documentación automática: del código al contrato, y la ejecución de un endpoint sin escribir un cliente.*

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>EXPERIMENTO — hacelo en la primera clase</strong></p>
<p>Es el que mejor muestra de qué se trata este framework. Cinco pasos:</p>
<ul>
<li><p><strong>Uno.</strong> Levantá el proyecto con un endpoint que reciba un producto_id: int.</p></li>
<li><p><strong>Dos.</strong> Abrí la documentación interactiva en el navegador y ejecutá el endpoint desde ahí. Anda: <strong>no hiciste ningún cliente</strong>.</p></li>
<li><p><strong>Tres.</strong> Probá mandarle abc donde va el entero. Mirá el 422 y leé el cuerpo del error: te dice qué campo, qué esperaba y qué recibió.</p></li>
<li><p><strong>Cuatro.</strong> Volvé al código, cambiá el tipo de retorno del handler, recargá la documentación. <strong>Cambió sola.</strong> No tocaste ningún archivo de documentación, porque no hay ninguno.</p></li>
<li><p><strong>Cinco, y es el que importa.</strong> Pedile la especificación en crudo —el JSON de OpenAPI— y mirá lo que tiene adentro.</p></li>
</ul>
<p>Ese archivo <strong>es el contrato</strong>. Es lo que la sección 6 del TPI describe en tablas, y es lo que tus compañeros de frontend van a leer para escribir su cliente. <strong>Si tu tipo está mal, ese archivo miente, y ellos no tienen forma de saberlo.</strong></p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

# 1.8 — Inyección de dependencias: acá se cobra la actividad 8

### El problema, primero

Un endpoint casi nunca trabaja solo: necesita una sesión de base de datos, el usuario autenticado, tal vez un cliente de caché. La forma directa es construir todo eso adentro del handler:

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p>@app.get("/pedidos/{pedido_id}")</p>
<p>async def obtener_pedido(pedido_id: int):</p>
<p>session = AsyncSession(engine) # el handler construye lo que necesita</p>
<p>uow = UnitOfWork(session)</p>
<p>...</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

Eso funciona. Y tiene **exactamente los tres problemas** que la actividad 8 nombró como propios de la dependencia de creación:

1.  **No se puede sustituir.** Para probar ese handler necesitás una base de datos real, porque la sesión se construye adentro y no hay forma de darle otra cosa.

2.  **Se repite.** Los setenta endpoints del TPI necesitan lo mismo, así que las mismas líneas aparecen setenta veces. Y el día que cambia la forma de construir la sesión, hay que tocar setenta lugares.

3.  **Nadie limpia.** Esa sesión hay que cerrarla. Si el handler falla en el medio, no se cierra.

### La solución: el handler no construye, recibe

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p>async def get_session() -&gt; AsyncGenerator[AsyncSession, None]:</p>
<p>async with async_session_maker() as session:</p>
<p>yield session # lo de arriba es preparación</p>
<p>async def get_uow(session: AsyncSession = Depends(get_session)) -&gt; UnitOfWork:</p>
<p>return UnitOfWork(session)</p>
<p>@app.get("/pedidos/{pedido_id}")</p>
<p>async def obtener_pedido(</p>
<p>pedido_id: int,</p>
<p>uow: UnitOfWork = Depends(get_uow), # lo recibe, no lo construye</p>
<p>) -&gt; PedidoResponse:</p>
<p>return await PedidoService.obtener(uow, pedido_id)</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

### Las cuatro propiedades del mecanismo, y qué resuelve cada una

| **Propiedad**                  | **Qué resuelve**                                                                                                                                                                                                     |
|--------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Se resuelve por la firma**   | El framework mira los parámetros, ve los Depends, y arma el orden de resolución solo. Vos no escribís el armado.                                                                                                     |
| **Las dependencias se anidan** | get_uow depende de get_session, y se declara igual que en el handler. Se forma un grafo que se resuelve de abajo hacia arriba.                                                                                       |
| **Se cachean por petición**    | Si tres dependencias distintas piden la sesión, se construye **una sola vez** y se comparte. Esto **no es una optimización**: es lo que garantiza que las tres trabajen en la misma transacción. Tema de la clase 6. |
| **Se limpian solas**           | Una dependencia declarada con yield ejecuta lo de arriba antes del handler y lo de abajo después de que la respuesta salió, **incluso si el handler lanzó una excepción**.                                           |

Y con eso llegamos a la regla del TPI que abrió el capítulo: **el Router recibe el Unit of Work y lo transporta al Service. No lo construye, no lo abre, no lo usa.**

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>PARA EL PIZARRÓN: es lo mismo que ya sabías</strong></p>
<p>En la actividad 8 la conclusión fue que un servicio que <strong>recibe</strong> su repositorio se puede probar con un repositorio falso, y uno que <strong>lo construye adentro</strong> no.</p>
<p>Depends() es eso mismo, resuelto por el framework. <strong>Vos declarás qué necesitás; alguien más decide qué darte.</strong> En producción te da la sesión real; en un test le decís que te dé otra cosa, sin tocar una línea del handler.</p>
<p>Lo único que cambió es <strong>quién arma el objeto</strong>. El principio es idéntico al que ya viste, y por eso esta clase te va a resultar más fácil de lo que debería: <strong>ya sabías la parte difícil</strong>.</p>
<p>La analogía de cocina: un chef que sale a comprar los tomates no se puede probar sin verdulería. Un chef que recibe los tomates del proveedor se prueba con tomates de plástico.</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

# 1.9 — Recursos y ciclo de vida

### Qué dice

Hay recursos que **no** se crean por petición: el pool de conexiones a la base, el cliente de Redis, el broker de la cola. Crearlos en cada petición sería absurdo, porque el costo de establecer una conexión es justamente lo que un pool existe para evitar.

En criollo: **no comprás una heladera nueva cada vez que querés un vaso de agua.** La heladera se compra una vez, se enchufa cuando abre el local, y se apaga cuando cierra.

Eso es el **lifespan**: se crean una vez al arrancar la aplicación y se cierran una vez al terminar.

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p>@asynccontextmanager</p>
<p>async def lifespan(app: FastAPI):</p>
<p>app.state.engine = create_async_engine(settings.DATABASE_URL)</p>
<p>app.state.redis = redis.from_url(settings.REDIS_URL)</p>
<p>yield # acá vive la aplicación</p>
<p>await app.state.redis.aclose()</p>
<p>await app.state.engine.dispose()</p>
<p>app = FastAPI(lifespan=lifespan)</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>EA-08</strong></p>
<p>El pool de conexiones y el cliente de Redis se crean en el lifespan de la aplicación y se cierran ahí. <strong>No se crean por petición ni a nivel de módulo.</strong></p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

Y hay una consecuencia práctica que el TPI declara en su stack: como esos recursos se crean en el ciclo de vida, **la suite de tests tiene que dispararlo**. Por eso el stack incluye una herramienta específica para eso. Si tus tests no arrancan el lifespan, no hay engine, y nada anda.

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>OJO ACÁ: el peor error del capítulo</strong></p>
<p>La prohibición de crearlos «a nivel de módulo» merece comentario aparte, porque <strong>es el error que más se comete y el que peor se diagnostica</strong>.</p>
<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p># arriba de todo del archivo, fuera de cualquier función</p>
<p>redis_client = redis.from_url(REDIS_URL) # se ejecuta al IMPORTAR</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>
<p>Eso corre <strong>cuando Python lee el archivo</strong>, que es antes de que exista un bucle de eventos. A veces anda igual. A veces te tira un error críptico sobre bucles distintos. Y a veces —lo peor de todo— <strong>anda al levantar el servidor y falla en los tests</strong>, o al revés.</p>
<p>Y ahí empieza la búsqueda en el lugar equivocado: mirás el test, mirás la configuración del test, mirás la fixture. <strong>El problema está en una línea de un archivo que ni abriste, que se ejecutó sola cuando alguien lo importó.</strong></p>
<p>Por eso EA-08 no dice «conviene». Dice <strong>no se crean por petición ni a nivel de módulo</strong>. Van en el lifespan, y punto.</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

# 1.10 — Las capas: lo que hay que llevarse de esta clase

Si de todo el capítulo te tenés que llevar algo para las siete clases que siguen, es esto. El TPI declara en su sección 2.1 un flujo de dependencias estricto:

**Router → Service → UoW → Repository → Model**

**Ninguna capa puede importar la capa superior.**

En criollo, es la cadena de mando de una cocina. El **mozo** habla con el **chef**; el chef trabaja sobre una **comanda** abierta; la comanda usa el **depósito**; el depósito toca la **mercadería**. Y la flecha va para un solo lado: **la mercadería no le da órdenes al mozo.**

<img src="media/image4.png" style="width:5.79167in;height:5.33333in" />

**Figura 1.3** *— Las capas y la dirección de las dependencias: Task entra por el costado, los puertos salen por el otro.*

| **Capa**     | **Archivo**   | **Responsabilidad**                                                                                                            | **Conoce a**                 |
|--------------|---------------|--------------------------------------------------------------------------------------------------------------------------------|------------------------------|
| Router       | router.py     | HTTP puro: parsea, valida el schema, resuelve dependencias, delega y serializa. **No traduce excepciones**                     | Service y el tipo UnitOfWork |
| Task         | tasks.py      | Punto de entrada del worker. Resuelve su UoW, invoca al Service. **Sin lógica propia**                                         | Service y UnitOfWork         |
| Service      | service.py    | La lógica de negocio. Sin estado y asincrónico. Recibe UoW y actor por parámetro. Lanza excepciones de dominio, **nunca HTTP** | UoW y los puertos            |
| Unit of Work | core/uow.py   | La transacción: sesión, repositorios, commit o rollback al salir. **No cierra la sesión**                                      | Repository y sesión          |
| Repository   | repository.py | Acceso a datos, sin lógica de negocio, todo con await. Declara la precarga de relaciones                                       | Model y sesión               |
| Model        | model.py      | Tablas y relaciones. **Sin imports de capas superiores**                                                                       | Nada de arriba               |

Tres observaciones sobre esa tabla, porque cada una es **una decisión** y no una descripción.

### 1) El Router no traduce excepciones

No hay try/except que convierta un error de dominio en un código HTTP. De eso se ocupa **un manejador global**, que la clase 8 estudia. La razón es la de siempre: si cada router traduce, hay setenta traducciones, y **basta con que una difiera** para que el mismo error devuelva un 404 en un endpoint y un 500 en otro. Nadie va a entender por qué.

### 2) El Service es asincrónico, sin estado, y recibe el actor por parámetro

No hay un «usuario actual» guardado en ningún lado. **Quien llama dice de parte de quién llama.** Eso es lo que permite que la misma función la invoque un Router y una tarea del worker.

### 3) La capa Task no es una capa

El TPI es explícito: **es un cliente de Service, igual que el Router.** Una tarea resuelve su propio Unit of Work y llama al mismo Service. Y da la razón: si existiera lógica que vive sólo en una tarea, no se podría ejercitar desde la API ni probar sin levantar un worker.

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>PARA ENTENDER: el Service no sabe quién lo llamó</strong></p>
<p>De toda esa tabla, esta es la fila que explica cómo está pensado el sistema entero.</p>
<p>El Service recibe el Unit of Work y recibe el actor, <strong>los dos por parámetro</strong>. No busca el usuario en ningún lado, no toca la petición HTTP, <strong>no sabe si hay una petición</strong>.</p>
<p>¿Y qué gana con eso? Tres cosas concretas:</p>
<ul>
<li><p>Lo puede llamar <strong>un Router</strong>, cuando alguien pide algo por HTTP.</p></li>
<li><p>Lo puede llamar <strong>una tarea del worker</strong>, donde no hay ninguna petición.</p></li>
<li><p>Lo podés llamar <strong>vos, en un test</strong>, sin levantar el servidor.</p></li>
</ul>
<p>Fijate la diferencia con la alternativa. Si el Service leyera el usuario de la petición, sólo lo podría llamar un Router. Y entonces la lógica de avanzar un pedido tendría que estar escrita <strong>dos veces</strong>: una para cuando lo hace una persona, y otra para cuando lo hace la expiración automática.</p>
<p><strong>Dos copias de la misma regla de negocio es como empiezan los bugs que nadie entiende.</strong> Una se corrige, la otra no. Y seis meses después alguien pregunta por qué el pedido se comporta distinto según quién lo tocó.</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

# 1.11 — Redis no es una capa: es un adaptador

Esta es la sección más importante del capítulo después de la anterior, y es donde **la actividad 4 —duck typing y Protocol— se cobra entera**.

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>LO QUE DECLARA EL TPI</strong></p>
<p>Redis no es una capa: es un adaptador. El Service <strong>nunca</strong> importa redis.asyncio. Consume dos puertos declarados en core/ports.py —CachePort y EventPort— cuyas implementaciones de Redis viven en core/adapters/.</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

Y —esto es lo que lo convierte en una lección y no en una convención arbitraria— **da la razón**:

La sección 4.3 exige que el sistema **siga funcionando con Redis caído**. Y eso se escribe como una implementación alternativa del puerto —NullCache— que la aplicación instala cuando el healthcheck de Redis falla. Con el cliente importado directamente en el Service, esa degradación se escribiría como un try/except repetido en veinte lugares.

### Desarmemos el razonamiento, porque es exactamente el de la actividad 4

**El requisito es de negocio, no de diseño:** si Redis se cae, el sistema tiene que seguir aceptando pedidos. Nadie pidió puertos. Pidieron seguir vendiendo.

**Sin puerto**, cumplir ese requisito significa rodear cada uso de Redis con un try/except que decida qué hacer si falla. Veinte usos, veinte bloques, **veinte oportunidades de que uno quede mal**.

**Con puerto**, el requisito se cumple **una sola vez**: escribís una implementación que no hace nada —guardar en ella no guarda, leer siempre devuelve vacío— y la instalás en lugar de la real. El Service no se entera. **Ni una línea suya cambia.**

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p>class CachePort(Protocol): # actividad 4: duck typing tipado</p>
<p>async def get(self, clave: str) -&gt; bytes | None: ...</p>
<p>async def set(self, clave: str, valor: bytes, ttl: int) -&gt; None: ...</p>
<p>class RedisCache: # la implementación real</p>
<p>async def get(self, clave): ...</p>
<p>async def set(self, clave, valor, ttl): ...</p>
<p>class NullCache: # la degradación, completa</p>
<p>async def get(self, clave): return None</p>
<p>async def set(self, clave, valor, ttl): return None</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

Fijate en algo: **ninguna de las dos implementaciones declara que implementa el puerto.** No hay un implements en ningún lado. Alcanza con **tener la forma**. Eso es duck typing, y es exactamente lo que la actividad 4 señaló como «el regalo que Java no tiene».

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>PARA EL PIZARRÓN: lo que separa un diseño de una colección de parches</strong></p>
<p>El requisito <strong>no era</strong> «usá puertos». El requisito era <strong>«si Redis se cae, el sistema tiene que seguir vendiendo»</strong>. El puerto es la única forma de cumplirlo sin ensuciar veinte lugares.</p>
<p>Las dos versiones del mismo requisito:</p>
<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p># Sin puerto: esto, repetido en veinte lugares</p>
<p>try:</p>
<p>valor = await redis.get(clave)</p>
<p>except RedisError:</p>
<p>valor = None</p>
<p># Con puerto: esto, una vez, en el arranque</p>
<p>cache = RedisCache(...) if redis_disponible else NullCache()</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>
<p>¿Y qué pasa con la primera versión en la práctica? Que a las dos de la mañana antes de entregar, alguien agrega el uso número veintiuno y se olvida del try. Y eso <strong>no falla en la demo</strong>: falla el día que Redis se cae, <strong>que es justamente el día en que el sistema tenía que seguir andando</strong>.</p>
<p>Es la misma lección que el módulo de frontend saca de sus once reglas: <strong>las reglas que dependen de que alguien se acuerde, fallan.</strong></p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

# 1.12 — Los ocho servicios

El TPI declara en su sección 2.2 que el sistema se despliega como **ocho procesos**, cada uno con su comando, su cardinalidad y —esto es lo interesante— **su comportamiento declarado ante la caída**.

| **Servicio** | **Instancias**          | **Si se cae**                                                          |
|--------------|-------------------------|------------------------------------------------------------------------|
| migrador     | Corre una vez y termina | Ningún otro proceso debe arrancar                                      |
| seed         | Corre una vez y termina | La API arranca sin catálogos y el healthcheck lo detecta               |
| api          | N, tras un balanceador  | Se pierden sus conexiones de eventos; el cliente reconecta             |
| worker       | N                       | La API sigue; se detiene el trabajo diferido y los eventos se acumulan |
| scheduler    | **Exactamente una**     | Deja de encolarse el trabajo periódico                                 |
| web          | N                       | No hay aplicación para el usuario aunque la API atienda                |
| postgres     | Una                     | **El sistema no funciona. No hay degradación posible**                 |
| redis        | Una                     | El sistema **degrada** según la sección 4.3 y sigue siendo correcto    |

<img src="media/image5.png" style="width:5.79167in;height:4.3125in" />

**Figura 1.4** *— Los ocho servicios y su orden de arranque: primero los trabajos, después los procesos, y abajo la infraestructura.*

Tres filas de esa tabla enseñan más que el resto:

### El migrador y el seed son trabajos, no servicios

Corren, terminan, y no vuelven. **Confundir eso lleva a orquestaciones donde el migrador se reinicia en bucle**: el orquestador ve que el proceso terminó, cree que se cayó, lo levanta de nuevo, vuelve a terminar, y así hasta que alguien mira los logs a las tres de la mañana.

### El planificador corre en exactamente una instancia

Y el TPI explica por qué: **dos instancias simultáneas encolan cada tarea dos veces.** De ahí sale la regla **TB-02 —toda tarea debe ser idempotente—**, que la clase 8 desarrolla. Idempotente quiere decir que ejecutarla dos veces da el mismo resultado que ejecutarla una. Si la tarea es «cobrarle al cliente», la diferencia entre idempotente y no idempotente es un reclamo.

### PostgreSQL y Redis fallan distinto, y es a propósito

Si se cae la base, el sistema no funciona y lo dice con un **503**. No hay degradación posible **ni se pretende que la haya**. Si se cae Redis, el sistema sigue siendo correcto, con menos rendimiento y sin tiempo real. Esa asimetría es la que le da sentido a la distinción del TPI entre **«único almacén durable»** y **«almacén efímero»**.

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>PARA EL PIZARRÓN: la pregunta que le tenés que hacer a cada dependencia</strong></p>
<p>Mirá las dos últimas filas juntas, porque dicen algo que vale para cualquier sistema que armes en tu vida:</p>
<p><strong>Cada dependencia tiene declarado qué pasa si se cae. Y no todas responden igual: una tira todo abajo, la otra degrada.</strong></p>
<p>Eso no es un detalle de operaciones, es una <strong>decisión de diseño</strong>. Decidir que Redis puede caerse sin que el sistema deje de vender te obliga a escribir el código de otra manera —con puertos, como viste en 1.11—. Decidir que Postgres no puede caerse te ahorra escribir un montón de código que nunca iba a funcionar bien igual.</p>
<p>La pregunta, con cada dependencia que agregues a cualquier proyecto, es esta: <strong>¿qué pasa si esto no está?</strong> Si no tenés respuesta, todavía no terminaste de diseñar.</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

# 1.13 — Los doce módulos

El TPI organiza el código **por funcionalidad, no por tipo de archivo**. Cada módulo vive en app/modules/\<nombre\>/ y contiene sus propios router.py, service.py, repository.py, model.py y tasks.py.

Los doce: **auth, usuarios, direcciones, categorias, productos, ingredientes, stock, pedidos, catalogos, estadisticas, eventos y operacion.**

Dos de esos módulos merecen mención desde ahora porque son especiales:

- **stock es el dueño del stock**, y expone aplicar_movimiento() como **único camino admitido** para modificarlo. Ningún otro módulo escribe stock directamente. La clase 7 estudia por qué.

- **eventos es el único que publica hacia el canal en tiempo real.** La clase 8 lo desarrolla.

<img src="media/image6.png" style="width:5.79167in;height:4.71875in" />

**Figura 1.6** *— La estructura de un módulo y sus cinco archivos, contra la organización por tipo de archivo.*

Y esa organización es —por si no se notó— **la misma decisión que el módulo de frontend toma en su octava clase con Feature-Sliced Design**: agrupar por dominio y declarar una dirección para las dependencias. Los dos lados del sistema resuelven el mismo problema de la misma manera, con vocabulario distinto.

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>Por qué así y no como en los tutoriales</strong></p>
<p>La alternativa —la que usan casi todos los tutoriales— es organizar por tipo de archivo:</p>
<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p>routers/ productos.py pedidos.py usuarios.py ...</p>
<p>services/ productos.py pedidos.py usuarios.py ...</p>
<p>models/ productos.py pedidos.py usuarios.py ...</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>
<p>Eso anda bien con cinco módulos. <strong>Con doce, cada cambio te obliga a abrir cinco carpetas</strong>, y ninguna te dice cuáles archivos son del mismo módulo.</p>
<p>Con la organización por funcionalidad, todo lo de pedidos vive junto: si querés entender pedidos, <strong>abrís una carpeta</strong>. Si querés borrar un módulo, <strong>borrás una carpeta</strong> y el intérprete te avisa quién lo extrañaba.</p>
<p>Es la diferencia entre una casa ordenada por ambientes y una casa donde todos los cajones de todos los muebles están en la misma habitación.</p>
<p>Y hay algo lindo acá: <strong>tus compañeros de frontend van a llegar a esta misma conclusión en su última clase, por su propio camino y con otro nombre.</strong> Es buena señal cuando dos equipos que resuelven problemas distintos terminan ordenando el código igual.</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

# 1.14 — Herramientas de diagnóstico

Cinco herramientas, de menos a más específica. Las primeras dos se subutilizan siempre.

| **Herramienta**                                  | **Para qué**                                               | **Cuándo**                                                                                                                                                                                      |
|--------------------------------------------------|------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **La documentación interactiva**                 | Ejecutar cualquier endpoint sin escribir un cliente        | Separa «el backend está mal» de «mi cliente está mal» **en diez segundos**                                                                                                                      |
| **La especificación en crudo** (JSON de OpenAPI) | Es el contrato                                             | Cuando el frontend reporta que algo no coincide. **La discusión se resuelve ahí, no por chat**                                                                                                  |
| **Los registros de uvicorn**                     | Método, ruta, código de estado y duración de cada petición | Desde el primer día, para acostumbrarte a distinguir un **422** (validación: el cliente mandó mal) de un **500** (excepción no controlada: el problema es tuyo)                                 |
| **curl y httpx**                                 | Aislar el backend del frontend completo                    | El TPI declara httpx en su stack porque **es también el cliente de los tests**: lo que probás a mano con él es lo mismo que después automatizás                                                 |
| **Seguir un import**                             | Verificar la regla de capas                                | El más útil de este capítulo: si un archivo de una capa importa algo de una capa superior, la regla de 1.10 está rota. **Se ve leyendo la cabecera del archivo**, y en la clase 8 se automatiza |

# 1.15 — Seguridad y evolución

### Tres cosas de seguridad

1.  **La documentación automática expone el contrato completo.** Eso es deseable en desarrollo y discutible en producción: publica qué endpoints existen, qué reciben y qué devuelven. Es información valiosísima **para quien quiera atacar el sistema**. Por eso suele deshabilitarse en producción o exigir autenticación.

2.  **Un mensaje de error puede filtrar más de lo que debería.** Una excepción no controlada que devuelve la traza completa entrega nombres de archivos, rutas y a veces fragmentos de consultas. De ahí que el TPI use un **manejador global** (clase 8).

3.  **Toda validación que importa ocurre en el servidor.** El frontend valida para dar buena experiencia; el servidor valida **porque es el único que puede**. Es exactamente la regla RN-F04 que la otra mitad de la cursada estudia, vista desde acá: sus garantes son tres casos de prueba que le pegan al backend salteándose la interfaz.

### Dos cosas sobre la evolución

**El GIL está siendo revisado.** Hay una modalidad experimental sin él desde Python 3.13. Y sin embargo eso **no cambia nada de este módulo**, porque el modelo asincrónico no se eligió sólo por el GIL, sino por lo que dice la sección 1.2: un servidor pasa su tiempo esperando, y **esperar no necesita un hilo por espera**. El GIL era un argumento adicional, no el argumento.

**El contrato ASGI habilitó cosas que WSGI no podía expresar**, y el TPI usa una de ellas: el flujo de eventos de la sección 11. Detalle interesante: elegir un contrato más expresivo abrió posibilidades **que no eran el objetivo original**. Suele pasar con las buenas abstracciones.

# 1.16 — Verificación: el checklist honesto

Nueve cosas. Si las nueve te salen, la clase la entendiste. Si alguna no, ya sabés qué sección releer.

1.  Escribir una aplicación ASGI **sin framework** que responda un JSON, y nombrar las tres piezas que recibe. \*(1.4)\*

2.  Levantar un proyecto con tres endpoints y verificar que los tres aparecen en la documentación automática. \*(1.7)\*

3.  Provocar un **422** mandando un tipo equivocado en un parámetro de ruta, y leer el cuerpo del error identificando qué campo falló. \*(1.5)\*

4.  Cambiar el tipo de retorno de un handler y verificar que la especificación **cambió sola**. \*(1.7)\*

5.  Escribir una dependencia con yield que registre en consola antes y después, y verificar el orden respecto de la respuesta. \*(1.8)\*

6.  Declarar una dependencia usada por otras dos y comprobar que **se construye una sola vez** por petición. \*(1.8)\*

7.  Ubicar cinco archivos del backend del TPI en su capa y justificar qué puede importar cada uno. \*(1.10)\*

8.  Explicar por qué el Router **no** traduce excepciones y quién lo hace. \*(1.10)\*

9.  Escribir un puerto con Protocol y dos implementaciones, y cambiar de una a otra **sin tocar el código que lo consume**. \*(1.11)\*

# 1.17 — Los nueve errores frecuentes

Todos estos errores tienen algo en común: **el código funciona**. Por eso son frecuentes.

| **El error**                                               | **Por qué es un error**                                                                                                            | **Sección** |
|------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------|-------------|
| Declarar un handler con def en lugar de async def          | Funciona —el framework lo manda a un hilo— y viola EA-01. **La mezcla es peor que cualquiera de las dos formas puras**             | 1.5         |
| Construir la sesión dentro del handler                     | Es dependencia de creación: no se puede sustituir en un test, se repite en cada endpoint y **nadie la cierra**                     | 1.8         |
| Crear el cliente de Redis o el motor **a nivel de módulo** | Se construyen al importar, cuando puede no haber bucle de eventos. Viola EA-08 y produce **fallos que aparecen sólo en los tests** | 1.9         |
| Importar redis.asyncio desde un Service                    | Impide la degradación de la sección 4.3 sin repetir manejo de errores en veinte lugares                                            | 1.11        |
| Traducir excepciones en el Router                          | **Produce setenta traducciones donde debería haber una**                                                                           | 1.10        |
| Poner lógica de negocio en una tarea                       | No se puede ejercitar desde la API ni probar sin worker                                                                            | 1.10        |
| Confundir el modelo de entrada con el modelo de la tabla   | Son cosas distintas, y usar el segundo como schema **expone campos que no deberían viajar**                                        | 1.6         |
| Declarar mal un tipo de retorno                            | Rompe **tres cosas a la vez**: la validación, la serialización y la especificación que el frontend va a leer                       | 1.5         |
| Tratar al migrador como un servicio de larga vida          | Corre una vez y termina; si se lo reinicia en bucle, **la orquestación nunca converge**                                            | 1.12        |

# 1.18 — Las actividades, y qué busca cada una

Siete actividades. Debajo de cada una está lo que en realidad quiere que descubras.

### 1. ASGI a mano

Escribir una aplicación ASGI sin dependencias que responda dos rutas distintas parseando scope\["path"\], documentar cuánto código hizo falta, reescribirla con el framework y comparar.

***Qué busca:** que el framework deje de ser magia. Después de esto sabés exactamente qué te está ahorrando.*

### 2. El contrato es código

Implementar tres endpoints del módulo catalogos con sus tipos correctos, exportar la especificación de OpenAPI y compararla con la tabla de la sección 6.10 del TPI, **campo por campo**.

***Qué busca:** que veas con tus ojos que el JSON generado y la tabla del TPI son el mismo objeto. Y que si difieren, el que está mal sos vos.*

### 3. Creación contra uso

Escribir un endpoint que construya su propia sesión y otro que la reciba por Depends. Escribir un test para cada uno y documentar qué hizo falta en cada caso. Relacionar con la actividad 8 de POO.

***Qué busca:** que sufras el primer test. Ahí entendés Depends() para siempre.*

### 4. El grafo de dependencias

Declarar una cadena de tres dependencias anidadas donde la última es usada por dos, agregar registros en consola, y documentar el orden de construcción y de limpieza, y cuántas veces se construyó cada una.

***Qué busca:** ver el caché por petición funcionando. Es lo que garantiza la transacción única de la clase 6.*

### 5. El puerto y su alternativa

Implementar CachePort como Protocol con dos implementaciones —una real y una que no hace nada—, y un servicio que la consuma. Demostrar que el servicio funciona con las dos **sin ningún cambio**, y relacionar con la sección 4.3 del TPI.

***Qué busca:** la actividad 4 con consecuencias de negocio.*

### 6. Exploración: las capas auditadas

Tomar la tabla de la sección 1.10 y, sobre un proyecto propio o de ejemplo, revisar **las cabeceras de import de cada archivo** buscando violaciones de la regla de dependencias. Documentar cada una y proponer cómo se corrige.

***Qué busca:** que descubras que auditar una arquitectura es leer las diez primeras líneas de cada archivo. Nada más que eso.*

### 7. Exploración: los dos lados de la misma petición

Junto con alguien del turno de frontend, tomar un endpoint concreto de la sección 6 del TPI. Implementarlo de este lado y consumirlo del otro. Documentar **qué información hizo falta que no estaba en la tabla**, y proponer cómo la especificación de OpenAPI la habría aportado.

***Qué busca:** que descubras en carne propia el hueco entre una tabla escrita a mano y un contrato generado. Requiere coordinar con la otra mitad de la cursada.*

# 1.19 — Síntesis: las once frases

Si tuvieras que resumir el capítulo en una hoja, es esta.

1.  Un servidor web pasa la mayor parte del tiempo **esperando, no calculando**. De ahí salen las tres respuestas históricas al problema de atender a muchos, y por qué ganó el bucle de eventos.

2.  El modelo de un proceso o un hilo por conexión **no escala**: el problema tuvo nombre propio en 1999 —C10K— y la salida fue un solo hilo que multiplexa esperas.

3.  El GIL **no impide** ese modelo: se libera mientras se espera, y esperar es lo que un servidor hace casi siempre.

4.  WSGI no podía expresar asincronía ni conexiones largas **por la forma de su contrato, no por descuido**. ASGI cambió el contrato: la aplicación es una corrutina, y la concurrencia pasó a ser problema de la aplicación.

5.  Las anotaciones de tipo dejaron de ser documentación y pasaron a ser **comportamiento**: validan, convierten y documentan. Un tipo mal declarado rompe las tres cosas a la vez.

6.  Una especificación **derivada del código no puede desactualizarse**, y eso elimina una clase entera de errores en un proyecto con dos equipos y setenta endpoints.

7.  Depends() **es la actividad 8**: la diferencia entre construir lo que se necesita y recibirlo. El TPI lo exige explícitamente —el Router no construye el Unit of Work— y de ahí sale que el código sea probable.

8.  Las dependencias se cachean por petición, y eso **no es una optimización**: es lo que garantiza que todo el manejo de una petición ocurra en la misma transacción.

9.  Las capas tienen **una sola dirección**: Router → Service → UoW → Repository → Model. Y la capa Task no es una capa: es otro cliente de Service, porque **ninguna lógica puede vivir donde no se la pueda probar**.

10. Redis no es una capa, es un adaptador. El puerto **no está por elegancia**: es la única forma de cumplir el requisito de degradación sin repetir manejo de errores en veinte lugares. Es la actividad 4 aplicada.

11. Cada dependencia declara **qué pasa si se cae**, y no todas responden igual: una tira el sistema abajo, la otra degrada. Esa asimetría es una decisión de diseño, no un detalle de operaciones.

# 1.20 — Qué leer, y en qué orden

El original lista las fuentes en un párrafo denso. Acá van ordenadas por prioridad real.

### Si leés una sola cosa

**El artículo de Dan Kegel sobre el problema C10K** (1999, actualizado hasta 2014), en kegel.com/c10k.html. Es la mejor fuente sobre el límite del modelo de un hilo por conexión y sobre los mecanismos de multiplexación que lo resolvieron. Está escrito en 1999 y se lee mejor que muchas cosas de ahora.

### Si leés tres

- **La documentación oficial de FastAPI** (fastapi.tiangolo.com) es inusualmente buena para ser documentación de producto. Su tutorial sobre dependencias explica el mecanismo de la sección 1.8 con más ejemplos de los que entran acá.

- **Martin Fowler, \*Inversion of Control Containers and the Dependency Injection Pattern**\* (2004): es el texto donde el patrón quedó nombrado, y conecta directo con la octava actividad de POO.

- **Alistair Cockburn (2005)**, la formulación original de puertos y adaptadores para la sección 1.11. Dato lindo: la otra mitad de la cursada llega al mismo texto por otro camino, al estudiar la arquitectura de su propio lado.

### Las fuentes normativas (para consultar, no para leer de corrido)

- **WSGI**: PEP 333 (2003) y su revisión PEP 3333 (2010). Leerlos muestra con claridad **por qué** un contrato sincrónico no podía extenderse a conexiones largas.

- **ASGI**: asgi.readthedocs.io. Alcanza con la sección de mensajes HTTP para reconocer lo que muestra la sección 1.4.

- **El modelo asincrónico del lenguaje**: PEP 3156 (introdujo asyncio) y PEP 492 (agregó async y await). El piso de versión que fija el TPI se explica por el PEP 654, que introdujo los grupos de excepciones.

- **OpenAPI 3.1**, mantenido por la OpenAPI Initiative: el formato de la especificación que el framework genera.

### Del TPI, tres secciones enteras

- **2.1** — el flujo de dependencias y la responsabilidad de cada capa.

- **2.2** — los ocho servicios y su comportamiento ante la caída.

- **2.3** — los doce módulos.

La **1.4**, que declara las ocho reglas de ejecución asincrónica, es el tema completo de la clase 3 y por ahora sólo se anticipa.

# Cierre: las seis cosas que hay que recordar

Si dentro de un mes te acordás de seis frases de todo esto, que sean estas.

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<thead>
<tr class="header">
<th><p><strong>LAS SEIS</strong></p>
<p><strong>1.</strong> Un servidor <strong>espera</strong>, no calcula. Todo el modelo asincrónico se apoya en eso, y donde la suposición no vale —bcrypt— el modelo se rompe.</p>
<p><strong>2.</strong> Si el único hilo se pone a calcular, <strong>no se demora una petición: se demoran todas</strong>.</p>
<p><strong>3.</strong> Las anotaciones de tipo <strong>son comportamiento</strong>. Un tipo mal puesto rompe la validación, la serialización y el contrato que lee el frontend, las tres juntas.</p>
<p><strong>4.</strong> Depends() es la actividad 8 con otro nombre: <strong>declarás lo que necesitás, no lo construís</strong>. Y por eso se puede probar.</p>
<p><strong>5.</strong> Las capas van para un solo lado: <strong>Router → Service → UoW → Repository → Model</strong>. Se audita leyendo la cabecera de cada archivo.</p>
<p><strong>6.</strong> El puerto no está por elegancia: <strong>es la única forma de cumplir un requisito de negocio sin depender de que veinte personas se acuerden de veinte bloques try.</strong></p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

Y una séptima, que no es del capítulo pero está en todas sus páginas: **cuando algo del diseño parece una convención arbitraria, buscá el requisito que la originó.** El TPI siempre lo dice. Eso es lo que separa aprender una arquitectura de copiarla.
