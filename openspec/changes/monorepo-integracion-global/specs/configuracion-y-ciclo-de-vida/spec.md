## ADDED Requirements

### Requirement: Orígenes CORS configurables
La aplicación SHALL leer `CORS_ORIGINS` como una lista separada por comas, con valor por defecto `http://localhost:8080,http://127.0.0.1:8080`, y SHALL configurar `CORSMiddleware` con esos orígenes explícitos, `allow_credentials=True`, los métodos `GET`, `POST`, `PATCH`, `DELETE`, `OPTIONS` y la cabecera `Content-Type`; MUST NOT usar `*` cuando las credenciales están habilitadas.

#### Scenario: Origen permitido
- **WHEN** se envía un preflight `OPTIONS /auth/login` con `Origin: http://localhost:8080`
- **THEN** la respuesta incluye `Access-Control-Allow-Origin: http://localhost:8080` y `Access-Control-Allow-Credentials: true`

#### Scenario: Origen no permitido
- **WHEN** se envía una petición con un `Origin` que no figura en `CORS_ORIGINS`
- **THEN** la respuesta no incluye `Access-Control-Allow-Origin` y el navegador bloquea la lectura

#### Scenario: Lista vacía
- **WHEN** `CORS_ORIGINS` está vacía
- **THEN** la aplicación arranca sin orígenes CORS permitidos y no habilita credenciales para ningún origen
