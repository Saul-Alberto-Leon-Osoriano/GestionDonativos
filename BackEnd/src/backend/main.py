from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.apis import (
    router_auth,
    router_donativos,
    router_entregas,
    router_lotes,
    router_transparencia,
    router_usuarios,
)
from backend.config import obtener_settings
from backend.database import cerrar_pool, conexion, inicializar_pool


@asynccontextmanager
async def lifespan(_: FastAPI):
    inicializar_pool()
    yield
    cerrar_pool()


settings = obtener_settings()

app = FastAPI(
    title="Gestor Solidario de Donativos",
    version="0.1.0",
    description="API del gestor solidario de donativos y alimentos de Pastoral San Pio X.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def manejar_error_validacion(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    errores = []
    for error in exc.errors():
        ubicacion = [
            str(parte)
            for parte in error.get("loc", ())
            if parte not in ("body", "query")
        ]
        errores.append(
            {
                "campo": ".".join(ubicacion) or "cuerpo",
                "mensaje": error.get("msg", "Valor invalido."),
            }
        )
    return JSONResponse(
        status_code=400,
        content={"detail": "Datos invalidos.", "errores": errores},
    )


@app.get("/api/health", tags=["health"])
def health() -> dict[str, str]:
    with conexion() as conn:
        cur = conn.cursor()
        try:
            cur.execute("SELECT 1")
            cur.fetchone()
        finally:
            cur.close()
    return {"estado": "ok", "base_datos": settings.db_name}


app.include_router(router_auth)
app.include_router(router_lotes)
app.include_router(router_donativos)
app.include_router(router_usuarios)
app.include_router(router_entregas)
app.include_router(router_transparencia)
