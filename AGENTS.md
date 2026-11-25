# AGENTS.md — Gestor Solidario de Donativos y Alimentos

Documento de referencia para agentes de IA y desarrolladores que trabajen en este
repositorio. Describe la arquitectura real, el stack y las reglas **obligatorias**
del proyecto.

> **Precedencia:** este archivo es la fuente de verdad a nivel de repositorio. Los
> `AGENTS.md` dentro de `FrontEnd/` y `BackEnd/` contienen detalles de cada
> subproyecto, pero pueden estar desactualizados; si contradicen este documento,
> prevalecen las reglas de aquí.

---

## 1. Contexto del proyecto

Sistema de gestión de donativos y alimentos de **Pastoral San Pio X (Huancayo)**.
Permite al personal administrativo (Agente Pastoral) registrar usuarios, lotes de
donativos y actas de entrega, y ofrece un **Portal de Transparencia** de solo
lectura para donantes (padres, familias y alumnos).

- Idioma del dominio, textos de interfaz, nombres de archivos y clases: **español**.
- Identificadores de código: `snake_case` en Python, `camelCase` en TypeScript.
- La API expone y acepta JSON en **camelCase** (Pydantic lo genera con
  `alias_generator=to_camel` en `BackEnd/src/backend/schemas/base.py`).

---

## 2. Arquitectura y rutas reales

```text
GestionDonativos/
├── AGENTS.md                         # este documento
├── FrontEnd/                         # SPA Angular 22 (SSR)
│   ├── angular.json
│   ├── package.json
│   ├── public/images/Logo-SanPioX.png
│   └── src/
│       ├── index.html                # Bootstrap 5.3 + Bootstrap Icons por CDN
│       ├── main.ts
│       ├── server.ts                 # servidor SSR Express 5
│       ├── styles.css                # tokens de diseño globales
│       ├── environments/environment.ts
│       └── app/
│           ├── app.config.ts
│           ├── app.routes.ts
│           ├── app.routes.server.ts
│           ├── pages/                # páginas enrutadas
│           ├── components/           # secciones reutilizables
│           ├── shared/               # utilidades de UI
│           └── core/
│               ├── data/             # datos mock
│               ├── forms/            # esquemas de formularios
│               ├── guards/           # authGuard / adminGuard
│               ├── models/           # interfaces y tipos
│               ├── services/         # estado con Signals + HTTP
│               └── utils/            # api.utils.ts
├── BackEnd/                          # API FastAPI (Python 3.13, uv)
│   ├── pyproject.toml
│   ├── uv.lock
│   ├── .python-version
│   └── src/backend/
│       ├── main.py                   # app FastAPI, CORS, routers, errores
│       ├── apis/                     # routers HTTP por dominio
│       │   ├── donativos.py
│       │   ├── lotes.py
│       │   ├── transparencia.py
│       │   └── usuarios.py
│       ├── services/                 # reglas de negocio
│       │   ├── donativos.py
│       │   ├── fechas.py
│       │   ├── lotes.py
│       │   ├── transparencia.py
│       │   └── usuarios.py
│       ├── repositories/             # persistencia (hoy en memoria)
│       │   ├── base.py
│       │   ├── lotes.py
│       │   ├── semilla.py
│       │   ├── transparencia.py
│       │   └── usuarios.py
│       └── schemas/                  # Pydantic (contratos camelCase)
│           ├── base.py
│           ├── catalogos.py
│           ├── donativo.py
│           ├── lote.py
│           ├── transparencia.py
│           └── usuario.py
└── DataBase/
    └── db_donativos_sanpiox.sql      # script MySQL completo (esquema + datos)
```

### 2.1 FrontEnd (`FrontEnd/`)

- Aplicación **Angular 22 standalone** (sin NgModules), con **SSR** habilitado
  (`outputMode: "server"`, `src/server.ts` con Express 5).
- `src/app/pages/` contiene las páginas enrutadas:
  `login-principal`, `panel-control-principal`, `panel-gestor-usuarios`,
  `registro-donativos`, `transparencia`.
- `src/app/components/` contiene secciones reutilizables (`header`, `footer`,
  `login`, `gestion-lotes`, `gestor-usuarios`, `metas-donacion`,
  `linea-tiempo`, `trazabilidad-donacion`, `alerta-caducidad`,
  `targetas-superiores`, `resumen`, etc.).
- Cada componente es una carpeta de 4 archivos: `nombre.ts`, `.html`, `.css`,
  `.spec.ts`. El selector es `app-<kebab-folder>`.
- `src/app/core/services/` usa **Signals** para el estado (`signal`, `computed`,
  `asReadonly`) y `HttpClient` para la API.
- `src/app/core/guards/auth.guard.ts` define:
  - `authGuard`: exige sesión activa; si no hay, redirige a `/inicio`.
  - `adminGuard`: exige sesión y rol administrativo; si es donante, redirige a
    `/panel-control`.
- `src/app/core/data/mock-data.ts` y `AuthService` aún conservan datos/credenciales
  demo. El resto de servicios ya consume la API real.

### 2.2 BackEnd (`BackEnd/`)

Arquitectura por capas, en este orden:

```text
apis/ (HTTP)  →  services/ (reglas de negocio)  →  repositories/ (persistencia)
```

- **`apis/`**: routers de FastAPI con prefijo `/api`. Solo traducen HTTP;
  delegan la lógica en `services/`.
- **`services/`**: cálculos y validaciones de negocio (peso neto, código de lote,
  alertas, KPIs, metas, CRUD de usuarios).
- **`repositories/`**: acceso a datos. **Aquí debe vivir todo el SQL.** Hoy son
  repositorios en memoria (`RepositorioMemoria` en `repositories/base.py`); deben
  migrarse a MySQL respetando la misma interfaz pública.
- **`schemas/`**: modelos Pydantic de entrada/salida. Responden en camelCase.
- **`main.py`**: instancia de FastAPI, CORS, manejador de errores de validación e
  inclusión de routers.

Punto de entrada real: `backend.main:app`.

### 2.3 Base de datos (`DataBase/db_donativos_sanpiox.sql`)

Script MySQL que crea la base `db_donativos_sanpiox` (`utf8mb4`,
`utf8mb4_unicode_ci`) con:

| Tabla | Propósito |
|---|---|
| `usuarios` | Login y control de acceso por rol (`Administrativo` / `Donante`). |
| `donantes` | Procedencia del donativo (familia/alumno, empresa, anónimo). |
| `categorias_viveres` | Categorías y meta de campaña en kg. |
| `donaciones` | Lotes recepcionados; solo los registra el Agente Pastoral. |
| `detalle_donaciones` | Artículos del lote (cantidad, unidad, peso, vencimiento). |
| `entregas_transparencia` | Actas y entregas publicadas en Transparencia. |

Vistas existentes: `vw_resumen_donaciones` y `vw_metas_transparencia`.

El script incluye datos de prueba. **Sus contraseñas están hasheadas con SHA-256**
(`SHA2(..., 256)`), lo cual es incompatible con la regla obligatoria de Argon2;
deben regenerarse al migrar (ver §5.2).

---

## 3. Stack tecnológico

### Frontend

| Tecnología | Uso |
|---|---|
| Angular 22 | SPA standalone, SSR, rutas, formularios |
| TypeScript ~6.0 | Lenguaje |
| Signals | Estado reactivo en servicios (`signal`, `computed`) |
| Guards funcionales | `authGuard`, `adminGuard` |
| Bootstrap 5.3.9 | Estilos, cargado por **CDN** en `src/index.html` |
| Bootstrap Icons 1.13.2 | Iconografía por CDN |
| Vitest 5 | Pruebas unitarias (`*.spec.ts`) |
| npm 11.19.1 | Gestor de paquetes (`package-lock.json` versionado) |

> Bootstrap **no** es dependencia npm: no ejecutar `npm install bootstrap` ni
> agregarlo a `angular.json`.

### Backend

| Tecnología | Uso |
|---|---|
| Python >= 3.13 | Runtime (`BackEnd/.python-version`) |
| FastAPI >= 0.165 | API HTTP |
| Uvicorn >= 0.54 | Servidor ASGI |
| Pydantic v2 | Esquemas y validación (camelCase) |
| **uv** | Gestor de paquetes y entorno (`uv.lock` versionado) |

### Base de datos

| Tecnología | Uso |
|---|---|
| MySQL | Motor de persistencia |
| `db_donativos_sanpiox` | Nombre exacto de la base |
| SQL directo | Sin ORM (ver §5.1) |

---

## 4. Comandos

### Frontend (desde `FrontEnd/`)

```bash
npm install                 # instalar dependencias
npm start                   # dev server en http://localhost:4200
npm run build               # build de producción (incluye SSR)
npm test                    # Vitest; usar --watch=false para una sola ejecución
npm run serve:ssr:GestionDonativos
```

### Backend (desde `BackEnd/`)

```bash
uv sync                                        # instalar entorno desde uv.lock
uv run uvicorn backend.main:app --reload       # API en http://localhost:8000
uv add <paquete>                               # añadir dependencia (actualiza uv.lock)
uv run pytest                                  # pruebas (añadir pytest/httpx si faltan)
```

Nunca editar `uv.lock` a mano.

### Base de datos

```bash
mysql -u root -p < DataBase/db_donativos_sanpiox.sql
```

> El script hace `DROP DATABASE IF EXISTS db_donativos_sanpiox`: **destruye los
> datos existentes**. No ejecutarlo contra una base con información real sin
> respaldo.

---

## 5. Reglas obligatorias del backend

### 5.1 MySQL sin ORM, SQL directo y parametrizado

- La persistencia debe usar **MySQL** sobre la base **`db_donativos_sanpiox`**.
- **Prohibido usar ORM**: nada de SQLAlchemy, Peewee, Tortoise, Django ORM ni
  similares.
- Todo el acceso a datos debe concentrarse en `BackEnd/src/backend/repositories/`.
  Los routers (`apis/`) y servicios (`services/`) **no** ejecutan SQL.
- Usar un driver MySQL (por ejemplo `mysql-connector-python` o `PyMySQL`) con
  cursor y parámetros.
- Todas las consultas deben ser **parametrizadas con `%s`**:

  ```python
  # Correcto
  cursor.execute(
      "SELECT id_usuario, codigo_usuario, nombre_completo "
      "FROM usuarios WHERE correo_electronico = %s",
      (correo,),
  )

  # Prohibido: interpolación/f-strings en SQL (riesgo de inyección)
  cursor.execute(f"SELECT * FROM usuarios WHERE correo_electronico = '{correo}'")
  ```

- Usar transacciones (`commit` / `rollback`) en operaciones multi-tabla:
  registrar una donación implica `donaciones` + `detalle_donaciones`; registrar
  un acta implica `entregas_transparencia`.
- Cerrar conexiones/cursors con context managers o `try/finally`.
- Configurar credenciales por variables de entorno (nunca hardcodear ni versionar
  secretos): `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`
  (`db_donativos_sanpiox`).
- Mantener la interfaz de los repositorios actuales para que `services/` no
  dependa del motor de persistencia.

### 5.2 Contraseñas con Argon2 y autenticación JWT

- Hashear y verificar contraseñas con **`argon2-cffi`** (`PasswordHasher`).
  - Al crear o cambiar contraseña: `hash(password)` y guardar solo el hash.
  - Al iniciar sesión: `verify(hash_guardado, password)`.
  - Nunca almacenar, registrar ni devolver contraseñas en texto plano.
  - Nunca devolver `password_hash` en respuestas de la API.
- La columna `usuarios.password_hash` del script SQL es `CHAR(64)` (tamaño de
  SHA-256) y **no cabe un hash Argon2**. Debe migrarse a `VARCHAR(255)`.
- Regenerar con Argon2 los hashes de los usuarios semilla del script.
- Autenticación mediante **JWT**:
  - Firmar con un secreto leído de entorno (`JWT_SECRET`), algoritmo HS256.
  - Incluir al menos `sub` (identificador del usuario) y `rol`.
  - Definir expiración (`JWT_EXPIRATION_MINUTES`) y validarla en cada petición.
  - Proteger los endpoints con una dependencia de FastAPI que extraiga y valide el
    token `Authorization: Bearer <token>`.
  - La dependencia de autorización debe comparar el rol del token con el rol
    requerido por el endpoint y responder `401` (sin token/inválido) o `403`
    (autenticado sin permiso).
- Los roles de la API se manejan en minúsculas (`administrativo`, `donante`);
  en la base de datos se almacenan como `Administrativo` y `Donante`. La
  conversión debe hacerse en la capa de repositorio/servicio, no en el frontend.
- Endpoints de autenticación previstos:
  `POST /api/auth/login`, `POST /api/auth/logout`, `GET /api/auth/sesion`,
  `POST /api/auth/recuperacion`.

### 5.3 CORS obligatorio

`BackEnd/src/backend/main.py` debe permitir peticiones desde el frontend Angular:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200",
        "http://127.0.0.1:4200",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

- El origen principal exigido es **`http://localhost:4200`**; se mantiene
  `http://127.0.0.1:4200` porque el frontend usa `environment.apiURL =
  http://127.0.0.1:8000` y puede abrirse con cualquiera de los dos hosts.
- No usar `allow_origins=["*"]` junto con `allow_credentials=True`.

### 5.4 Contratos y errores

- Prefijo de API: `/api`.
- Cuerpos y respuestas en **camelCase**; fechas en **ISO 8601 UTC**.
- Errores con `detail` en español. `RequestValidationError` ya se transforma en
  `400` con `{ "detail": "Datos invalidos.", "errores": [...] }`.
- Códigos esperados: `400` validación, `401` no autenticado, `403` sin permiso,
  `404` no encontrado, `500` error inesperado.
- Las reglas de negocio (peso neto, código de lote, alertas, KPIs, metas) viven en
  el backend; no duplicarlas en Angular.

---

## 6. Lógica de negocio y roles (`usuarios`)

### 6.1 Tabla `usuarios`

Columnas relevantes:

| Columna | Descripción |
|---|---|
| `id_usuario` | PK autoincremental. |
| `codigo_usuario` | Código único: `A###` para administrativos, `U###` para donantes. |
| `nombre_completo` | Nombre visible. |
| `correo_electronico` | Credencial de acceso (único). |
| `password_hash` | Hash Argon2 (debe migrarse a `VARCHAR(255)`). |
| `telefono` | Opcional. |
| `tipo_usuario` | `ENUM('Administrativo', 'Donante')`. |
| `creado_por_id` | FK al administrativo que creó la cuenta (`NULL` para el primero). |
| `estado` | `1` activo, `0` bloqueado/inactivo. |
| `fecha_creacion`, `fecha_actualizacion` | Auditoría. |

### 6.2 Roles y permisos

| Rol (BD / API) | Perfil | Permisos |
|---|---|---|
| **`Administrativo`** / `administrativo` | Agente Pastoral | **Único autorizado** para: crear usuarios, registrar lotes de donativos y registrar actas de entrega. Además, CRUD de usuarios, cambio de estado de lotes, exportaciones y lectura completa. |
| **`Donante`** / `donante` | Padres, familias o alumnos | **Solo lectura del Portal de Transparencia**. No puede crear usuarios, registrar donativos/lotes ni actas. |

Reglas de aplicación:

- `POST /api/usuarios` → solo `Administrativo`. Un donante recibe `403`.
- `POST /api/donativos` y `POST /api/lotes` → solo `Administrativo`.
- Registro de actas (`entregas_transparencia`) → solo `Administrativo`.
- `PUT`/`DELETE /api/usuarios/{id}`, `PUT /api/lotes/{id}/estado` y cualquier
  mutación → solo `Administrativo`.
- `GET /api/transparencia/*` → lectura permitida para `Donante` y público en
  general (portal de transparencia). Nunca debe exponer datos personales de
  usuarios ni hashes.
- Los endpoints de inventario, usuarios y donativos no son accesibles para el rol
  `Donante`.
- La autorización **debe validarse en el backend**; los guards de Angular son solo
  UX, no seguridad.

### 6.3 Mapeo de estados

| Base de datos | API |
|---|---|
| `Nuevo` | `pendiente` |
| `En Almacén` | `preparacion` |
| `Entregado` | `entregado` |

Tipos de donante: BD `Familia / Alumno`, `Empresa / Aliado`, `Anónimo` ↔ API
`familia`, `empresa`, `anonimo`.

---

## 7. Endpoints actuales y autorización objetivo

| Método | Ruta | Rol requerido | Estado |
|---|---|---|---|
| `GET` | `/api/lotes` | Administrativo | Implementado (en memoria) |
| `GET` | `/api/lotes/alertas` | Administrativo | Implementado (en memoria) |
| `GET` | `/api/lotes/kpis` | Administrativo | Implementado (en memoria) |
| `GET` | `/api/lotes/exportar.csv` | Administrativo | Implementado (en memoria) |
| `GET` | `/api/lotes/{id}` | Administrativo | Implementado (en memoria) |
| `POST` | `/api/lotes` | **Administrativo** | Implementado (en memoria) |
| `PUT` | `/api/lotes/{id}/estado` | **Administrativo** | Implementado (en memoria) |
| `POST` | `/api/donativos` | **Administrativo** | Implementado (en memoria) |
| `GET` | `/api/usuarios` | Administrativo | Implementado (en memoria) |
| `POST` | `/api/usuarios` | **Administrativo** | Implementado (en memoria) |
| `PUT` | `/api/usuarios/{id}` | Administrativo | Implementado (en memoria) |
| `DELETE` | `/api/usuarios/{id}` | Administrativo | Implementado (en memoria) |
| `GET` | `/api/transparencia/metas` | Público / Donante (lectura) | Implementado (en memoria) |
| `GET` | `/api/transparencia/hitos` | Público / Donante (lectura) | Implementado (en memoria) |
| `GET` | `/api/transparencia/estadisticas` | Público / Donante (lectura) | Implementado (en memoria) |
| `POST` | `/api/auth/login` | Público | **Pendiente** |
| `POST` | `/api/auth/logout` | Autenticado | **Pendiente** |
| `GET` | `/api/auth/sesion` | Autenticado | **Pendiente** |
| `POST` | `/api/auth/recuperacion` | Público | **Pendiente** |
| `POST` | `/api/entregas` | **Administrativo** | **Pendiente** (actas de entrega) |

---

## 8. Frontend: rutas, guards y estado

Rutas reales en `FrontEnd/src/app/app.routes.ts`:

| Ruta | Componente | Guard |
|---|---|---|
| `''` | `LoginPrincipal` | — |
| `inicio` | `LoginPrincipal` | — |
| `transparencia` | `Transparencia` | — (pública, solo lectura) |
| `registrar_encomienda` | `RegistroDonativos` | `authGuard` |
| `panel-control` | `PanelControlPrincipal` | `authGuard` |
| `gestor-usuarios` | `PanelGestorUsuarios` | `adminGuard` |
| `**` | redirige a `inicio` | — |

- `AuthService` mantiene la sesión en un `signal` y en `localStorage`
  (`gestion-donativos:sesion`), pero **aún usa credenciales demo** de
  `core/data/mock-data.ts`. Debe migrarse a `POST /api/auth/login`, guardar el JWT
  y enviarlo en el header `Authorization: Bearer <token>`.
- `LoteService`, `TransparenciaService`, `UsuarioService` y
  `DonativoDraftService` ya usan `HttpClient` contra `environment.apiURL`.
- `environment.apiURL` es `http://127.0.0.1:8000`. El backend debe escuchar en
  `8000` y permitir CORS desde `4200`.
- Mantener el patrón de estado con Signals y componentes standalone.
- No romper el SSR: proteger `window`, `document`, `localStorage`, etc. con
  `isPlatformBrowser`.
- Los guards solo controlan navegación; la seguridad real es responsabilidad del
  backend.

---

## 9. Convenciones de trabajo

- No renombrar carpetas existentes aunque parezcan mal escritas (por ejemplo
  `targetas-superiores`) ni hacer formateos masivos.
- No modificar `node_modules/`, `dist/`, `.angular/` ni archivos generados.
- No versionar secretos, `.env`, `__pycache__/`, `.venv/` ni artefactos de build.
- Añadir dependencias Python con `uv add` (nunca editar `uv.lock` a mano).
- Añadir dependencias npm con `npm install` y conservar `package-lock.json`.
- Mantener los nombres de dominio y mensajes de error en español.
- Cualquier cambio de esquema debe reflejarse en
  `DataBase/db_donativos_sanpiox.sql` y en los esquemas Pydantic.

---

## 10. Brechas actuales que deben cerrarse (obligatorio)

1. Sustituir los repositorios en memoria por implementaciones MySQL con SQL
   parametrizado (`%s`) en `BackEnd/src/backend/repositories/`.
2. Añadir `argon2-cffi`, un driver MySQL y una librería JWT (`PyJWT` o
   `python-jose`) con `uv add`.
3. Migrar `usuarios.password_hash` de `CHAR(64)` a `VARCHAR(255)` y regenerar los
   hashes semilla con Argon2.
4. Implementar los endpoints `/api/auth/*` y la dependencia de autorización por
   rol (`Administrativo` / `Donante`).
5. Implementar el registro de actas de entrega (`entregas_transparencia`),
   restringido a `Administrativo`.
6. Migrar `AuthService` del frontend de credenciales demo a JWT real y adjuntar el
   token en las peticiones protegidas.
7. Verificar que CORS siga permitiendo `http://localhost:4200` (y
   `http://127.0.0.1:4200`) con credenciales.

---

## 11. Criterios de aceptación

- Un `Administrativo` puede iniciar sesión, crear usuarios, registrar lotes y
  actas, y consultar todo el sistema.
- Un `Donante` puede iniciar sesión y consultar únicamente el Portal de
  Transparencia; cualquier intento de mutación o acceso a usuarios/lotes/donativos
  responde `403`.
- Las contraseñas se almacenan y verifican con Argon2; nunca se devuelven en las
  respuestas.
- Las peticiones protegidas exigen un JWT válido y vigente.
- Todas las consultas MySQL usan parámetros `%s` y viven en `repositories/`.
- El frontend en `http://localhost:4200` puede consumir la API sin errores de CORS.
- El script `DataBase/db_donativos_sanpiox.sql` refleja el esquema real usado por
  el backend.
