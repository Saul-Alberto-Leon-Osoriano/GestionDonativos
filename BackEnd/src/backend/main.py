from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.apis import (
    router_donativos,
    router_lotes,
    router_transparencia,
    router_usuarios,
)

app = FastAPI(
    title="Gestor Solidario de Donativos",
    version="0.1.0",
    description="API del gestor solidario de donativos y alimentos de Pastoral San Pio X.",
)

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


@app.exception_handler(RequestValidationError)
async def manejar_error_validacion(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    errores = []
    for error in exc.errors():
        ubicacion = [
            str(parte) for parte in error.get("loc", ()) if parte not in ("body", "query")
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


app.include_router(router_lotes)
app.include_router(router_donativos)
app.include_router(router_usuarios)
app.include_router(router_transparencia)
