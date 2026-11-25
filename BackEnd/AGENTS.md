# AGENTS.md — BackEnd

## Contexto

`GestionDonativos` es el gestor solidario de donativos y alimentos de Pastoral San
Pio X (Huancayo). Este paquete es la API FastAPI que debe servir los datos de la
SPA Angular ubicada en `../FrontEnd`. Usuarios y texto de negocio en español.

Hoy el frontend funciona por completo con `src/app/core/data/mock-data.ts` y
servicios con `signal`; no hay llamadas HTTP. El objetivo del backend es
reemplazar esos mocks sin cambiar la forma de los datos que consume Angular.

## Estado actual

- Proyecto creado con `uv`: Python >=3.13, FastAPI >=0.165, Uvicorn >=0.54.
- `src/backend/main.py` solo contiene `app = FastAPI()`. No hay routers,
  modelos, persistencia ni pruebas.
- `src/backend/__init__.py` expone `main()` que imprime "Hello from backend!";
  es residual del scaffold. El punto de entrada real es `backend.main:app`.
- `README.md` está vacío y la descripción de `pyproject.toml` es la del
  scaffold. Este archivo es la fuente de verdad sobre el propósito del código.

## Comandos

Desde `BackEnd/`:

- `uv sync` — instala el entorno (hay `.venv` y `uv.lock` committed).
- `uv run uvicorn backend.main:app --reload` — servidor en `http://localhost:8000`.
  La SPA se sirve en `http://localhost:4200`: configurar CORS para ese origen.
- `uv add <paquete>` — añadir dependencias y actualizar `uv.lock` (nunca editar
  el lock a mano).
- `uv run pytest` — pruebas (añadir `pytest` y `httpx` como dependencias de dev
  si aún no están).

No hay scripts de lint ni formateo configurados.

## Estructura recomendada

```text
BackEnd/
  pyproject.toml
  uv.lock
  src/backend/
    main.py          # app FastAPI, CORS, include_router
    models/          # esquemas Pydantic (donativo, lote, usuario, auth, transparencia)
    routers/         # endpoints por dominio
    services/        # reglas de negocio y cálculos
    data/            # datos semilla (espejo de mock-data.ts)
  tests/
```

Convención: nombres de archivos y clases en español, snake_case en Python;
los modelos Pydantic usan alias `camelCase` para coincidir con TypeScript.

## Dominio (contrato con el frontend)

Fuentes de verdad: `../FrontEnd/src/app/core/models/` y
`../FrontEnd/src/app/core/data/mock-data.ts`.

- **Donativo (borrador)**: `donante` (`tipo`: `familia` | `empresa` | `anonimo`,
  `nombre`, `documento`, `gradoSeccion`, `telefono`), `articulos[]`
  (`id`, `categoria`, `descripcion`, `cantidad`, `unidad`: `Unid.` | `Kg` | `Paq.`,
  `pesoUnitarioKg`, `fechaVencimiento`), `observaciones` y `destino`.
  El peso neto es `sum(cantidad * pesoUnitarioKg)`, redondeado a 2 decimales.
- **Lote**: `id`, `codigo` (`#PX-LOT-2026-041`, secuencia por año),
  `fechaIngreso`, `categoriaPrincipal`, `descripcion`, `volumen` (kg), `unidad`,
  `destino`, `estado` (`pendiente` | `preparacion` | `entregado`),
  `familiasBeneficiadas` y `articulos[]`.
  Alertas: artículos con `diasRestantes <= 15` (fecha de vencimiento en UTC).
  KPIs: total acopiado, lotes activos, lotes entregados, artículos críticos.
- **Usuario**: `id` (`A###` administrativo, `U###` donante), `nombre`,
  `telefono`, `correo`, `rol` (`donante` | `administrativo`), `activo`.
- **Auth**: credenciales demo (`pastoral@sanpiox.edu.pe` / `admin123`,
  `donante@sanpiox.edu.pe` / `donante123`), sesión
  (`id`, `nombre`, `correo`, `rol`) y solicitudes de recuperación
  (`id`, `correo`, `fecha`, `atendida`).
- **Transparencia**: metas por categoría (`metaKg`, `recolectadoKg`), hitos
  derivados de lotes y estadísticas públicas (`totalKg`, `totalLotes`,
  `totalFamilias`).

Categorías de alimento y unidades: tomar las listas de `donativo.model.ts`.

## Endpoints previstos (contrato propuesto, aún no implementados)

Prefijo `/api`. Respuestas y cuerpos en `camelCase`.

- `GET /api/lotes` (búsqueda y paginación), `GET /api/lotes/{id}`,
  `POST /api/lotes`, `PATCH /api/lotes/{id}/estado`,
  `GET /api/lotes/alertas`, `GET /api/lotes/kpis`, `GET /api/lotes/exportar.csv`.
- `POST /api/donativos` — recibe el borrador y crea un lote en `pendiente`.
- `GET/POST /api/usuarios`, `PATCH/DELETE /api/usuarios/{id}`.
- `POST /api/auth/login`, `POST /api/auth/logout`, `GET /api/auth/sesion`,
  `POST /api/auth/recuperacion`.
- `GET /api/transparencia/metas`, `/hitos`, `/estadisticas`.

Errores con `detail` en español y códigos HTTP adecuados (400 validación,
401/403 auth, 404 no encontrado).

## Reglas de integración

- Serializar fechas como ISO 8601 en UTC. Las fechas de calendario
  (`type="date"`) se envían a medianoche UTC, igual que `fechaUTC()` en el
  frontend, para evitar desfases de zona horaria.
- Los cálculos (peso neto, código de lote, alertas, KPIs, metas) deben vivir en
  el backend; no duplicar reglas de negocio en Angular.
- Persistencia inicial: datos semilla en memoria (`data/`), sin base de datos.
  La estructura debe permitir sustituir el repositorio por SQLite/BD después
  sin cambiar los esquemas HTTP.
- No modificar `../FrontEnd` salvo que se pida explícitamente; el frontend
  seguirá con mocks hasta que se acuerde la migración a `HttpClient`.

## Pendientes / decisiones

- Auth real (hash de contraseñas, JWT o sesiones) en lugar de credenciales demo.
- Persistencia definitiva y migraciones.
- Definir si el prefijo `/api` se mantiene y cómo se proxyará desde Angular.
- Reemplazar el script residual `backend = "backend:main"` de `pyproject.toml`.
