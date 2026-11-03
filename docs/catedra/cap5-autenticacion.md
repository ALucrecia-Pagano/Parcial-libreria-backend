**CAPÍTULO 5 — GUÍA DE LECTURA**

**Autenticación y autorización**

JWT, RBAC y bcrypt, explicados en criollo

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
<p>Esta clase responde <strong>dos preguntas que suelen tratarse como una sola y no lo son</strong>:</p>
<ul>
<li><p><strong>Autenticación</strong> es establecer <strong>quién es alguien</strong>.</p></li>
<li><p><strong>Autorización</strong> es decidir <strong>qué puede hacer</strong>.</p></li>
</ul>
<p><strong>Un sistema puede saber perfectamente quién sos y negarte todo.</strong> Esa distinción —que del lado del cliente se ve como la diferencia entre un 401 y un 403— acá se convierte en <strong>dos mecanismos separados con reglas propias</strong>.</p>
<p>Y hay una coincidencia de calendario para aprovechar: <strong>esta misma semana la otra mitad de la cursada estudia el token desde el navegador</strong> —dónde guardarlo, por qué ninguna opción es gratis, y por qué las guardas de ruta son usabilidad y no seguridad—.</p>
<p><strong>Las dos clases son las dos mitades de la misma demostración: allá se aprende que el cliente no protege nada; acá se construye lo único que sí protege.</strong></p></td>
</tr>
</tbody>
</table>

5.1 — De qué se trata esta clase

El capítulo cobra **dos reglas de la clase 3 sobre el único caso del sistema donde aparecen**. EA-02 —ninguna operación bloqueante desde una corrutina— y EA-06 —nada de trabajo de procesador sin ceder— existen, en la práctica, **casi exclusivamente por bcrypt**. Y el TPI da el número que lo explica todo:

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p><strong>El número que ordena todo el capítulo</strong></p>
<p>bcrypt con factor de costo 12 consume del orden de <strong>trescientos milisegundos de procesador por verificación</strong>. En un proceso asincrónico, trescientos milisegundos de procesador dentro de una corrutina son trescientos milisegundos en los que el bucle de eventos <strong>no atiende absolutamente nada</strong>: ni el catálogo público, ni las conexiones abiertas, ni el chequeo de salud.</p></td>
</tr>
</tbody>
</table>

Hay además **una decisión de modelado que vale por sí sola** y conviene anticipar porque enseña a pensar: el TPI declara que **SISTEMA no es un rol**, y explica por qué modelarlo como tal habría sido un error. La sección 5.8 lo desarrolla.

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p><strong>PARA EL PIZARRÓN</strong></p>
<p>Al terminar la clase tenés que poder hacer tres cosas:</p>
<ul>
<li><p><strong>Implementar el flujo de autenticación completo.</strong></p></li>
<li><p><strong>Explicar qué garantiza un token firmado y qué no.</strong></p></li>
<li><p><strong>Justificar por qué la autorización consulta la base en cada petición</strong> aunque el token ya traiga los roles.</p></li>
</ul>
<p>La tercera es la que más gente contesta mal, y es la decisión más importante del capítulo.</p></td>
</tr>
</tbody>
</table>

5.2 — Del Basic al token: tres respuestas, tres renuncias

Qué dice

El problema es viejo: **un protocolo sin estado necesita que cada petición diga de parte de quién viene**. Hubo tres respuestas, y **cada una resignó algo distinto**.

| **Las cuatro decisiones de diseño del capítulo**            | **Qué significa**                                                                           |
|-------------------------------------------------------------|---------------------------------------------------------------------------------------------|
| **1. El servidor no guarda sesiones**                       | Cada petición **se basta a sí misma**. Cualquier instancia puede atender cualquier petición |
| **2. La firma garantiza integridad, no confidencialidad**   | **El contenido del token se puede leer.** La sección 5.3 desarrolla lo que eso implica      |
| **3. El hash de contraseña es lento a propósito**           | **No es una carencia de la herramienta: es su propósito.** La sección 5.4 explica por qué   |
| **4. La autorización se decide en la base, no en el token** | **La decisión menos obvia y la más importante del capítulo.** La sección 5.9 la desarrolla  |

<img src="media/4492e111a36f0fbf249faf21c32094120c88768a.png" style="width:5.79167in;height:4.8125in" />

**Figura 5.1** *— Los tres esquemas históricos y qué resigna cada uno.*

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p><strong>PARA EL PIZARRÓN: la pregunta correcta</strong></p>
<p><strong>No hay una tercera opción que tenga las dos cosas.</strong> Todo lo que se hace para «revocar un JWT» —listas negras, tokens cortos con refresco, versionado— es <strong>reintroducir estado del servidor de alguna forma</strong>, aceptando parte del costo que se quería evitar.</p>
<p>Por eso la pregunta correcta no es <em>«¿cuál es mejor?»</em> sino <strong>«¿qué me duele menos perder?»</strong>. En el TPI <strong>duele menos no poder revocar al instante que no poder escalar</strong>, y por eso el token gana.</p>
<p>Y ojo con esto: <strong>la decisión trae consecuencias que aparecen después.</strong> Cuando en la sección 5.9 veas que la autorización consulta la base en cada petición, vas a entender que <strong>es exactamente el precio de esta decisión, pagado en cuotas</strong>.</p></td>
</tr>
</tbody>
</table>

5.3 — Anatomía de un token

Un token firmado tiene **tres partes separadas por puntos**, cada una codificada.

<img src="media/a1dbd3ad21418ed4040fd142f21f0e56b1f2d564.png" style="width:5.79167in;height:4.26042in" />

**Figura 5.2** *— Las tres partes de un token y qué garantiza cada una.*

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p><strong>OJO ACÁ: hacelo ahora mismo, es de las cosas que hay que ver una vez</strong></p>
<ul>
<li><p><strong>Uno.</strong> Tomá cualquier token — el tuyo, de cualquier sistema donde hayas iniciado sesión.</p></li>
<li><p><strong>Dos.</strong> Copiá <strong>la parte del medio</strong>, entre los dos puntos.</p></li>
<li><p><strong>Tres.</strong> Decodificala. En la consola del navegador: atob("...").</p></li>
</ul>
<p><strong>Lo leés entero. Sin clave, sin nada.</strong></p>
<p>Ahora pensá qué significa eso para lo que vas a escribir. Si en el token metés el correo, el rol y el identificador, <strong>todo eso es público</strong> para cualquiera que tenga el token, <strong>incluido el propio usuario</strong>.</p>
<p>A veces está perfectamente bien —el usuario ya sabe su correo—. <strong>Y a veces no:</strong> si metés un campo interno como el nivel de descuento que le corresponde o una marca de cliente problemático, <strong>acabás de publicárselo</strong>.</p>
<p><strong>Regla sin excepciones: si no lo pondrías en una respuesta visible para ese usuario, no va en el token.</strong></p></td>
</tr>
</tbody>
</table>

5.4 — Por qué el hash de contraseña es lento a propósito

Las contraseñas **no se guardan**. Se guarda el resultado de aplicarles una función que **no se puede revertir**, de modo que quien acceda a la base **no obtenga las contraseñas**.

Y acá aparece **la primera intuición equivocada**. Una función de hash criptográfico como las de la familia SHA parece lo indicado: es irreversible y está bien estudiada. **No sirve, y la razón es contraintuitiva: es demasiado rápida.**

Esas funciones están diseñadas para procesar grandes volúmenes de datos **a máxima velocidad**. Una placa gráfica moderna calcula **miles de millones por segundo**. Si un atacante obtiene la base, **no necesita revertir nada**: prueba contraseñas candidatas hasta que un hash coincida. Con esa velocidad, **cualquier contraseña razonable cae en horas**.

**bcrypt** —publicado en 1999 por Niels Provos y David Mazières— **invierte deliberadamente esa propiedad**. Fue diseñado para ser **lento y difícil de acelerar con hardware especializado**, y tiene un parámetro que ajusta cuánto: **el factor de costo**. Cada incremento **duplica** el trabajo. El TPI declara factor **12**: unos **trescientos milisegundos** por verificación.

|                                   | **Con un SHA rápido** | **Con bcrypt costo 12**   |
|-----------------------------------|-----------------------|---------------------------|
| Verificar un login legítimo       | Instantáneo           | **0,3 s** — imperceptible |
| Probar mil millones de candidatas | Segundos              | **Diez años**             |

**Esa asimetría es todo el punto: la lentitud molesta una vez por login y arruina un ataque por fuerza bruta.**

bcrypt incorpora además una **sal** —un valor aleatorio distinto por contraseña— que **se guarda dentro del propio hash**. Su efecto es que **dos usuarios con la misma contraseña tienen hashes distintos**, lo que impide precalcular una tabla de hashes comunes y usarla contra toda la base de una vez.

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p>$2b$12$LQv3c1yqBWVHxkd0LHAkCO.Yl6X8Yh9lRqLxJKQ2vQe3nZ8Vv5rGa</p>
<p>│ │ └────── la sal, 22 caracteres ──────┘└─── el hash ───┘</p>
<p>│ └── el factor de costo</p>
<p>└── la variante del algoritmo</p></td>
</tr>
</tbody>
</table>

Esa **autodescripción** tiene una consecuencia práctica valiosa: **el sistema puede verificar contraseñas guardadas con distintos factores de costo**, porque cada hash dice con cuál se generó. Eso permite subir el factor —como la sección 5.12 anticipa que habrá que hacer— **sin invalidar las contraseñas existentes**: las viejas se siguen verificando con su costo original, y se rehashean con el nuevo **la próxima vez que alguien inicie sesión**.

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p><strong>El corolario que te va a servir para leer código ajeno</strong></p>
<p>Esto es de las pocas cosas en informática donde <strong>«más lento» es la característica y no el defecto</strong>. Vale la pena tenerlo claro porque <strong>va a chocar con todo lo demás que aprendiste</strong>.</p>
<p><strong>Si ves una contraseña hasheada con SHA-256, MD5 o cualquier cosa rápida, eso está mal.</strong> No «es mejorable»: <strong>está mal</strong>, y es de los errores más serios que puede tener un sistema.</p>
<p>Y no importa cuánto se haya complicado el resto —tres vueltas de hash, una sal propia, concatenaciones raras—: <strong>si la función base es rápida, sigue siendo rápida</strong>, y un atacante con la base en la mano prueba millones de candidatas por segundo.</p>
<p>Hay algoritmos más nuevos y mejores que bcrypt —<strong>argon2</strong> ganó una competencia internacional en 2015 por eso— pero <strong>todos comparten la misma idea: ser caros a propósito</strong>.</p></td>
</tr>
</tbody>
</table>

5.5 — El flujo de autenticación, y por qué el orden importa

La sección 5.1 del TPI describe el inicio de sesión en once pasos. **Los primeros tres concentran las decisiones.**

<img src="media/438189e53a9b0064a54b1ba5a0f2633139a0ef59.png" style="width:5.79167in;height:4.54167in" />

**Figura 5.3** *— El flujo de autenticación, con el punto donde se decide sin calcular.*

5.6 — bcrypt fuera del bucle, y su semáforo

Acá se cobran EA-02 y EA-06 sobre **el único caso del sistema donde aparecen**. El TPI enuncia la regla **sin ninguna flexibilidad**: toda invocación a Passlib —**hash y verificación**— se ejecuta con await anyio.to_thread.run_sync(). **No hay ninguna excepción y no hay ninguna llamada directa en el código.**

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p>from anyio import to_thread</p>
<p>async def verificar_password(plano: str, hasheado: str) -&gt; bool:</p>
<p>async with _semaforo_bcrypt:</p>
<p>return await to_thread.run_sync(pwd_context.verify, plano, hasheado)</p></td>
</tr>
</tbody>
</table>

**Dos piezas, y la segunda es la que sorprende.** El hilo aparte resuelve EA-02: el trabajo de procesador ocurre **fuera del bucle**, que sigue atendiendo. **El semáforo resuelve un problema que el hilo no resuelve.**

<img src="media/737dfa6e81c9e0013532ad85a14e0852fc599c66.png" style="width:5.79167in;height:3.94792in" />

**Figura 5.4** *— bcrypt dentro del bucle, en un hilo, y en un hilo con semáforo.*

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p><strong>OJO ACÁ: hacé la cuenta antes de seguir</strong></p>
<ul>
<li><p>Un login = <strong>0,3 segundos de procesador puro</strong>.</p></li>
<li><p>Sin sacarlo a un hilo: <strong>tres logins por segundo saturan el proceso completo</strong>.</p></li>
<li><p>Y no «lo ponen lento»: lo <strong>detienen</strong>. Ni el catálogo, ni el chequeo de salud, ni las conexiones de eventos abiertas.</p></li>
</ul>
<p>Y ahora <strong>la parte que engaña</strong>: en tu máquina, probando solo, <strong>tres logins por segundo no van a pasar jamás</strong>. Vas a escribir pwd_context.verify(...) sin await to_thread, va a andar perfecto, y vas a pensar que la regla es exagerada.</p>
<p>Se rompe <strong>el primer día de uso real</strong>, cuando treinta personas entran a la vez al empezar el turno. Y el síntoma no va a ser «el login está lento»: va a ser <strong>la aplicación entera no responde</strong>, incluidos los usuarios que ya estaban adentro mirando su pedido.</p>
<p>Por eso el TPI dice «no hay ninguna excepción y no hay ninguna llamada directa en el código». <strong>Es de las pocas reglas que se pueden verificar con un grep</strong>, igual que EA-03: buscá pwd_context sin to_thread cerca.</p></td>
</tr>
</tbody>
</table>

5.7 — Los cuatro roles

El TPI define **cuatro roles acumulables** —un usuario puede tener más de uno— y establece antes que nada **un principio que ordena todo lo demás**:

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p><strong>El principio</strong></p>
<p>Todo endpoint que opera sobre <strong>un recurso propio</strong> —direcciones y pedidos propios— exige <strong>únicamente estar autenticado y ser el propietario</strong>, no un rol en particular. <strong>El administrador puede comprar como cualquier otro usuario.</strong></p>
<p>Dicho al revés: <strong>los roles otorgan capacidades sobre lo ajeno, no sobre lo propio.</strong> Nadie necesita un rol para ver su propio pedido.</p></td>
</tr>
</tbody>
</table>

| **Rol**     | **Puede**                                                                                                                     | **No puede**                                                                                                                               |
|-------------|-------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------|
| **ADMIN**   | CRUD de usuarios, categorías, productos, galerías e ingredientes; ver todos los pedidos; estadísticas; ajuste manual de stock | No tiene restricciones **de rol** — pero **sigue sujeto a la matriz de transiciones y a las reglas de negocio**                            |
| **STOCK**   | Leer productos e ingredientes con cantidad exacta, cambiar disponibilidad, ajustar stock, ver movimientos                     | **No crea, edita ni elimina** productos, ingredientes ni categorías: **sólo mueve existencias**. No administra usuarios ni ve estadísticas |
| **PEDIDOS** | Ver todos los pedidos con detalle e historial, ejecutar transiciones autorizadas, reclasificar modalidad en pendiente         | No administra el catálogo, no ve estadísticas, y **nunca mueve stock por un endpoint propio**: eso lo produce la transición de estado      |
| **CLIENT**  | Catálogo, carrito, crear pedidos, consultar y seguir los propios, cancelar mientras estén pendientes                          | Sólo accede a **sus propios datos**. Es el rol que **el registro asigna automáticamente**                                                  |

**Dos filas merecen comentario porque enseñan a leer una matriz de permisos.**

**El administrador no está por encima de las reglas de negocio.** Puede ver todo y administrar todo, y **sigue sujeto a la matriz de transiciones**: no puede llevar un pedido entregado a pendiente **porque ningún rol puede**, no porque le falte permiso.

**El gestor de pedidos nunca mueve stock directamente.** Puede *provocar* movimientos —al avanzar un estado— pero **no existe un endpoint donde él escriba stock**. Eso es coherente con lo que la clase 7 desarrolla: **el stock tiene un único punto de escritura**.

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p><strong>PARA ENTENDER: tener todos los permisos no es estar por encima de las reglas</strong></p>
<p>Son <strong>dos capas distintas</strong> y hay que tenerlas separadas en la cabeza:</p>
<ul>
<li><p><strong>Permisos:</strong> <em>¿este actor puede intentar esta operación?</em></p></li>
<li><p><strong>Reglas de negocio:</strong> <em>¿esta operación tiene sentido en este estado?</em></p></li>
</ul>
<p>Un sistema que las mezcla termina con un rol «superadministrador» que puede saltearse las reglas del dominio — y <strong>ese rol es la puerta por la que se cuelan todas las inconsistencias</strong>: alguien lo usa para «arreglar» un caso raro, y <strong>deja los datos en un estado que ninguna otra parte del sistema espera</strong>.</p></td>
</tr>
</tbody>
</table>

5.8 — Por qué SISTEMA no es un rol

Esta sección trata **una decisión de modelado que ocupa un párrafo del TPI y enseña más que muchas páginas**.

La matriz de transiciones incluye un actor llamado SISTEMA: es quien ejecuta, por ejemplo, **la expiración automática de un pedido que nadie confirmó**. Parece natural modelarlo como un quinto rol. **El TPI dice que no**, y da las dos razones:

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p><strong>Lo que declara el TPI</strong></p>
<p><strong>SISTEMA no es un rol.</strong> No aparece en la tabla de transiciones ni en la tabla de roles. Un rol es algo que <strong>se le asigna a un usuario</strong> y que la verificación de permisos comprueba; SISTEMA <strong>no se le puede asignar a nadie, no se puede autenticar con él</strong>, y no existe ninguna fila de usuario que lo tenga. <strong>Es una marca en el historial</strong> que dice «esta transición no la ejecutó una persona».</p>
<p>Y la razón por la que la alternativa era peor: modelarlo como rol habría exigido crear un usuario de sistema, y <strong>un usuario que existe pero con el que nadie puede entrar es una fila que en algún momento alguien va a intentar usar para otra cosa.</strong></p></td>
</tr>
</tbody>
</table>

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p><strong>PARA ENTENDER: un usuario de sistema es una puerta que dejaste abierta y anotaste que no se usa</strong></p>
<p><strong>Pensá cómo termina siempre.</strong> Creás usuario_sistema para que las tareas automáticas tengan bajo qué actuar. Al mes, alguien necesita correr un script y <strong>usa esa cuenta porque ya existe y tiene permisos</strong>. A los seis meses hay <strong>tres integraciones</strong> usándola. Al año <strong>nadie sabe qué hace cada cosa con esa cuenta, y no la podés desactivar</strong> porque algo se rompe.</p>
<p>La alternativa del TPI es más simple y más segura: <strong>SISTEMA es un dato, no una identidad.</strong> Es un valor en una columna del historial que dice quién ejecutó una transición. <strong>No tiene contraseña, no tiene permisos, y no hay forma de entrar con él.</strong></p>
<p><strong>La pregunta de diseño que te llevás:</strong> cuando estés por crear una entidad «técnica» —un usuario de sistema, una cuenta genérica, un rol especial— preguntate si lo que necesitás es <strong>una identidad o un dato</strong>. <strong>Casi siempre es un dato.</strong></p></td>
</tr>
</tbody>
</table>

5.9 — Vigencia: la autorización se decide en la base

**Acá está la decisión más importante del capítulo**, y es la que responde al costo que la sección 5.2 anunció.

El TPI declara que las asignaciones de rol **tienen vigencia**: pueden revocarse y pueden vencer. Y de ahí sale la regla que gobierna todo:

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p><strong>Lo que declara el TPI</strong></p>
<p><strong>Roles incluidos en el token.</strong> El token incorpora únicamente los roles vigentes al momento de emitirlo, y <strong>son informativos para la interfaz. Nunca son fuente de autorización.</strong></p>
<p><strong>Expiración durante la sesión.</strong> La autorización <strong>consulta la base en cada petición</strong>, de modo que una asignación revocada o vencida <strong>deja de otorgar permisos de inmediato, aun con un token todavía vigente</strong>.</p></td>
</tr>
</tbody>
</table>

**Esa es la respuesta del TPI al problema de la sección 5.2** —que un token emitido no se puede invalidar—. Y fijate en la jugada, porque es elegante: **no intenta invalidar el token. Hace que el token no decida nada.**

El token **sigue siendo válido**: sigue diciendo quién sos, y eso no cambió. **Lo que cambió es qué podés hacer** — y eso **no vive en el token sino en la base**, donde sí se puede modificar en cualquier momento.

Y la contracara para el frontend es exacta: los roles que vienen en el token sirven para **decidir qué botones mostrar** —que es usabilidad— y **no sirven para nada más**. **Es RN-F04 vista desde este lado**, y por eso sus garantes le pegan al backend directamente, salteándose la interfaz.

| **Regla de vigencia** | **Qué establece**                                                                                                                         |
|-----------------------|-------------------------------------------------------------------------------------------------------------------------------------------|
| **Asignación**        | Sólo un administrador asigna o revoca roles a terceros. **Queda registro de quién lo hizo**                                               |
| **Revocación**        | El borrado **escribe una fecha de revocación; la fila no se borra**. El historial de quién tuvo qué rol **se conserva completo**          |
| **Reasignación**      | Asignar un rol vencido crea una fila nueva y cierra la anterior **en la misma transacción**. Si ya hay una abierta, responde 409          |
| **Auto-registro**     | El registro inserta la asignación del rol de cliente **en la misma transacción** que crea el usuario                                      |
| **Autoprotección**    | Un administrador **no puede eliminarse ni revocarse su propio rol**, y el sistema **rechaza lo que dejaría cero administradores activos** |

**El auto-registro y la transacción** merecen un comentario. El TPI aclara: *«sin esa inserción, el usuario recién registrado no puede comprar»*. Crear el usuario y asignarle su rol son **una sola operación de negocio**, y si la segunda falla, **la primera no debe quedar**. Es exactamente el problema que la clase 6 resuelve con el Unit of Work — y conviene notarlo ahora, porque **es la primera vez en el módulo que aparece una operación que no tiene sentido a medias**.

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p><strong>OJO ACÁ: la autoprotección parece exagerada hasta que ves lo fácil que es quedarse afuera</strong></p>
<p>Hay <strong>dos administradores</strong>. Uno se va de la empresa y le revocan el rol. El que queda está probando la pantalla de roles y <strong>se revoca el suyo para ver qué pasa</strong>.</p>
<p>Listo. <strong>Cero administradores.</strong> Nadie puede asignar roles, <strong>porque asignar roles requiere ser administrador</strong>. La única salida es entrar a la base a mano y escribir una fila.</p>
<p>Y fijate que <strong>ninguno de los dos hizo nada raro</strong>: el primero se fue, el segundo probó un botón. <strong>El sistema quedó inutilizable por dos operaciones perfectamente válidas.</strong></p>
<p>Por eso el TPI no dice «tené cuidado»: declara que <strong>el sistema rechaza la operación que dejaría cero administradores activos</strong>. Es la misma idea que venís viendo desde el frontend: <strong>una regla que depende de que alguien se acuerde, falla.</strong></p></td>
</tr>
</tbody>
</table>

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p><strong>Y el historial guarda el rol como instantánea</strong></p>
<p>El TPI lo dice así: una transición ejecutada el viernes a las 23:59 <strong>sigue diciendo bajo qué rol se autorizó</strong>, aunque el lunes ese rol ya no exista.</p>
<p>Es <strong>lo mismo que viste en la clase 4 con el precio del producto</strong>: el registro guarda <strong>lo que era cierto en ese momento</strong>, no lo que es cierto ahora.</p>
<p>Y la razón es idéntica. Si el historial resolviera el rol consultando la asignación actual, <strong>revocarle un rol a alguien reescribiría todo lo que esa persona hizo en el pasado</strong>. Una auditoría de lo que pasó en marzo <strong>daría resultados distintos según el día en que la corras</strong>.</p>
<p>Es la distinción de la clase 4 otra vez: <strong>lo que describe cambia, lo que registra no.</strong> Y cuando dudes de si un dato hay que copiarlo o referenciarlo, <strong>esa es la pregunta</strong>.</p></td>
</tr>
</tbody>
</table>

5.10 — Cambio obligatorio de contraseña, y los dos routers

El sistema puede marcar que un usuario **debe cambiar su contraseña** —por ejemplo, tras un reseteo administrativo— y mientras esa marca esté activa **el acceso queda restringido a un puñado de endpoints**.

**La implementación es donde está la lección**, porque el TPI resuelve **una limitación real del marco de trabajo**.

<img src="media/1b90092bc5a9e447c0189c3ab54862e3087f4a58.png" style="width:5.79167in;height:3.84375in" />

**Figura 5.5** *— Los dos routers, qué endpoint cae en cada uno, y por qué no se resuelve con exclusiones.*

La salida del estado tiene **una sutileza que conviene notar**. Al confirmar la contraseña nueva, la marca se desactiva, se registra el momento del cambio, y el endpoint **devuelve un token nuevo cuya marca de emisión es igual o posterior** — de modo que, en palabras del TPI, *«la sesión continúa»*. **El usuario no tiene que volver a iniciar sesión.**

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p><strong>El detalle del canal de eventos, que parece menor</strong></p>
<p>Muestra <strong>cómo se piensa un bloqueo completo</strong>. Es fácil acordarse de bloquear los endpoints normales: llegan, pasan por la dependencia, se rechazan. <strong>El canal de eventos es distinto porque es una conexión que queda abierta</strong> — y si nadie lo contempla, alguien con el cambio de contraseña pendiente <strong>igual sigue recibiendo eventos en vivo</strong>.</p>
<p>No es un agujero grave —son sus propios pedidos—. Pero <strong>es una inconsistencia</strong>: el sistema dice «no podés hacer nada hasta que cambies la contraseña» <strong>y al mismo tiempo le está mandando datos</strong>.</p>
<p>Cuando armes un bloqueo de este tipo, la pregunta es: <strong>¿qué caminos hacia mis datos no pasan por donde puse la verificación?</strong> Casi siempre hay uno que se escapa, y <strong>suele ser el que no se parece a los demás</strong>.</p></td>
</tr>
</tbody>
</table>

5.11 — Herramientas de diagnóstico

<img src="media/6a21298d30d8c07c89d01d18a2ad8f3e20742bf6.png" style="width:5.79167in;height:3.09375in" />

**Figura 5.6** *— Un token decodificado: qué está bien que sea público y qué no.*

| **Herramienta**                                | **Qué verifica**                                                                                                                                                                                                                    |
|------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Decodificar un token**                       | La primera verificación, y **se hace sin herramientas**. Con la advertencia de la figura: **nunca pegar un token de producción en un sitio de terceros**                                                                            |
| **La documentación interactiva**               | Permite autenticarse y ejecutar endpoints protegidos. Es la forma más rápida de verificar que una dependencia de rol hace lo que debe: **iniciar sesión con un usuario sin el rol requerido y comprobar que responde 403 y no 401** |
| **Los registros del servidor**                 | Los intentos fallidos **con su motivo**. Y acá una regla de diagnóstico que es también de seguridad: **el registro puede decir «contraseña incorrecta para el usuario X»; la respuesta al cliente no**                              |
| **Medir cuánto tarda una verificación**        | Si un login tarda **del orden de trescientos milisegundos**, el factor de costo está bien puesto. **Si tarda cinco, alguien lo bajó**                                                                                               |
| **Contar hilos activos durante varios logins** | Verifica el semáforo. Sin él, veinte logins simultáneos producen **veinte hilos**; con él, **tantos como permisos haya declarados**                                                                                                 |

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p><strong>EXPERIMENTO — cinco minutos, y hace visible por qué existe cada pieza</strong></p>
<ul>
<li><p><strong>Uno.</strong> Implementá la verificación <strong>sin</strong> sacar bcrypt a un hilo. Medí cuánto tarda un login. <strong>Anotá el número.</strong></p></li>
<li><p><strong>Dos.</strong> Ahora, <strong>mientras hacés un login</strong>, pedí desde otra pestaña cualquier endpoint público — el catálogo, o el chequeo de salud.</p></li>
</ul>
<p><strong>No responde hasta que el login termina.</strong> Ni siquiera el chequeo de salud, <strong>que es lo que un orquestador usa para saber si tu servicio está vivo</strong>.</p>
<ul>
<li><p><strong>Tres.</strong> Sacalo a un hilo con to_thread.run_sync. Repetí el paso 2: <strong>ahora el catálogo responde al instante</strong>.</p></li>
<li><p><strong>Cuatro, y es el que muestra el semáforo:</strong> lanzá <strong>veinte logins simultáneos</strong> y volvé a pedir el catálogo. Sin semáforo, veinte hilos compitiendo por los núcleos: <strong>el catálogo vuelve a ponerse lento</strong>. Con cuatro permisos, veinte logins se procesan de a cuatro y <strong>el resto del sistema sigue respondiendo normalmente</strong>.</p></li>
</ul>
<p>Los tres pasos muestran tres cosas distintas: <strong>el hilo salva al bucle, el semáforo salva a los núcleos, y el límite de intentos —que ya está antes— salva de los dos al abuso deliberado.</strong></p></td>
</tr>
</tbody>
</table>

5.12 — Seguridad y evolución

**Cuatro consideraciones cierran el capítulo, y son las más importantes del módulo hasta acá.**

| **La consideración**                                                                      | **Por qué**                                                                                                                                                                                                                                                                                                                                                                                                                  |
|-------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Los mensajes de error no revelan si un usuario existe**                                 | Responder «ese correo no está registrado» ante uno y «contraseña incorrecta» ante otro le permite a un atacante **enumerar cuentas sin adivinar ninguna contraseña**. La respuesta al cliente **debe ser la misma en los dos casos**; en los registros del servidor, en cambio, conviene distinguirlos                                                                                                                       |
| **El tiempo de respuesta también revela**                                                 | Si un correo inexistente responde **al instante** y uno existente tarda **trescientos milisegundos** —porque calculó el hash—, **la diferencia es medible** y permite lo mismo que el mensaje. La defensa es **verificar contra un hash ficticio cuando el usuario no existe**, de modo que el tiempo sea equivalente                                                                                                        |
| **El token no se puede invalidar, y eso hay que decirlo**                                 | Un usuario que cierra sesión borra su token del navegador, **y ese token sigue siendo válido hasta que expira**. Si alguien lo capturó antes, **el cierre de sesión no lo detiene**. La mitigación es la de la sección 5.9: aunque el token siga siendo válido, **la autorización se reevalúa contra la base en cada petición**                                                                                              |
| **La cadena es tan fuerte como su eslabón más débil — y el más débil suele estar afuera** | Un sistema con bcrypt de costo 12, tokens firmados y roles con vigencia **no sirve de nada** si el reseteo de contraseña manda un enlace que no expira, o si la clave de firma está en el repositorio. Y eso último merece énfasis: **la clave con la que se firman los tokens es el secreto más importante del sistema**, porque quien la tenga **puede fabricar un token válido para cualquier usuario con cualquier rol** |

Sobre la evolución, tres observaciones. **La primera:** el factor de costo **se revisa con el tiempo**. Lo que hoy son trescientos milisegundos, **con el hardware de dentro de cinco años serán treinta**, y el parámetro habrá que subirlo. **Es un valor que caduca**, y conviene tenerlo declarado como configuración y no fijo en el código.

**La segunda:** existen algoritmos posteriores a bcrypt —**argon2** ganó una competencia internacional en 2015— diseñados para resistir mejor el hardware especializado. bcrypt sigue siendo aceptable, y **la migración entre uno y otro es posible porque el hash guarda con qué algoritmo se generó**.

**Y la tercera: la industria se mueve hacia no tener contraseñas.** Las llaves de acceso basadas en criptografía de clave pública **eliminan el problema de raíz** — no hay nada que hashear ni que robar de la base. Ese es probablemente el futuro, y **entender por qué las contraseñas son difíciles es lo que permite valorarlo**.

5.13 — Verificación: el checklist honesto

1.  Decodificar un token y **leer su contenido sin la clave**, explicando qué garantiza la firma y qué no. *(5.3)*

2.  Alterar un carácter del contenido y verificar que **la firma deja de validar**. *(5.3)*

3.  Medir cuánto tarda una verificación de contraseña y **comprobar que es del orden de trescientos milisegundos**. *(5.4)*

4.  Verificar **sin sacar bcrypt a un hilo** y comprobar que **el chequeo de salud deja de responder** mientras tanto. *(5.6)*

5.  Lanzar veinte inicios de sesión simultáneos **con y sin semáforo**, y documentar la diferencia. *(5.6)*

6.  Provocar un 401 y un 403 y explicar **cuál corresponde a cada situación**. *(5.7)*

7.  Revocar un rol a un usuario con sesión abierta y verificar que **pierde permisos en la petición siguiente, con el mismo token**. *(5.9)*

8.  Intentar que un administrador **se revoque su propio rol** y verificar el rechazo. *(5.9)*

9.  Activar la marca de cambio de contraseña y comprobar que **los cuatro endpoints exceptuados siguen funcionando** y el resto no. *(5.10)*

5.14 — Los doce errores frecuentes

| **El error**                                                                     | **Por qué duele**                                                                                                                                   | **Sección** |
|----------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------|-------------|
| **Guardar contraseñas con un hash rápido**                                       | Una función de la familia SHA es demasiado veloz: **un atacante con la base prueba miles de millones por segundo**                                  | 5.4         |
| **Llamar a bcrypt directamente desde una corrutina**                             | Bloquea el bucle **trescientos milisegundos por verificación**. Viola EA-02 y EA-06                                                                 | 5.6         |
| **Sacar bcrypt a un hilo y no acotar la concurrencia**                           | Cien logins simultáneos lanzan **cien hilos** con un cálculo caro cada uno                                                                          | 5.6         |
| **Evaluar el límite de intentos después de verificar la contraseña**             | Le regala al atacante **una amplificación**: a él le cuesta una petición y al servidor un cálculo caro                                              | 5.5         |
| **Poner datos sensibles en el contenido del token**                              | **No está cifrado:** cualquiera con el token lo lee                                                                                                 | 5.3         |
| **Autorizar según los roles que vienen en el token**                             | El TPI es explícito: son informativos y **nunca fuente de autorización**. Un rol revocado **seguiría otorgando permisos hasta que el token expire** | 5.9         |
| **Modelar un actor técnico como un usuario del sistema**                         | Una cuenta que existe y con la que nadie debería entrar **termina usándose para otra cosa**                                                         | 5.8         |
| **Borrar la fila al revocar un rol**                                             | Se pierde **el historial de quién tuvo qué y hasta cuándo**                                                                                         | 5.9         |
| **Resolver el rol del historial consultando la asignación actual**               | Revocar un rol **reescribiría el pasado**                                                                                                           | 5.9         |
| **Crear el usuario y asignarle su rol en operaciones separadas**                 | Si la segunda falla, **queda un usuario que no puede comprar**                                                                                      | 5.9         |
| **Distinguir en la respuesta entre usuario inexistente y contraseña incorrecta** | Permite **enumerar cuentas sin adivinar ninguna contraseña** — y lo mismo vale para el tiempo de respuesta                                          | 5.12        |
| **Poner la clave de firma en el repositorio**                                    | Quien la tenga **puede fabricar un token válido para cualquier usuario con cualquier rol**                                                          | 5.12        |

5.15 — Las actividades, y qué busca cada una

1\. El token por dentro

Emitir un token, **decodificar sus tres partes** y documentar cada afirmación de su contenido. Alterar el contenido y verificar el rechazo. **Explicar por qué la alteración se detecta sin que el servidor guarde nada.**

***Qué busca:** la última parte. Que el servidor detecte la alteración sin recordar el token es exactamente lo que hace que el esquema escale.*

2\. El costo medido

Medir el tiempo de verificación con factores de costo **8, 10 y 12**, y construir la tabla de la sección 5.4 **con datos propios**: cuánto tarda un login legítimo y cuánto tardaría probar mil millones de candidatas en cada caso.

***Qué busca:** que veas que cada incremento duplica, y que la cuenta del atacante crece igual de rápido. El número te va a sorprender.*

3\. Las tres capas de defensa

Implementar el flujo de login con **las tres piezas** —límite de intentos, hilo aparte y semáforo— y **demostrar con mediciones qué protege cada una**. Documentar **qué pasa si se quita cada una por separado**.

***Qué busca:** que ninguna sea reemplazable por otra. Sacá una y aparece un problema distinto — no el mismo más leve.*

4\. La autorización que no está en el token

Implementar la verificación de roles **consultando la base**. Iniciar sesión, **revocar el rol desde otra sesión**, y demostrar que **el mismo token pierde permisos en la petición siguiente**. Explicar por qué eso no sería posible si la autorización leyera el token.

***Qué busca:** ver el token seguir siendo válido mientras deja de servir para algo. Ahí se entiende la diferencia entre autenticar y autorizar.*

5\. Los dos routers

Implementar el cambio obligatorio de contraseña con la estructura que el TPI declara. **Intentar resolverlo con exclusiones y documentar por qué no se puede.** Verificar que los cuatro exceptuados funcionan.

***Qué busca:** que choques contra el límite de la herramienta antes de leer la solución. Es la única forma de que la estructura de dos routers deje de parecer arbitraria.*

6\. Exploración: la enumeración de cuentas

Implementar un login que **responda mensajes distintos** según si el usuario existe, y medir además **los tiempos de respuesta** en los dos casos. Documentar **cómo se podría enumerar cuentas con cada una de las dos vías**. Corregir ambas y verificar que las respuestas son indistinguibles **en contenido y en tiempo**.

***Qué busca:** la segunda vía. Casi todo el mundo arregla el mensaje y deja el tiempo — que revela exactamente lo mismo.*

7\. Exploración: los dos lados del mismo token

Junto con alguien del turno de frontend, **seguir un token completo**: dónde se emite, cómo viaja, dónde se guarda, **qué decide de cada lado**. Documentar **qué decisión toma el frontend con los roles del token y qué decisión toma el backend**, y relacionarlo con RN-F04 y sus tres garantes.

***Qué busca:** que descubran juntos que los dos leen el mismo campo y sólo uno de los dos decide algo que importa.*

5.16 — Síntesis: las doce frases

1.  **Autenticación y autorización son dos cosas**: quién sos y qué podés hacer. Del lado del cliente se ven como la diferencia entre un 401 y un 403.

2.  Los tres esquemas históricos resignaron cosas distintas: la contraseña en cada petición **la expone**; la sesión en servidor **puede cerrarse y no escala**; el token **escala y no se puede invalidar**. **No hay una opción que tenga las dos.**

3.  **El contenido de un token no está cifrado: está codificado.** La firma garantiza **integridad y autenticidad, no confidencialidad**. Nada que no pueda ser público va ahí.

4.  El hash de contraseña **es lento a propósito**, y eso no es un defecto: **es la característica**. Una función rápida permite probar miles de millones de candidatas por segundo.

5.  **Trescientos milisegundos de procesador dentro de una corrutina detienen el proceso entero.** Tres logins por segundo saturan el servidor si bcrypt no sale a un hilo.

6.  **El hilo salva al bucle; el semáforo salva a los núcleos; el límite de intentos —evaluado antes que todo— salva del abuso deliberado.** Ninguno reemplaza a otro.

7.  Las validaciones **baratas van antes que las caras**. Invertir ese orden **regala una amplificación**: al atacante le cuesta una petición y al servidor un cálculo de trescientos milisegundos.

8.  Los roles otorgan capacidades **sobre lo ajeno, no sobre lo propio**: nadie necesita un rol para ver su propio pedido, y **el administrador compra como cualquiera**.

9.  **SISTEMA es un dato, no una identidad.** Un usuario que existe y con el que nadie debería entrar **termina usándose para otra cosa**.

10. **Los roles del token son informativos y nunca fuente de autorización.** La autorización consulta la base en cada petición, y **esa es la respuesta del TPI al problema de no poder invalidar un token**.

11. El historial guarda el rol **como instantánea**: si lo resolviera consultando la asignación actual, **revocar un rol reescribiría el pasado**. Es la distinción de la clase 4 entre **lo que describe y lo que registra**.

12. **Las dependencias del marco de trabajo se suman y no se restan**, y de esa limitación sale la estructura de dos routers. **Saber por qué está así evita que alguien la «simplifique».**

5.17 — Qué leer, y en qué orden

Si leés una sola cosa

La **OWASP Password Storage Cheat Sheet** — es **la referencia práctica actualizada**, con los parámetros recomendados para cada algoritmo y **el criterio para elegir entre ellos**. Su sección sobre argon2 explica qué mejora respecto de bcrypt.

Si leés tres

- La **OWASP Authentication Cheat Sheet**: cubre en detalle **los cuatro problemas de la sección 5.12**, incluida **la enumeración por tiempos de respuesta**.

- **Provos y Mazières**, *A Future-Adaptable Password Scheme* (USENIX, 1999): el artículo original de bcrypt. Explica por qué **la adaptabilidad del costo era el punto central del diseño**, y sigue siendo la mejor fuente sobre la idea.

- **Ferguson, Schneier y Kohno**, *Cryptography Engineering* (Wiley, 2010): explica **qué garantiza una firma y qué no** con el rigor que la sección 5.3 resume en dos líneas. Su capítulo sobre **gestión de claves** es pertinente a la advertencia final sobre el secreto de firma.

Las fuentes normativas

- **RFC 7617** — la autenticación básica. Conviene leerla **aunque sea para confirmar que la codificación que usa no es cifrado**.

- **RFC 7519** (*JSON Web Token*, 2015) — define las afirmaciones registradas de la sección 5.3. Se apoya en la **7515** para la firma y en la **7518** para los algoritmos; la **RFC 8725** recopila las buenas prácticas, y **sus advertencias sobre la elección del algoritmo merecen lectura**.

- **RFC 9110** — los códigos de estado y la semántica de 401 y 403, y el encabezado de reintento que la sección 5.5 menciona.

- **Bishop**, *Computer Security: Art and Science* (2.ª ed., 2018): trata los modelos de control de acceso basado en roles **con la formalidad que este capítulo aplica de manera intuitiva**.

Del TPI

Este capítulo se apoya en **la sección 5 completa** —sus cinco subsecciones— y toca además la **4.4** por el límite de intentos que la sección 5.5 menciona, y la **3.5** por la matriz de transiciones donde aparece el actor de la sección 5.8.

Cierre: las seis cosas que hay que recordar

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p><strong>LAS SEIS</strong></p>
<p><strong>1.</strong> <strong>El token está codificado, no cifrado.</strong> Si no lo pondrías en una respuesta visible para ese usuario, <strong>no va en el token</strong>.</p>
<p><strong>2.</strong> <strong>El hash lento es la característica, no el defecto.</strong> Si la función base es rápida, todo lo que le agregues alrededor sigue siendo rápido.</p>
<p><strong>3.</strong> <strong>300 ms de procesador en una corrutina detienen el proceso entero.</strong> Y en tu máquina, probando solo, eso no se nota nunca.</p>
<p><strong>4.</strong> <strong>Las validaciones baratas van antes que las caras.</strong> Si le cuesta menos a él que a vos, tenés un problema aunque el sistema «funcione».</p>
<p><strong>5.</strong> <strong>SISTEMA es un dato, no una identidad.</strong> Antes de crear una entidad técnica, preguntate si necesitás una identidad o un dato — casi siempre es un dato.</p>
<p><strong>6.</strong> <strong>El token dice quién sos; la base dice qué podés.</strong> Por eso un rol revocado deja de servir en la petición siguiente, con el mismo token en la mano.</p></td>
</tr>
</tbody>
</table>

Y una séptima, que es la que ata este capítulo con el de enfrente: **el cliente no protege nada.** Las guardas de ruta del frontend son para que el usuario no vea botones que no puede usar. **Lo único que protege es lo que construiste acá** — y por eso los garantes de RN-F04 son tres pruebas que le pegan al backend **salteándose la interfaz por completo**.
