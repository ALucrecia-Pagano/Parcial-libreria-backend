# Spec Delta — configuracion-y-ciclo-de-vida

## Purpose

Define cómo `parcial/` obtiene su configuración (del entorno, sin secretos en el código ni defaults para lo sensible) y cómo se crean y liberan los recursos compartidos (motor y fábrica de sesiones) durante la vida de la aplicación.

## ADDED Requirements

### Requirement: Variables de configuración reconocidas
La aplicación SHALL leer su configuración del entorno o de un `.env` local no versionado, con las variables `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `POSTGRES_HOST`, `POSTGRES_PORT`, `JWT_SECRET`, `JWT_MINUTOS`, `BCRYPT_COSTO`, `COOKIE_SECURE`, `DB_POOL_SIZE` y `SQL_ECHO`, validando su tipo.

#### Scenario: Configuración completa
- **WHEN** todas las variables están definidas con valores válidos
- **THEN** la aplicación arranca y usa esos valores

#### Scenario: Valor con tipo inválido
- **WHEN** `DB_POOL_SIZE` vale `abc`
- **THEN** la aplicación no arranca e informa qué variable es inválida, sin mostrar el valor de ningún secreto

### Requirement: Secretos sin valor por defecto
`POSTGRES_PASSWORD` y `JWT_SECRET` MUST NOT tener valor por defecto en el código; si falta cualquiera de los dos, ni la aplicación ni las migraciones SHALL arrancar.

#### Scenario: Falta la contraseña de la base
- **WHEN** se inicia `uvicorn app.main:app` sin `POSTGRES_PASSWORD` en el entorno ni en `.env`
- **THEN** el proceso termina con un error de configuración que nombra `POSTGRES_PASSWORD` y no queda escuchando en el puerto

#### Scenario: Falta el secreto de firma
- **WHEN** se inicia la aplicación sin `JWT_SECRET`
- **THEN** el proceso termina con un error de configuración que nombra `JWT_SECRET`

#### Scenario: Falta la contraseña al migrar
- **WHEN** se ejecuta `alembic upgrade head` sin `POSTGRES_PASSWORD`
- **THEN** Alembic falla antes de conectarse a la base

### Requirement: Dirección de la base derivada de la configuración
La dirección de conexión SHALL derivarse de `POSTGRES_*` con el dialecto asincrónico `postgresql+asyncpg`, y la misma dirección SHALL usarla la aplicación y Alembic. Ninguna dirección ni contraseña MUST figurar en archivos versionados.

#### Scenario: Alembic usa la configuración
- **WHEN** se ejecuta `alembic upgrade head` con `POSTGRES_*` definidas
- **THEN** Alembic se conecta a la base indicada por esas variables y no a ningún valor de `alembic.ini`

#### Scenario: Archivo de ejemplo sin secretos
- **WHEN** se lee `parcial/env.example`
- **THEN** lista todas las variables reconocidas, deja vacíos o con marcador `<definir>` `POSTGRES_PASSWORD` y `JWT_SECRET`, e indica cómo generar `JWT_SECRET`

#### Scenario: Un solo archivo de ejemplo y README coherente
- **WHEN** se revisa `parcial/`
- **THEN** no existe `parcial/.env.example`, el README indica copiar `env.example` a `.env` y completar `POSTGRES_PASSWORD` y `JWT_SECRET` sin mencionar `DATABASE_URL` ni `DEBUG`, y el comentario de `parcial/.gitignore` nombra `env.example` mientras `.env` sigue ignorado

### Requirement: Recursos creados y liberados en el ciclo de vida
El motor (con tamaño de pool `DB_POOL_SIZE` y eco de SQL según `SQL_ECHO`) y la fábrica de sesiones SHALL crearse una sola vez al arrancar la aplicación y liberarse al apagarla; no SHALL crearse por petición ni al importar módulos.

#### Scenario: Arranque y apagado
- **WHEN** la aplicación arranca y luego se detiene
- **THEN** el motor se crea una vez en el arranque y su pool se cierra en el apagado

#### Scenario: Eco de SQL
- **WHEN** `SQL_ECHO=true` y se atiende una petición que consulta la base
- **THEN** las consultas emitidas aparecen en la consola

### Requirement: Una sesión por petición
Cada petición que necesite la base SHALL recibir su propia sesión, obtenida de la fábrica del ciclo de vida, cerrada al terminar la petición y configurada para que los objetos sigan legibles después de confirmar.

#### Scenario: Sesión cerrada al terminar
- **WHEN** termina una petición que usó la base (con éxito o con error)
- **THEN** su sesión queda cerrada y la conexión vuelve al pool
