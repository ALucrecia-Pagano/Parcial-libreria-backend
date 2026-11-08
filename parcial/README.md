# Parcial Programación III — Librería (capítulos 1 a 6)

**Tecnicatura Universitaria en Programación — UTN FRM — Comisión 4**

## Integrantes

- Pagano Amanda
- Liendo Mateo
- Avila Lucas
- Valentini Tiziano
- García Juan

## Qué agrega el parcial respecto del TP

- **Configuración** con `Settings` (pydantic-settings): la base se arma desde variables `POSTGRES_*`; `POSTGRES_PASSWORD` y `JWT_SECRET` son obligatorias y sin valor por defecto.
- **Usuarios y roles** (ADMIN, VENDEDOR, CLIENTE) con vigencia, alta de personal y autoprotección del administrador.
- **Autenticación** con bcrypt y JWT en una cookie `HttpOnly`; límite de intentos con 429 y registro de cada intento en una sesión propia.
- **Autorización** con dos grupos de rutas (abierto y protegido), roles leídos de la base y cambio obligatorio de contraseña.
- **Repositorios y Unit of Work** en todos los módulos (`BaseRepository`, `SoftDeleteRepository`, `UnitOfWork`).
- **Stock con movimientos**: un único punto de escritura, reposición, baja lógica de libros y un disparador que impide modificar o borrar movimientos.
- **Ventas** que descuentan stock en una sola transacción, `/mis-ventas` y control del dueño de la venta.
- **Paginación** con el envoltorio `{items, total, page, size, pages}`.

## Cómo levantarlo desde cero

Pasos para Windows con Git Bash. Requiere Python 3.12 o superior y PostgreSQL 16 o superior.

1. Entrá a la carpeta del proyecto:
   ```bash
   cd parcial
   ```
2. Creá y activá el entorno virtual:
   ```bash
   py -3.12 -m venv .venv
   source .venv/Scripts/activate
   ```
3. Instalá las dependencias:
   ```bash
   pip install -r requirements.txt
   ```
4. Creá el archivo `.env` a partir de la plantilla:
   ```bash
   cp env.example .env
   ```
   Completá `POSTGRES_PASSWORD` con la contraseña de tu PostgreSQL y `JWT_SECRET` con una clave de firma generada así:
   ```bash
   python -c "import secrets;print(secrets.token_hex(32))"
   ```
   Si tu PostgreSQL no usa el puerto 5432, cambiá también `POSTGRES_PORT`. Sin `POSTGRES_PASSWORD` o sin `JWT_SECRET`, la aplicación y Alembic no arrancan.
5. Creá la base vacía:
   ```bash
   psql -U postgres -c "CREATE DATABASE libreria;"
   ```
6. Aplicá las migraciones:
   ```bash
   alembic upgrade head
   ```
7. Cargá los datos iniciales:
   ```bash
   python seed.py
   ```
   El script vacía todas las tablas y vuelve a cargar los datos, así que se puede correr las veces que haga falta. Se corre antes de cada archivo de prueba.
8. Levantá el servidor:
   ```bash
   uvicorn app.main:app --reload --reload-dir app
   ```
9. Abrí la documentación de la API en http://localhost:8000/docs

## Datos iniciales

La contraseña ficticia común de los usuarios está en la constante `PASSWORD_SEED` de `seed.py`.

| Usuario | Rol | Debe cambiar la contraseña |
|---|---|---|
| `admin@example.com` | ADMIN | no |
| `admin2@example.com` | ADMIN | no |
| `vendedor@example.com` | VENDEDOR | no |
| `ana@example.com` | CLIENTE | no |
| `nuevo@example.com` | VENDEDOR | sí |

Además: 3 editoriales, 3 géneros, 6 autores, 5 libros (Rayuela, Antología de la literatura fantástica, Ficciones, Respiración artificial y Bestiario), 3 clientes (Lucía Fernández, Tomás Ríos y Ana Paz) y la venta 1 de Lucía por 69000.00. El stock de cada libro coincide con la suma de sus movimientos.

## Casos de prueba

Cada caso está en `test/`, con la respuesta esperada en un comentario. Antes de cada archivo se corre `python seed.py`.

| Caso | Archivo |
|---|---|
| C-01 | `test/C-01_param_no_entero.http` |
| C-02 | `test/C-02_registro.http` |
| C-03 | `test/C-03_cookie.http` |
| C-04 | `test/C-04_anti_enumeracion.http` |
| C-05 | `test/C-05_limite_intentos.http` |
| C-06 | `test/C-06_401_vs_403.http` |
| C-07 | `test/C-07_revocar_rol.http` |
| C-08 | `test/C-08_autoproteccion.http` |
| C-09 | `test/C-09_cambio_obligatorio.http` |
| C-10 | `test/C-10_venta_valida.http` |
| C-11 | `test/C-11_venta_sin_stock.http` |
| C-12 | `test/C-12_venta_referencias_invalidas.http` |
| C-13 | `test/C-13_baja_reposicion_isbn.http` |
| C-14 | `test/solo_agregado.sql` (en psql) |
| C-15 | `test/C-15_sin_n_mas_1.http` (con `SQL_ECHO=true`) |
| C-16 | `test/C-16_busqueda_paginacion_patch.http` |

## Evidencia

En `evidencia/`:

- `C-14-solo-agregado.txt`: la salida de psql con el `UPDATE` y el `DELETE` sobre `movimiento_stock` rechazados por el disparador.
- `C-15-detalle-venta.txt`: las consultas del detalle de una venta con 2 renglones y de otra con 4; son las mismas en los dos casos.

## Despliegue

El despliegue no forma parte de este proyecto: se hizo con el TP de los capítulos 1 a 4, en la carpeta `despliegue/`, y está en línea en http://179.199.141.99:8000.