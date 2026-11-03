**CAPÍTULO 2 — GUÍA DE LECTURA**

**Contratos**

Schemas, validación y CRUD, explicados en criollo

*Traducción didáctica del texto académico, sección por sección. Mismos conceptos, otro idioma.*

Antes de empezar: cómo usar esta guía

Este documento no reemplaza al capítulo original: lo traduce. Cada sección tiene **Qué dice** (la idea comprimida), **En criollo** (la explicación larga con la analogía) y **Para el pizarrón** (la frase que hay que llevarse). **No se pierde ni un concepto**: lo que cambia es el idioma.

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p><strong>LA IDEA MADRE DE TODO EL CAPÍTULO</strong></p>
<p>Si te quedás con una sola palabra de las cuarenta páginas, que sea esta: <strong>contrato</strong>.</p>
<p>Un contrato es un acuerdo entre dos partes sobre <strong>qué se manda, qué se devuelve y qué pasa cuando algo no cumple</strong>.</p>
<p>Y cuando las dos partes son <strong>dos equipos</strong> —como en esta cursada, donde una mitad escribe el servidor y la otra el cliente— ese acuerdo deja de ser un detalle técnico y pasa a ser <strong>el principal punto de fricción del proyecto</strong>.</p>
<p>Todo lo que sigue —los schemas, el 422, los tres modelos, el dinero como cadena— es una respuesta a la misma pregunta: <strong>cómo hacer que ese acuerdo no se rompa sin que nadie se entere.</strong></p></td>
</tr>
</tbody>
</table>

2.1 — De qué se trata esta clase

Qué dice

El capítulo anterior terminó con una afirmación que conviene tomar en serio: **la especificación de la API se deriva del código y por lo tanto no puede desactualizarse**. Este capítulo es el que convierte esa afirmación en algo con consecuencias, porque estudia **qué se declara** para que esa especificación diga lo correcto.

En criollo: por qué esta clase es la segunda y no la sexta

Hay una razón concreta, y es de cronograma. **Al terminar esta clase el backend tiene un contrato publicado y navegable, aunque todavía no haya base de datos.**

La otra mitad de la cursada está esa semana con hojas de estilo y no lo necesita todavía. Cuando lo necesite —cuatro semanas después, al tipar el contrato en TypeScript— **va a existir hace un mes y va a estar corriendo**. Y tipar contra algo que responde es una situación **muy distinta** de tipar contra una tabla de un documento: podés probar, equivocarte y ver el error hoy, no en la semana de integración.

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p><strong>Y una decisión que sorprende a todo el mundo la primera vez</strong></p>
<p>El capítulo la enuncia acá aunque todavía no haya persistencia:</p>
<p>Todos los importes son <strong>DECIMAL(10,2)</strong> y viajan en JSON <strong>como cadena decimal</strong> —"1234.50"—. El tipo TypeScript espejo es <strong>string</strong>.</p>
<p>Esa es la mitad de arriba de una regla que la otra mitad de la cursada estudia como <strong>RN-F08</strong>. Acá se ve <strong>por qué el servidor la impone</strong>, y la sección 2.7 lo desarrolla entero.</p></td>
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
<li><p><strong>Escribir los schemas</strong> de cualquier módulo de la sección 7 del TPI.</p></li>
<li><p><strong>Implementar su CRUD</strong> con los verbos y los códigos de estado correctos.</p></li>
<li><p><strong>Explicar por qué hacen falta tres modelos por entidad y no uno.</strong></p></li>
</ul>
<p>Si podés las tres, esta clase la aprobaste.</p></td>
</tr>
</tbody>
</table>

2.2 — Por qué existe el contrato: tres etapas y tres renuncias

Qué dice

Cuando dos sistemas se hablan, alguien tiene que decidir **qué significa cada campo**. La historia de cómo se resolvió eso tiene tres etapas, y de cada una queda algo.

En criollo

**Primera etapa: el contrato rígido y generado.** A principios de los 2000, el enfoque dominante fue SOAP, con contratos escritos en WSDL. La propuesta era fuerte: el contrato es un documento formal y a partir de él **se generan automáticamente el cliente y el servidor**. Nada podía desajustarse, porque las dos partes salían del mismo archivo.

Funcionó y se abandonó, y el motivo es instructivo. El contrato era **enorme y frágil**: cambiar un campo obligaba a regenerar y redesplegar todo, los documentos eran ilegibles para un humano, y el acoplamiento era tan fuerte que evolucionar por separado se volvía imposible. **Se había resuelto el desajuste al precio de que nada pudiera moverse.**

**Segunda etapa: sin contrato formal.** El estilo REST, que se impuso después, no traía **ningún** mecanismo de contrato. La API era un conjunto de rutas que devolvían JSON, y la documentación **se escribía a mano en un archivo aparte**.

Eso resolvió la rigidez y creó el problema opuesto, que es el que este módulo combate: un documento escrito a mano **se desactualiza el día que alguien cambia un campo y no lo actualiza**. Y a partir de ese momento **no avisa que miente**: sigue ahí, prolijo, describiendo algo que ya no existe. El cliente implementa contra la mentira y el error aparece en integración.

**Tercera etapa: el contrato derivado del código.** En 2011, Tony Tam publicó **Swagger**, con una idea intermedia: que la especificación se genere **a partir del código**, en un formato legible tanto por humanos como por herramientas. En 2015 el proyecto se donó a la Linux Foundation y pasó a llamarse **OpenAPI**; su versión 3.1, de 2021, se alineó con JSON Schema.

<img src="media/6277891f4373f1406e34bfa4380ff20ecb55ca4a.png" style="width:5.79167in;height:4.69792in" />

**Figura 2.1** *— Del contrato generado al contrato derivado: qué resolvió y qué resignó cada etapa.*

Falta la otra mitad de la historia: cómo se declaran esas formas

Durante años la validación se programaba a mano, con condicionales que revisaban cada campo. En 2017, Samuel Colvin publicó **Pydantic**, con una propuesta distinta: **usar las anotaciones de tipo del propio lenguaje** —que existían desde Python 3.5 y hasta entonces eran sólo documentación— para validar en tiempo de ejecución. Su versión 2, de 2023, reescribió el núcleo en Rust y lo volvió lo bastante rápido para **no ser un costo**.

| **Las cuatro decisiones que gobiernan el capítulo** | **Qué significa**                                                                                                                                                                      |
|-----------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **1. El tipo es la validación**                     | No se declara y **además** se valida: **declarar es validar**. Es lo que el Capítulo 1 señaló al decir que las anotaciones dejaron de ser documentación y pasaron a ser comportamiento |
| **2. El contrato se deriva del código**             | Es la lección de las tres etapas: lo que no existe separado del código no se puede desactualizar                                                                                       |
| **3. Fallar temprano y con detalle**                | Si la entrada no cumple, se rechaza **antes** de que corra la lógica, y el rechazo dice exactamente **qué campo falló, qué se esperaba y qué llegó**                                   |
| **4. Entrada y salida son cosas distintas**         | El modelo con el que se recibe **no** es el modelo con el que se responde, y **ninguno de los dos es la tabla**. La sección 2.5 desarrolla por qué                                     |

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p><strong>PARA EL PIZARRÓN: el patrón, que es el mismo de toda la carrera</strong></p>
<p><strong>SOAP resolvió el desajuste haciendo que nada pudiera moverse. REST resolvió la rigidez perdiendo la garantía. OpenAPI busca el punto medio.</strong></p>
<p>Nadie inventó nada mágico. Cada etapa <strong>resignó algo distinto</strong>, y la que ganó fue la que resignó lo que menos dolía en ese momento.</p>
<p>Y ojo con la trampa: <strong>no es que OpenAPI sea «la solución definitiva»</strong>. Es la solución a los problemas de las dos anteriores, con sus propios costos — que el contrato <strong>depende de que vos declares bien los tipos</strong>, por ejemplo.</p>
<p><strong>La pregunta que te tenés que hacer con cada herramienta es siempre la misma: ¿qué resignó para funcionar?</strong> Si no lo ves, todavía no la entendiste.</p></td>
</tr>
</tbody>
</table>

2.3 — Anatomía de un modelo

Un modelo declara **la forma de un dato**:

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p>from decimal import Decimal</p>
<p>from typing import Annotated</p>
<p>from pydantic import BaseModel, Field</p>
<p>class ProductoCreate(BaseModel):</p>
<p>nombre: Annotated[str, Field(min_length=1, max_length=120)]</p>
<p>descripcion: Annotated[str | None, Field(max_length=500)] = None</p>
<p>precio: Annotated[Decimal, Field(gt=0, max_digits=10, decimal_places=2)]</p>
<p>categoria_id: Annotated[int, Field(gt=0)]</p>
<p>disponible: bool = True</p></td>
</tr>
</tbody>
</table>

Cada línea declara **cuatro cosas a la vez**, y conviene tenerlas separadas:

| **Elemento**      | **En nombre**                | **Qué determina**                           |
|-------------------|------------------------------|---------------------------------------------|
| Nombre del campo  | nombre                       | La clave en el JSON                         |
| Tipo              | str                          | Qué se acepta y a qué se convierte          |
| Restricciones     | min_length=1, max_length=120 | Qué valores son válidos **dentro** del tipo |
| Valor por defecto | *(no tiene)*                 | **Si el campo es obligatorio o no**         |

La última fila es la que más confusión genera, y la regla es simple: **un campo sin valor por defecto es obligatorio.** descripcion tiene = None, así que se puede omitir. nombre no tiene, así que omitirlo produce un error.

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p><strong>OJO ACÁ: «puede ser nulo» y «se puede omitir» no son lo mismo</strong></p>
<p>Esta distinción confunde a todo el mundo. Mirá las cuatro combinaciones juntas y quedate con esto:</p>
<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p>a: str # obligatorio, no admite nulo</p>
<p>b: str | None # OBLIGATORIO, admite nulo ← el que sorprende</p>
<p>c: str = "x" # opcional, no admite nulo</p>
<p>d: str | None = None # opcional, admite nulo</p></td>
</tr>
</tbody>
</table>
<p>El caso <strong>b</strong> es el que nadie espera: <strong>hay que mandarlo sí o sí, pero podés mandar null.</strong> Si te olvidás de poner = None, tu campo «opcional» <strong>no es opcional</strong> y el cliente se come un 422 que no entiende.</p>
<p>La regla, y no tiene excepciones:</p>
<ul>
<li><p><strong>El tipo</strong> responde <em>¿qué valores acepto?</em></p></li>
<li><p><strong>El valor por defecto</strong> responde <em>¿se puede omitir?</em></p></li>
</ul>
<p>Son dos preguntas distintas. Que la respuesta a las dos suela ser None es lo que hace que se confundan.</p></td>
</tr>
</tbody>
</table>

Las restricciones más usadas:

| **Restricción**            | **Aplica a**    | **Ejemplo del dominio**       |
|----------------------------|-----------------|-------------------------------|
| gt, ge, lt, le             | Números         | gt=0 para un precio           |
| min_length, max_length     | Textos y listas | max_length=120 para un nombre |
| pattern                    | Textos          | Un código de unidad           |
| max_digits, decimal_places | Decimales       | DECIMAL(10,2) para importes   |

Y para valores cerrados —un conjunto fijo de opciones— corresponde una **enumeración**:

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p>from enum import StrEnum</p>
<p>class EstadoPedido(StrEnum):</p>
<p>PENDIENTE = "pendiente"</p>
<p>CONFIRMADO = "confirmado"</p>
<p>EN_PREPARACION = "en_preparacion"</p>
<p>ENTREGADO = "entregado"</p>
<p>CANCELADO = "cancelado"</p></td>
</tr>
</tbody>
</table>

Eso hace tres cosas: **rechaza** cualquier valor fuera de la lista, **documenta** los cinco valores en la especificación, y —esto es lo que conviene señalar— **es exactamente lo que la otra mitad de la cursada escribe como unión literal en TypeScript**. Los dos lados expresan la misma restricción con la herramienta de su lenguaje, y la especificación de OpenAPI es lo que los mantiene alineados.

2.3.1 — Cuando la restricción no entra en un campo

Las restricciones declarativas cubren la mayoría de los casos, pero no todos. Dos situaciones se les escapan, y para cada una hay una herramienta.

Una regla sobre un solo campo que no es estándar

Por ejemplo, que un nombre **no sea sólo espacios en blanco**:

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p>from pydantic import field_validator</p>
<p>class ProductoCreate(BaseModel):</p>
<p>nombre: Annotated[str, Field(min_length=1, max_length=120)]</p>
<p>@field_validator("nombre")</p>
<p>@classmethod</p>
<p>def nombre_no_vacio(cls, v: str) -&gt; str:</p>
<p>limpio = v.strip()</p>
<p>if not limpio:</p>
<p>raise ValueError("El nombre no puede ser sólo espacios")</p>
<p>return limpio # devolver el valor normalizado</p></td>
</tr>
</tbody>
</table>

Fijate que el validador **devuelve un valor**, y ese valor es el que queda. Sirve tanto **para rechazar como para normalizar**: recortar espacios, pasar a minúsculas, unificar formato. **Normalizar en el borde evita que cada consulta después tenga que contemplar variantes** — si limpiás el nombre acá, no hay que acordarse de limpiarlo en los quince lugares donde se compara.

Una regla que involucra dos campos a la vez

Ninguna restricción de campo puede expresar «la fecha de fin tiene que ser posterior a la de inicio», porque **necesita ver los dos**. Para eso existe la validación a nivel de modelo, que corre **después** de que todos los campos se validaron por separado:

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p>from pydantic import model_validator</p>
<p>class RangoDeFechas(BaseModel):</p>
<p>desde: date</p>
<p>hasta: date</p>
<p>@model_validator(mode="after")</p>
<p>def rango_coherente(self):</p>
<p>if self.hasta &lt; self.desde:</p>
<p>raise ValueError("hasta no puede ser anterior a desde")</p>
<p>return self</p></td>
</tr>
</tbody>
</table>

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p><strong>Un detalle de zonas horarias que conviene retener</strong></p>
<p>El TPI usa este par de fechas en varios endpoints de estadísticas, y su sección 6.1 agrega una precisión: los pares desde y hasta son <strong>fechas civiles interpretadas en la zona horaria de la aplicación</strong>, mientras que <strong>todas las marcas de tiempo se almacenan y se devuelven en UTC</strong>.</p>
<p>Son <strong>dos cosas distintas viviendo en la misma petición</strong>. Confundirlas produce ese bug clásico donde el reporte «del martes» incluye tres horas del miércoles.</p></td>
</tr>
</tbody>
</table>

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p><strong>Una advertencia de criterio</strong></p>
<p><strong>Estas herramientas son para reglas del contrato, no para reglas de negocio.</strong></p>
<p>Que un nombre no sea espacios <strong>es del contrato</strong>. Que un producto no se pueda vender sin stock <strong>es del dominio</strong>, y va en el Service.</p>
<p>Meter reglas de negocio en el schema las vuelve <strong>imposibles de probar sin construir una petición HTTP</strong> — y ese es exactamente el problema que la clase 1 explicó con las capas.</p></td>
</tr>
</tbody>
</table>

2.4 — Qué ocurre durante la validación

Al llegar una petición, el marco de trabajo ejecuta **cuatro pasos antes de que el handler corra**. Conocer el orden importa, porque explica comportamientos que de otro modo sorprenden.

<img src="media/1bf1012a901ac730fa0480361e7e0aa29ac24832.png" style="width:5.79167in;height:4.51042in" />

**Figura 2.2** *— Los cuatro pasos de la validación, y dónde nace el 422.*

El paso 2 merece atención, porque es una decisión y no un descuido

Por defecto, el modo es **permisivo**: si un valor se puede convertir sin ambigüedad, se convierte. Eso es razonable para HTTP, donde **todo llega como texto** — un parámetro de consulta es siempre una cadena, y exigirle al cliente que distinga tipos que la URL no puede expresar sería absurdo.

Pero tiene una contracara: **la coerción puede ocultar un error del cliente.** Si alguien manda "1234.50" donde va un Decimal, se acepta. Si manda 1234.5 como número de punto flotante, **también** — y ahí ya se perdió precisión antes de llegar. Por eso el TPI declara que los importes viajan como cadena: no es sólo para el cliente, es **para que no haya conversión intermedia por punto flotante**.

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p><strong>OJO ACÁ: que un valor se acepte no significa que esté bien mandado</strong></p>
<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p>class Filtro(BaseModel):</p>
<p>activo: bool</p>
<p># Todo esto se acepta y vale True:</p>
<p>{"activo": true} {"activo": "true"} {"activo": 1} {"activo": "yes"}</p></td>
</tr>
</tbody>
</table>
<p>Eso está bien para HTTP —de una URL todo llega como texto— y <strong>está mal cuando disimula un bug del cliente</strong>. Si el frontend te manda "yes" porque alguien concatenó mal, <strong>vos nunca te enterás: lo aceptaste</strong>.</p>
<p>Y ojo con el caso feo: <strong>si el cliente te manda un importe como número JSON en vez de cadena, se acepta igual</strong> — y para cuando llegó a tu modelo, JavaScript ya lo convirtió a punto flotante y le comió precisión. Por eso el TPI declara string de los dos lados: <strong>no es una preferencia, es cerrar esa puerta</strong>.</p>
<p>Cuando quieras que no haya coerción, existe <strong>el modo estricto</strong>. Usalo donde importe.</p></td>
</tr>
</tbody>
</table>

2.5 — Modelos segregados: por qué tres y no uno

La tentación natural es escribir **un solo modelo por entidad** y usarlo para todo. Conviene ver por qué no funciona antes de aceptar la alternativa.

Un Producto tiene identificador, nombre, precio, fecha de creación, y quizá un campo interno de costo que **no debe salir nunca**. Con un solo modelo aparecen **tres problemas a la vez**.

<img src="media/84c620e5ed501f880be78e517121bacd8f034b16.png" style="width:5.79167in;height:3.98958in" />

**Figura 2.3** *— Los tres modelos segregados y qué campo aparece en cada uno.*

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p>class ProductoBase(BaseModel):</p>
<p>nombre: Annotated[str, Field(min_length=1, max_length=120)]</p>
<p>precio: Annotated[Decimal, Field(gt=0, max_digits=10, decimal_places=2)]</p>
<p>class ProductoCreate(ProductoBase):</p>
<p>categoria_id: Annotated[int, Field(gt=0)]</p>
<p>class ProductoUpdate(BaseModel):</p>
<p>nombre: Annotated[str | None, Field(min_length=1, max_length=120)] = None</p>
<p>precio: Annotated[Decimal | None, Field(gt=0)] = None</p>
<p>class ProductoPublic(ProductoBase):</p>
<p>id: int</p>
<p>creado_en: datetime</p>
<p># el costo interno no está: no sale nunca</p></td>
</tr>
</tbody>
</table>

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p><strong>PARA ENTENDER: response_model es lo más subestimado del marco de trabajo</strong></p>
<p><strong>Filtra la salida aunque tu código se equivoque.</strong></p>
<p>Pensá el caso concreto: hoy el modelo de la tabla no tiene ningún campo sensible. Dentro de tres meses alguien agrega costo_interno para calcular márgenes. Si el endpoint devuelve el objeto tal cual, <strong>ese campo empieza a viajar al cliente ese mismo día</strong>, sin que nadie lo note.</p>
<p>Con response_model, <strong>no sale. Nadie tuvo que acordarse de nada.</strong></p>
<p>Es la misma idea que tus compañeros del turno de frontend ven en su última clase: <strong>las reglas que dependen de que alguien se acuerde fallan; las que hacen que equivocarse sea difícil, no.</strong></p></td>
</tr>
</tbody>
</table>

2.6 — Actualización parcial: ausente contra nulo

Acá aparece un problema que **parece de detalle y no lo es**, y el TPI lo resuelve explícitamente en su sección 6.1.

Cuando llega una modificación parcial, hay **tres situaciones distintas** para cada campo, y sólo dos son fáciles:

| **El cliente…**                | **Significa**             | **Qué hay que hacer** |
|--------------------------------|---------------------------|-----------------------|
| Manda {"nombre": "Napolitana"} | «Cambiá el nombre a esto» | Actualizar            |
| **No manda nombre**            | «No toques el nombre»     | **Dejarlo intacto**   |
| Manda {"nombre": null}         | «Vaciá el nombre»         | Poner nulo            |

**La segunda y la tercera fila se ven iguales** si sólo se mira el objeto ya construido: en las dos, modelo.nombre vale None. **Y son órdenes opuestas.**

La distinción se resuelve preguntando **qué campos vinieron efectivamente**, y el TPI declara cómo: los schemas Update tienen **todos sus campos opcionales** y el Service aplica **model_dump(exclude_unset=True)**. Omitir un campo lo deja intacto; enviarlo explícitamente lo cambia.

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p>datos = producto_update.model_dump(exclude_unset=True)</p>
<p>for campo, valor in datos.items():</p>
<p>setattr(producto, campo, valor)</p></td>
</tr>
</tbody>
</table>

exclude_unset=True devuelve **sólo los campos que el cliente mandó**. Si no mandó nombre, no aparece en el diccionario y el bucle no lo toca. Si lo mandó como nulo, aparece con valor nulo y se aplica.

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p><strong>OJO ACÁ: el bug más elegante y más difícil de encontrar del capítulo</strong></p>
<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p># MAL: model_dump() sin exclude_unset devuelve TODOS los campos</p>
<p>datos = producto_update.model_dump()</p>
<p>for campo, valor in datos.items():</p>
<p>setattr(producto, campo, valor)</p></td>
</tr>
</tbody>
</table>
<p>El cliente mandó {"precio": "5000.00"} para cambiar <strong>sólo el precio</strong>. Pero model_dump() sin argumentos devuelve <strong>todos los campos del modelo</strong>, y los que el cliente no mandó <strong>valen None por ser opcionales</strong>.</p>
<p><strong>Resultado: le cambiaste el precio y le borraste el nombre, la descripción y la categoría.</strong></p>
<p>Y lo peor es cómo se manifiesta. El endpoint devuelve <strong>200</strong>. No hay excepción, no hay log de error. Alguien entra tres días después y ve productos sin nombre, y <strong>nadie puede reconstruir qué pasó</strong>.</p>
<p><strong>Un solo argumento separa una actualización parcial de un borrado silencioso.</strong> Por eso el TPI lo declara en la sección 6.1 en vez de dejarlo a criterio de cada uno.</p></td>
</tr>
</tbody>
</table>

2.7 — El dinero y las cantidades

El TPI es taxativo en su sección 6.1: todos los importes son **DECIMAL(10,2)** en la moneda declarada y viajan en JSON **como cadena decimal** —"1234.50"—, con **string** como tipo TypeScript espejo. Y las cantidades de receta y de stock de insumo son **DECIMAL(12,3)**, también como cadena, **acompañadas siempre del código de la unidad**.

**Tres decisiones, tres razones distintas.**

<img src="media/3c547ef3699007ac044a2f38142f4e5061a1e19e.png" style="width:5.79167in;height:4.28125in" />

**Figura 2.4** *— El importe de la base al cliente: el camino exacto y el camino roto.*

**Por qué Decimal y no punto flotante.** El formato de punto flotante representa los números **en base dos**, y hay decimales que en base dos son periódicos. 0.1 es uno de ellos. Sumar importes en punto flotante **acumula diferencias de centavos** que después no cierran contra la facturación. Decimal representa exactamente lo que se le da.

**Por qué viaja como cadena.** Porque JSON **no distingue** entre un entero, un decimal y un punto flotante: tiene **un solo tipo numérico**. Si el importe viajara como número, el cliente lo convertiría a punto flotante al parsearlo, y el error aparecería del otro lado **sin que el servidor pudiera hacer nada**. Mandarlo como texto garantiza que llegue exactamente igual.

**Por qué la cantidad viaja con su unidad.** Un "1.500" **no significa nada por sí solo**: puede ser un kilo y medio o mil quinientos gramos. El TPI exige que la unidad acompañe al número siempre, y eso elimina una clase entera de errores.

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p><strong>El mejor ejemplo del módulo de una decisión que atraviesa los dos lados</strong></p>
<p>Vos declarás Decimal en el modelo y string en el schema. Tus compañeros del turno de frontend declaran total: string en TypeScript y <strong>tienen prohibido operar con ese valor</strong>. <strong>Es la misma decisión, tomada dos veces, por la misma razón.</strong></p>
<p>Y del lado de ellos hay un detalle que te va a interesar: el TPI dice que <strong>el garante de esa regla es el tipo de TypeScript</strong>, porque si dijera number el compilador dejaría escribir total * cantidad. Diciendo string, lo rechaza — <strong>no porque entienda de dinero, sino porque no se puede multiplicar texto</strong>.</p>
<p>Fijate lo que eso significa: <strong>la restricción la impone el tipo, no la disciplina de quien escribe.</strong> Y de este lado pasa igual: Decimal no te deja perder precisión aunque quieras.</p></td>
</tr>
</tbody>
</table>

2.8 — Los verbos y sus códigos

El TPI declara en su sección 6.1 qué verbo se usa para qué, y hay una decisión que conviene destacar **porque contradice lo que se enseña habitualmente**:

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p><strong>Lo que declara el TPI</strong></p>
<p>POST crea o ejecuta un comando, GET lee, DELETE borra. <strong>PATCH modifica de forma parcial y es el verbo de toda actualización. No se usa PUT: ningún endpoint reemplaza el recurso completo.</strong></p></td>
</tr>
</tbody>
</table>

La razón es coherente con la sección anterior. **PUT significa «reemplazá el recurso por esto»**, y por lo tanto exige mandarlo **entero**: si un campo falta, se borra. En una interfaz real casi nunca se manda todo, así que un PUT mal usado —mandando sólo lo que cambió— **borra el resto**. Es el mismo desastre del model_dump() sin argumentos, pero causado por el verbo.

**El TPI evita el problema quitando el verbo.** No es que esté prohibido por gusto: es que ese verbo tiene un filo que en este dominio no hace falta.

| **Situación**           | **Código** | **Detalle**                                                   |
|-------------------------|------------|---------------------------------------------------------------|
| Lectura exitosa         | **200**    |                                                               |
| Creación exitosa        | **201**    | Con Location apuntando al recurso creado                      |
| Borrado exitoso         | **204**    | Sin cuerpo                                                    |
| Entrada inválida        | **422**    | El de la sección 2.4                                          |
| No autenticado          | **401**    | «No sé quién sos»: falta la credencial o no vale              |
| Autenticado sin permiso | **403**    | «Sé quién sos y no te alcanza»: la credencial vale, el rol no |
| No existe               | **404**    |                                                               |
| Conflicto de estado     | **409**    | Por ejemplo, stock insuficiente                               |

La distinción entre 401 y 403 merece énfasis porque **se maltrata todo el tiempo**. Un cliente que los trata igual **manda al login a alguien que ya inició sesión** — y esa persona escribe bien su contraseña, entra, y vuelve a chocar con lo mismo, porque el problema nunca fue quién era.

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p><strong>Sobre el 201 hay un detalle que casi nadie pone y el TPI sí pide</strong></p>
<p>El encabezado <strong>Location</strong>:</p>
<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p>@app.post("/productos", status_code=201)</p>
<p>async def crear_producto(datos: ProductoCreate, response: Response):</p>
<p>producto = _crear(datos)</p>
<p>response.headers["Location"] = f"/api/v1/productos/{producto.id}"</p>
<p>return producto</p></td>
</tr>
</tbody>
</table>
<p><strong>¿Para qué sirve?</strong> Para que el cliente sepa <strong>dónde quedó</strong> lo que acaba de crear, sin tener que armar la URL por su cuenta adivinando el formato.</p>
<p>Parece poco. Pero fijate el efecto: si mañana las rutas cambian de /productos/{id} a /catalogo/productos/{id}, <strong>un cliente que usa Location sigue funcionando. Uno que arma la URL a mano, no.</strong></p>
<p>Es el mismo principio de todo el capítulo: <strong>cuanto menos tenga que adivinar el cliente, menos se puede romper.</strong></p></td>
</tr>
</tbody>
</table>

2.9 — Colecciones: envoltorio, paginación y ordenamiento

Devolver una lista suelta funciona **hasta que la lista crece**. El TPI lo resuelve con una convención declarada: toda colección cuyo tamaño puede crecer con el uso devuelve el envoltorio **{ items, total, page, size, pages }**.

Los cuatro campos que acompañan a items son los que el cliente necesita para dibujar un paginador, **y no se pueden deducir de la lista**: cuántos hay en total, en qué página está, de qué tamaño, y cuántas páginas hay. Sin ellos, el cliente tiene una lista y ninguna forma de saber si hay más.

| **Regla de paginación** | **Valor**                                           |
|-------------------------|-----------------------------------------------------|
| Tamaño por defecto      | 20                                                  |
| Tamaño máximo           | **100**                                             |
| Página máxima           | El pages de esa consulta; más allá responde **422** |
| El total                | **Respeta los filtros activos**                     |

**Dos de esas filas son decisiones y no detalles.**

**El tamaño máximo existe para protegerse.** Sin él, un cliente puede pedir un millón de registros y el servidor **intenta cumplir**: arma la consulta, la trae a memoria, la serializa. No hace falta mala intención —alcanza con un error de tipeo— y **el efecto es el mismo que un ataque**.

**El total respeta los filtros.** Si hay un filtro por categoría, el total es el de esa categoría y no el de la tabla. Suena obvio y **se equivoca seguido**, porque calcular el total sin filtros es más fácil.

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p><strong>OJO ACÁ: el bug del total sin filtrar, que nadie reporta como bug</strong></p>
<p>Porque <strong>el sistema no falla: miente despacio.</strong></p>
<p>El usuario filtra por «Empanadas», ve <strong>8 productos</strong> en pantalla, y el paginador le dice <strong>«1 de 12 páginas»</strong>. Hace clic en la página 2 y no hay nada. Vuelve, prueba la 3, tampoco.</p>
<p>No hay error, no hay excepción, no hay nada en los logs. Simplemente el paginador está contando <strong>los 240 productos de la tabla</strong> en vez de los 8 que cumplen el filtro.</p>
<p>La causa es siempre la misma y es la vía fácil: se arma la consulta <strong>con filtros</strong> para traer los ítems, y el conteo se hace aparte <strong>sobre la tabla entera</strong> porque es una línea más corta.</p>
<p><strong>Regla: el conteo y la búsqueda salen de la misma consulta filtrada.</strong> Si escribís dos consultas distintas, la segunda tiene que llevar <strong>exactamente</strong> los mismos filtros que la primera.</p></td>
</tr>
</tbody>
</table>

Para el orden, el TPI usa una convención compacta: parámetro **sort** con el nombre del campo, **precedido de un guion para orden descendente**. Así, sort=nombre ordena ascendente y sort=-creado_en descendente. Y cada endpoint **declara en su tabla qué campos son ordenables** — lo que no es un detalle de comodidad: **aceptar un nombre de campo arbitrario del cliente y meterlo en una consulta es exactamente la puerta que la sección 2.13 estudia.**

Los parámetros de consulta se declaran como los demás, y por lo tanto **se validan igual**:

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p>@app.get("/productos", response_model=Pagina[ProductoPublic])</p>
<p>async def listar_productos(</p>
<p>page: Annotated[int, Query(ge=1)] = 1,</p>
<p>size: Annotated[int, Query(ge=1, le=100)] = 20,</p>
<p>sort: Annotated[str | None, Query(pattern=r"^-?(nombre|precio|creado_en)$")] = None,</p>
<p>categoria_id: Annotated[int | None, Query(gt=0)] = None,</p>
<p>q: Annotated[str | None, Query(min_length=2, max_length=80)] = None,</p>
<p>):</p>
<p>...</p></td>
</tr>
</tbody>
</table>

**Cinco decisiones en cinco líneas, y ninguna es cosmética:**

- El le=100 **es** el límite de tamaño de la tabla de arriba, **declarado donde se aplica** — no en un comentario ni en un documento aparte.

- El pattern del ordenamiento **es** la lista blanca de campos ordenables: **lo que no está en esa expresión no llega a la consulta**.

- El ge=1 de la página evita el cero y los negativos.

- El mínimo de dos caracteres en la búsqueda evita que **una sola letra recorra la tabla entera**.

Y fijate en algo: **la lista blanca vive en el mismo lugar que la documentación.** Quien lea la especificación va a ver exactamente qué valores admite sort, **sin que nadie lo escriba aparte** — y por lo tanto sin que se pueda desactualizar.

2.10 — Errores: un formato normado

El TPI **no inventa** su formato de error: adopta uno normado — la **RFC 9457**, con Content-Type: application/problem+json.

Esa norma —*Problem Details for HTTP APIs*— define una forma estándar para describir un error, con campos como type, title, status, detail e instance. Adoptarla tiene una ventaja concreta sobre inventar un formato propio: **cualquier cliente que la conozca sabe leer el error sin documentación adicional.**

Sobre esa base, la sección 14.1 del TPI define un **catálogo de códigos de error**: una lista donde cada situación del dominio tiene **un código estable**, su código HTTP y la descripción de cuándo se produce.

Por qué ese catálogo importa para las dos mitades de la cursada

**El cliente puede distinguir casos por un código y no por el texto del mensaje.** Comparar textos es frágil —cambian, se corrigen, se traducen— y un código no. Con catálogo, el cliente puede mostrar una pantalla distinta ante «stock insuficiente» que ante «producto no disponible», y **esa lógica no se rompe cuando alguien mejora la redacción del mensaje**.

Del lado del servidor, eso se traduce en una regla que el Capítulo 1 ya adelantó: **el Router no traduce excepciones.** El Service lanza excepciones de dominio, y un manejador global —que la clase 8 estudia— las convierte al formato normado. La razón es la de siempre: **con setenta endpoints traduciendo por su cuenta, basta con que uno difiera**.

En esta clase, sin base de datos todavía, alcanza con HTTPException para los casos simples:

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p>@app.get("/productos/{producto_id}", response_model=ProductoPublic)</p>
<p>async def obtener_producto(producto_id: int):</p>
<p>producto = _almacen.get(producto_id)</p>
<p>if producto is None:</p>
<p>raise HTTPException(status_code=404, detail="Producto no encontrado")</p>
<p>return producto</p></td>
</tr>
</tbody>
</table>

Eso es correcto para un CRUD en memoria y **deja de serlo apenas aparece el Service**. La razón se ve mejor con un ejemplo del dominio: cuando el Service de pedidos detecta que no hay stock, **no puede lanzar una excepción HTTP, porque el Service no sabe que existe HTTP**. La misma función la invoca una tarea del worker, **donde no hay ninguna petición que responder**.

Lo que el Service lanza es una excepción de dominio:

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p>class StockInsuficiente(ErrorDeDominio):</p>
<p>codigo = "STOCK_INSUFICIENTE"</p>
<p>estado_http = 409</p></td>
</tr>
</tbody>
</table>

Y el manejador global la traduce **una sola vez, para todos los endpoints**. Esta clase usa HTTPException porque todavía no hay Service; **la clase 8 hace el cambio y explica por qué era inevitable.**

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p><strong>Una decisión que vale para cualquier API que escribas en tu vida</strong></p>
<p><strong>Un mensaje de error es para una persona. Un código de error es para un programa.</strong> Hacen falta los dos y no se reemplazan.</p>
<ul>
<li><p>Si sólo mandás <strong>mensaje</strong>, el cliente termina haciendo if (error.message.includes("stock")), y eso <strong>se rompe el día que alguien corrige una tilde</strong>.</p></li>
<li><p>Si sólo mandás <strong>código</strong>, la persona que abre las herramientas de desarrollo ve ERR_4021 y no sabe qué pasó.</p></li>
</ul>
<p>Y hay un tercer nivel que casi nadie pone y es el que más ayuda: <strong>qué puede hacer el cliente al respecto.</strong> No es lo mismo «no hay stock» —esperá o cambiá el producto— que «el pedido ya fue entregado» —no hay nada que hacer—. Esa distinción es la que permite, del otro lado, <strong>mostrar un botón de reintentar o no mostrarlo</strong>.</p></td>
</tr>
</tbody>
</table>

2.11 — Observabilidad: el identificador de petición

El TPI declara una convención que **parece menor y resuelve un problema grande**: todas las respuestas llevan el encabezado **X-Request-Id**, que también aparece en **cada línea de log** de esa petición **y viaja hasta las tareas que la petición encoló**.

El problema que resuelve es concreto. Un usuario reporta que algo falló. En los registros del servidor hay **miles de líneas de decenas de peticiones simultáneas**, y sin un identificador **no hay forma de saber cuáles corresponden a la suya**. Es buscar una conversación en una grabación de un salón lleno de gente hablando.

Con un identificador que viaja en la respuesta, ese usuario —o el frontend, que lo puede registrar— aporta **un dato** que permite filtrar los registros y ver **sólo esa petición**, de punta a punta.

Y la última parte es la que más vale: **el identificador viaja hasta las tareas.** Una petición puede encolar trabajo que se ejecuta minutos después **en otro proceso**; sin ese arrastre, un error en el worker es **imposible de atar a lo que lo originó**. Es la regla **TB-06**, que la clase 8 desarrolla.

2.12 — Herramientas de diagnóstico

**La documentación interactiva** vuelve a ser la herramienta principal, y ahora con más para mirar: cada endpoint muestra el schema de entrada **con sus restricciones**, el de salida, y los códigos de error posibles. Ejecutar desde ahí con datos inválidos es **la forma más rápida** de verificar que la validación hace lo que se espera.

<img src="media/1038494b7213d19979acee88ac592f5f4ed7f49a.png" style="width:5.79167in;height:3.73958in" />

**Figura 2.5** *— Un 422 y su detalle en la documentación interactiva: tres errores de una sola vez.*

**La especificación en crudo** es lo que hay que abrir cuando el frontend reporta un desajuste. **Es el contrato, y la discusión se resuelve ahí** — no por chat.

<img src="media/bf1d443f4d71c6baeaa2bfbc3ef3c971ba4a7fa9.png" style="width:5.79167in;height:4.78125in" />

**Figura 2.6** *— Del modelo a la especificación: cómo se traduce cada restricción que declaraste.*

**El propio modelo, en una consola de Python**, es la forma más rápida de probar una validación **sin levantar el servidor**:

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p>&gt;&gt;&gt; ProductoCreate.model_validate({"nombre": "", "precio": "-1"})</p>
<p>ValidationError: 2 validation errors for ProductoCreate</p></td>
</tr>
</tbody>
</table>

**Dos errores, no uno:** la validación reporta todo lo que encuentra. Y **model_json_schema()** devuelve el esquema del modelo, que es **literalmente** lo que aparece en la especificación — útil para verificar que una restricción quedó declarada donde se pensaba.

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p><strong>PARA ENTENDER: probá tus modelos en la consola antes de levantar el servidor</strong></p>
<p>Es un hábito que te va a servir toda la carrera y que casi nadie adopta.</p>
<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p>&gt;&gt;&gt; from app.schemas import ProductoCreate</p>
<p>&gt;&gt;&gt; ProductoCreate.model_validate({"nombre": "Milanesa", "precio": "4750.00",</p>
<p>... "categoria_id": 3})</p>
<p>ProductoCreate(nombre='Milanesa', precio=Decimal('4750.00'), categoria_id=3)</p></td>
</tr>
</tbody>
</table>
<p>Fijate lo que ganaste: <strong>el ciclo de prueba pasó de «levantar el servidor, abrir el navegador, armar el cuerpo, mandar» a una línea.</strong></p>
<p>Y hay algo más importante que la velocidad. Un modelo se puede probar <strong>sin FastAPI, sin servidor y sin red</strong>, porque es una clase común de Python. Eso significa que <strong>también se puede testear así</strong>, y los tests de tus schemas van a correr en milisegundos.</p>
<p>Es la misma idea de la actividad 8 que viste en la clase 1: <strong>lo que no depende de nada se prueba solo.</strong> Tus schemas no dependen de nada. Aprovechalo.</p></td>
</tr>
</tbody>
</table>

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p><strong>EXPERIMENTO — el de esta clase se hace de a dos</strong></p>
<p>Demuestra por qué el contrato importa. Cinco pasos y un sexto que es el que cuenta:</p>
<ul>
<li><p><strong>Uno.</strong> Escribí ProductoCreate con sus restricciones y levantá el proyecto.</p></li>
<li><p><strong>Dos.</strong> Abrí la documentación interactiva y <strong>mandá cinco cuerpos inválidos distintos</strong>: nombre vacío, precio negativo, precio con tres decimales, categoría cero, y <strong>un campo de más que no existe en el modelo</strong>.</p></li>
<li><p><strong>Tres.</strong> Anotá qué respondió cada uno. <strong>Fijate especialmente en el último.</strong></p></li>
<li><p><strong>Cuatro.</strong> Ahora mandá <strong>dos errores a la vez</strong> y contá cuántos te reporta.</p></li>
<li><p><strong>Cinco.</strong> Cinco validaciones que no escribiste, y un cuerpo de error que dice exactamente qué falló en cada caso.</p></li>
<li><p><strong>Seis, y es el que importa: pasale la URL de la documentación a alguien del turno de frontend y pedile que arme el cuerpo correcto sin que le expliques nada.</strong></p></li>
</ul>
<p>Si puede hacerlo, tu contrato está bien. <strong>Si tiene que preguntarte algo, eso que te preguntó es lo que falta declarar</strong> — y es mejor descubrirlo hoy que en la semana de integración.</p></td>
</tr>
</tbody>
</table>

2.13 — Seguridad y evolución

Tres consideraciones cierran el capítulo, y las tres son la misma idea vista desde ángulos distintos: **lo que el sistema no te deja hacer mal vale más que lo que confía en que hagas bien**.

| **La consideración**                                                          | **Por qué es de seguridad y no de estilo**                                                                                                                                                                                                                                                                                           |
|-------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **El modelo de salida es un control, no una comodidad**                       | response_model filtra lo que sale **aunque el objeto traiga de más**. Sin él, cada campo que alguien agregue al modelo de datos **empieza a viajar al cliente el día que se agrega**, sin que nadie lo decida                                                                                                                        |
| **Los campos que el cliente no debería fijar no van en el modelo de entrada** | Es el mismo principio del lado contrario: si el modelo Create incluye es_administrador, **el cliente lo puede mandar**. Y no hace falta que la interfaz lo ofrezca: alcanza con **emitir la petición a mano**, que es exactamente lo que hace quien quiere atacar el sistema                                                         |
| **Un parámetro que nombra un campo de la base es una superficie de ataque**   | El ordenamiento de la sección 2.9 recibe un nombre de campo **del cliente**; si ese nombre se interpola en una consulta sin validar contra una lista blanca, **se abre la puerta a una inyección**. Por eso el TPI exige que cada endpoint declare qué campos son ordenables: **la lista blanca no es documentación, es la defensa** |

Sobre la evolución, dos observaciones. **La primera:** el formato de error adoptado —la RFC 9457— es de 2023 y reemplazó a una norma anterior de 2016. Elegir un estándar en lugar de un formato propio significa que **el sistema se beneficia de esa evolución sin cambiar nada**.

**La segunda:** la validación declarativa **está corriéndose hacia los bordes en todo el ecosistema**. El mismo enfoque que acá valida una petición HTTP se usa para validar configuración, mensajes de una cola y respuestas de servicios externos. **Lo que se aprende en esta clase no es específico de la web.**

2.14 — Verificación: el checklist honesto

Nueve comprobaciones. Si las nueve te salen, la clase la entendiste.

1.  Escribir un modelo con **cinco restricciones distintas** y verificar cada una con un valor que la viole. *(2.3)*

2.  Provocar un 422 y **leer los cuatro campos** de su detalle, explicando qué aporta cada uno. *(2.4)*

3.  Mandar **dos errores en la misma petición** y verificar que se reportan los dos. *(2.4)*

4.  Escribir los **tres modelos segregados** de una entidad y justificar **campo por campo** por qué está o no está en cada uno. *(2.5)*

5.  Implementar una actualización parcial con exclude_unset=True, y **demostrar el bug** que aparece sin ese argumento. *(2.6)*

6.  Declarar un importe como Decimal y verificar que **sale como cadena** en el JSON. *(2.7)*

7.  Implementar el envoltorio de colección con paginación, y verificar que el total **respeta un filtro activo**. *(2.9)*

8.  Pedir una página **más allá del máximo** y verificar que responde 422. *(2.9)*

9.  Devolver un objeto con un campo de más y **verificar que response_model lo filtra**. *(2.5)*

2.15 — Los trece errores frecuentes

Casi todos comparten una característica: **el código funciona y devuelve 200**. Por eso llegan a producción.

| **El error**                                                | **Por qué duele**                                                                                                                                  | **Sección** |
|-------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------|-------------|
| **Usar un solo modelo para entrada y salida**               | Obliga a declarar opcionales campos que el servidor genera, y **expone campos que no deberían salir**                                              | 2.5         |
| **Olvidar exclude_unset=True en una actualización parcial** | **Borra silenciosamente** todos los campos que el cliente no mandó — y responde 200                                                                | 2.6         |
| **Confundir «puede ser nulo» con «se puede omitir»**        | El tipo dice qué valores admite; el valor por defecto dice si es obligatorio. Y esa confusión **también rompe el contrato que lee el otro equipo** | 2.3         |
| **Declarar un importe como float**                          | Reintroduce el error de punto flotante que Decimal evita                                                                                           | 2.7         |
| **Devolver el importe como número JSON**                    | El cliente lo convierte a punto flotante al parsearlo, y **la precisión se pierde del otro lado**                                                  | 2.7         |
| **Usar PUT para una modificación parcial**                  | Reemplaza el recurso completo, así que **los campos ausentes se borran**. El TPI directamente no usa PUT                                           | 2.8         |
| **Tratar 401 y 403 como lo mismo**                          | Manda al login a alguien que **ya inició sesión**                                                                                                  | 2.8         |
| **Devolver una lista suelta en lugar del envoltorio**       | El cliente **no puede dibujar un paginador** sin el total y las páginas                                                                            | 2.9         |
| **Calcular el total sin los filtros activos**               | **El paginador miente** — y nadie lo reporta como bug                                                                                              | 2.9         |
| **No limitar el tamaño de página**                          | Un cliente puede pedir un millón de registros, y **alcanza con un error de tipeo**                                                                 | 2.9         |
| **Interpolar el campo de ordenamiento sin lista blanca**    | Es una **superficie de inyección**                                                                                                                 | 2.9 y 2.13  |
| **Distinguir errores por el texto del mensaje**             | Se rompe cuando alguien corrige la redacción. **Para eso está el código**                                                                          | 2.10        |
| **Omitir response_model**                                   | Cada campo que se agregue al modelo de datos **empieza a viajar al cliente sin que nadie lo decida**                                               | 2.13        |

2.16 — Las actividades, y qué busca cada una

1\. Los tres modelos

Tomar la entidad Producto de la sección 7 del TPI y escribir sus **tres modelos segregados completos**, con todas las restricciones que el documento declara. Justificar campo por campo su presencia o ausencia en cada uno.

***Qué busca:** que descubras que la justificación es siempre la misma pregunta — ¿quién produce este dato, el cliente o el servidor?*

2\. El bug del model_dump

Implementar una actualización parcial **de las dos formas** —con y sin exclude_unset—, ejecutar la misma petición contra ambas y documentar el resultado. Explicar **por qué la versión incorrecta responde 200**.

***Qué busca:** que veas un borrado de datos que no genera ni una línea de error. Después de eso no se olvida más.*

3\. El contrato completo de un módulo

Implementar el CRUD **en memoria** del módulo categorias del TPI, con los verbos correctos, los códigos de estado de la sección 2.8, el envoltorio de colección y el ordenamiento. Exportar la especificación y **compararla con la tabla de la sección 6.5 del TPI**.

***Qué busca:** comprobar con los ojos que el JSON generado y la tabla del TPI son el mismo objeto. Y que si difieren, el que está mal sos vos.*

4\. El dinero de punta a punta

Escribir un endpoint que devuelva un importe y verificar en el **JSON crudo** que sale como cadena. Después, en la consola del navegador, hacer JSON.parse de esa respuesta y **comprobar qué tipo llega**. Repetir declarando el importe como número y **documentar la diferencia**.

***Qué busca:** ver el momento exacto en que la precisión se pierde, y que ese momento está del lado del cliente.*

5\. Errores con código

Definir **cinco códigos de error propios** para el módulo de productos, en el formato de la RFC 9457, y escribir el cliente mínimo que distinga entre ellos **sin leer el texto del mensaje**.

***Qué busca:** que sientas lo incómodo que es distinguir por texto — y por qué el catálogo existe.*

6\. Exploración: el contrato como interfaz entre equipos

Junto con alguien del turno de frontend, implementar un endpoint y pedirle que escriba el cliente **usando únicamente la documentación interactiva, sin conversar**. Documentar **cada pregunta que hizo falta hacer igual**, y para cada una, qué habría que declarar en el schema para que no hiciera falta.

***Qué busca:** que la lista de preguntas sea tu lista de tareas. Cada una es algo que el contrato no dice y debería.*

7\. Exploración: los límites de la coerción

Para un modelo con campos int, bool, Decimal y datetime, probar **diez entradas ambiguas** y documentar cuáles se aceptan y a qué valor se convierten. Repetir **en modo estricto** y comparar. Relacionarlo con la decisión de la sección 2.7 sobre por qué los importes viajan como cadena.

***Qué busca:** que veas cuánto te está tapando la coerción, y que decidas dónde no querés que te tape nada.*

2.17 — Síntesis: las once frases

1.  La historia del contrato entre sistemas tiene tres etapas, y cada una **resignó algo distinto**: el contrato generado eliminó el desajuste al precio de que nada pudiera moverse; REST recuperó la flexibilidad perdiendo la garantía; la especificación derivada del código busca las dos cosas.

2.  **Declarar es validar.** Las anotaciones de tipo dejaron de ser documentación y pasaron a ser comportamiento: validan, convierten y documentan a la vez.

3.  La validación ocurre **antes** del handler y reporta **todos** los errores que encuentra, no el primero.

4.  La coerción es deliberada —de una URL todo llega como texto— y tiene una contracara: **puede disimular un error del cliente**.

5.  **El tipo dice qué valores admite; el valor por defecto dice si es obligatorio.** Son dos cosas distintas y confundirlas rompe la actualización parcial.

6.  Hacen falta **tres modelos y no uno**: lo que el cliente aporta, lo que puede cambiar y lo que se le muestra. Un modelo compartido **obliga a mentir en la especificación** y expone campos que no deben salir.

7.  **exclude_unset=True separa una actualización parcial de un borrado silencioso.** Sin él, los campos que el cliente no mandó se pisan con nulo, y la respuesta es 200.

8.  **El dinero es Decimal adentro y cadena afuera**, y las dos mitades tienen su razón: exactitud del lado del servidor, y que el cliente no lo convierta a punto flotante al parsearlo.

9.  El TPI **no usa PUT**, porque reemplazar el recurso completo borra lo que no se mandó. PATCH es el verbo de toda actualización.

10. Un **mensaje de error es para una persona y un código es para un programa**. Hacen falta los dos, y comparar textos es frágil.

11. El **identificador de petición** convierte miles de líneas de registro en las diez que corresponden a un problema concreto, y **viaja hasta las tareas** que esa petición encoló.

2.18 — Qué leer, y en qué orden

Si leés una sola cosa

La documentación de **Pydantic** en docs.pydantic.dev — es la fuente para todo lo de las secciones 2.3 a 2.6, y su página sobre **modos de validación** explica con precisión **qué convierte y qué no**, que es justo lo que la sección 2.4 deja planteado.

Si leés tres

- La documentación de **FastAPI** sobre **modelos de respuesta** y sobre **parámetros de consulta**: cubre lo de las secciones 2.5 y 2.9 con más ejemplos de los que entran acá.

- **Kleppmann**, *Designing Data-Intensive Applications* (O'Reilly, 2017), **capítulo cuarto**: trata la compatibilidad hacia adelante y hacia atrás, y responde la pregunta que todo el mundo hace al final de esta clase — **qué pasa cuando el contrato tiene que cambiar**.

- **Masse**, *REST API Design Rulebook* (O'Reilly, 2011), para las convenciones de la sección 2.9 — leyéndolo con la advertencia de que **es anterior a OpenAPI**.

Las fuentes normativas (para consultar, no para leer de corrido)

- **RFC 9457**, *Problem Details for HTTP APIs* (2023): reemplazó a la RFC 7807 y define los campos de error que el TPI adopta.

- **RFC 9110**, ya citada por la otra mitad de la cursada: códigos de estado y semántica de los métodos. Su sección sobre PATCH remite a la **RFC 5789**, que lo introdujo y **explica en qué se diferencia de PUT**.

- **OpenAPI 3.1** y **JSON Schema**: el formato de la especificación que el marco de trabajo genera, alineado con JSON Schema desde esa versión. Conviene tenerlo a mano para entender **cómo se traduce cada restricción** (Figura 2.6).

- La entrada del proyecto **OpenAPI sobre su propia historia**, para el contexto de la sección 2.2: el paso de Swagger a la Linux Foundation en 2015.

Del TPI, tres secciones

- **6.1** — las convenciones globales. **Conviene leerla entera y tenerla a mano**: de ahí salen la paginación, el ordenamiento, el dinero, los verbos y el exclude_unset.

- **7** — los schemas de cada módulo.

- **14.1** — el catálogo de errores.

Cierre: las seis cosas que hay que recordar

Si dentro de un mes te acordás de seis frases de todo esto, que sean estas.

<table>
<colgroup>
<col style="width: 100%" />
</colgroup>
<tbody>
<tr class="odd">
<td><p><strong>LAS SEIS</strong></p>
<p><strong>1.</strong> Un contrato entre dos equipos <strong>siempre resigna algo</strong>: rigidez o garantía. La pregunta ante cualquier herramienta es <strong>qué resignó para funcionar</strong>.</p>
<p><strong>2.</strong> <strong>Declarar es validar.</strong> El mismo tipo valida la entrada, convierte, filtra la salida y escribe el contrato que lee el otro equipo. <strong>Si está mal, están mal las cuatro.</strong></p>
<p><strong>3.</strong> <strong>Tres modelos y no uno:</strong> lo que el cliente aporta, lo que puede cambiar y lo que se le muestra. Un modelo compartido obliga a mentir y filtra datos sin dar error.</p>
<p><strong>4.</strong> <strong>exclude_unset=True</strong> es la diferencia entre actualizar y borrar. Y la versión rota <strong>responde 200</strong>.</p>
<p><strong>5.</strong> <strong>El dinero es Decimal adentro y cadena afuera.</strong> La restricción la impone el tipo, no la disciplina de quien escribe.</p>
<p><strong>6.</strong> <strong>El mensaje es para una persona; el código, para un programa.</strong> Y el tercer nivel —qué puede hacer el cliente— es el que casi nadie pone y el que más ayuda.</p></td>
</tr>
</tbody>
</table>

Y una séptima, que atraviesa todo el capítulo: **cada vez que una regla depende de que alguien se acuerde, buscá la forma de que la imponga el tipo, el schema o el framework.** response_model, la lista blanca del sort, el le=100, el Decimal. Ninguna de esas cuatro confía en tu memoria — y por eso ninguna falla a las dos de la mañana antes de entregar.
