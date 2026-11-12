# Spec Delta

## Purpose

Define cómo el frontend de la librería consume la API FastAPI a través del proxy same-origin `/api`, mantiene la sesión por cookie, mapea los contratos del backend a su modelo interno y presenta estados de carga, error y permisos sin perder la accesibilidad existente.

## ADDED Requirements

### Requirement: Cliente HTTP same-origin
El frontend SHALL enviar las peticiones a `/api` mediante `fetch` con `credentials: 'include'` y `Content-Type: application/json`, y SHALL desenvolver las respuestas paginadas `{items,total,page,size,pages}` antes de entregarlas a las pantallas.

#### Scenario: Catálogo desde la API
- **WHEN** se abre la vista Catálogo con el backend disponible
- **THEN** el frontend solicita `GET /api/libros?size=100` con credenciales y renderiza los `items` recibidos

#### Scenario: Petición con cookie
- **WHEN** el usuario inicia sesión y luego solicita una ruta protegida
- **THEN** la petición incluye la cookie `access_token` y el backend la recibe a través de Nginx

### Requirement: Sesión y visibilidad por rol
El frontend SHALL iniciar sesión con `POST /api/auth/login`, consultar la identidad con `GET /api/auth/yo`, cerrar sesión con `POST /api/auth/logout` y SHALL mostrar u ocultar las acciones protegidas según los roles `ADMIN`, `VENDEDOR` y `CLIENTE`.

#### Scenario: Inicio de sesión exitoso
- **WHEN** el usuario envía credenciales válidas en el formulario de sesión
- **THEN** el frontend muestra su nombre y roles, habilita las acciones permitidas y conserva la sesión al recargar mediante `/auth/yo`

#### Scenario: Cierre de sesión
- **WHEN** el usuario autenticado pulsa "Cerrar sesión"
- **THEN** el frontend llama a `/api/auth/logout`, limpia el estado y vuelve a la vista pública

#### Scenario: Acción no permitida
- **WHEN** un usuario CLIENTE o anónimo intenta acceder a una acción de staff
- **THEN** el frontend no muestra el formulario o botón correspondiente y, si la petición se fuerza, muestra el mensaje de error 403 del backend

#### Scenario: Historial del cliente
- **WHEN** un usuario con rol CLIENTE abre Historial
- **THEN** el frontend solicita `GET /api/mis-ventas` y muestra solo sus ventas

### Requirement: Cambio obligatorio de contraseña
El frontend SHALL detectar `debe_cambiar_password` en el login o en `/auth/yo`, SHALL mostrar el formulario de cambio de contraseña y SHALL enviar `POST /api/auth/cambiar-password` antes de permitir operaciones protegidas.

#### Scenario: Usuario con cambio obligatorio
- **WHEN** `nuevo@example.com` inicia sesión y el backend responde `debe_cambiar_password: true`
- **THEN** el frontend muestra el formulario de cambio, informa que las operaciones están bloqueadas y, tras cambiarla, refresca la sesión

### Requirement: Mapeo de contratos
El frontend SHALL convertir los importes `Decimal` serializados como string a `number`, los identificadores enteros a sus identificadores internos con prefijo y viceversa, los nombres `snake_case` a `camelCase` y el identificador de venta a `V-####`; SHALL conservar las fechas ISO y formatearlas solo al mostrarlas.

#### Scenario: Importe y venta
- **WHEN** la API devuelve un libro con `precio: "25000.00"` y una venta con `id: 1`
- **THEN** el frontend muestra el precio como `$ 25.000,00` y la venta como `V-0001`

#### Scenario: Cliente
- **WHEN** la API devuelve un cliente con `nombre: "Lucía"` y `perfil: null`
- **THEN** el frontend lo muestra como `nombreCompleto: "Lucía"` sin romper el render

### Requirement: Pantallas conectadas y fuente de verdad
Las vistas Catálogo, Libros, Clientes, Ventas e Historial SHALL obtener sus datos de la API y SHALL refrescar los listados afectados después de cada alta o venta; el frontend MUST NOT persistir libros, clientes ni ventas en `localStorage`.

#### Scenario: Alta de libro
- **WHEN** un ADMIN envía el formulario de alta de libro
- **THEN** el frontend llama a `POST /api/libros`, muestra el resultado y refresca la tabla de libros desde la API

#### Scenario: Venta y stock
- **WHEN** un VENDEDOR o ADMIN confirma una venta válida
- **THEN** el frontend llama a `POST /api/ventas`, muestra el total devuelto y refresca libros, stock e historial

#### Scenario: Sin persistencia de dominio
- **WHEN** se recarga la aplicación después de crear un libro
- **THEN** el libro se recupera de la API y no existe una clave `libreria.libros` en `localStorage`

### Requirement: Preferencias locales
El frontend SHALL conservar en `localStorage` únicamente las preferencias de tema y estado de la sidebar; cualquier otro dato SHALL provenir de la API.

#### Scenario: Preferencias persistentes
- **WHEN** el usuario cambia el tema o colapsa la sidebar y recarga
- **THEN** el frontend conserva esas preferencias y vuelve a cargar los datos de dominio desde la API

### Requirement: Errores, carga y accesibilidad
El frontend SHALL mostrar estados de carga, vacío y error para cada vista, SHALL mapear los códigos 401, 403, 404, 409, 422, 429 y los fallos de red a mensajes en español, y SHALL mantener `aria-live`, foco visible, foco al primer campo inválido y uso de `textContent`/`createElement` para datos de usuario.

#### Scenario: Error de validación
- **WHEN** el backend responde 422 con errores de campo
- **THEN** el frontend muestra los mensajes junto a los campos, marca `aria-invalid` y enfoca el primer campo inválido

#### Scenario: Conflicto de stock o ISBN
- **WHEN** el backend responde 409 con un mensaje de stock o ISBN
- **THEN** el frontend muestra el mensaje en la región `role="alert"` sin recargar la página

#### Scenario: Límite de intentos
- **WHEN** el backend responde 429 con `Retry-After`
- **THEN** el frontend informa los segundos de espera y no reintenta automáticamente

#### Scenario: Fallo de red
- **WHEN** el backend no está disponible
- **THEN** el frontend muestra un mensaje de conexión con un botón "Reintentar" y no deja la vista en blanco

### Requirement: Servido por HTTP
El frontend SHALL funcionar servido por HTTP y SHALL detectar el protocolo `file:` para mostrar un aviso de que debe abrirse desde `http://localhost:8080` o la URL desplegada, sin intentar operaciones de API.

#### Scenario: Apertura por file://
- **WHEN** `index.html` se abre con `location.protocol === 'file:'`
- **THEN** el frontend muestra el aviso de servidor requerido y no realiza peticiones a `/api`
