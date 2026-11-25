import csv
import io
from datetime import datetime

from fastapi import HTTPException

from backend.repositories import RepositorioLotes
from backend.schemas import (
    AlertaVencimiento,
    EstadoLote,
    KpisInventario,
    Lote,
    LoteCrear,
    RespuestaPaginada,
)

from .donativos import calcular_peso_neto, redondear
from .fechas import dias_hasta, normalizar_utc, utc_actual


def generar_codigo_lote(lotes: list[Lote], fecha_ingreso: datetime) -> str:
    anio = fecha_ingreso.year
    prefijo = f"#PX-LOT-{anio}-"
    secuencia = 0

    for lote in lotes:
        if not lote.codigo.startswith(prefijo):
            continue
        sufijo = lote.codigo[len(prefijo) :]
        if sufijo.isdigit():
            secuencia = max(secuencia, int(sufijo))

    return f"{prefijo}{secuencia + 1:03d}"


def generar_id_lote(lotes: list[Lote], secuencia: int) -> str:
    ids_existentes = {lote.id for lote in lotes}
    while True:
        candidato = f"lote-{secuencia:03d}"
        if candidato not in ids_existentes:
            return candidato
        secuencia += 1


class ServicioLotes:
    """Reglas de negocio y consultas sobre lotes."""

    def __init__(self, repositorio: RepositorioLotes) -> None:
        self._repositorio = repositorio

    def _filtrar(
        self,
        termino: str | None,
        estado: EstadoLote | None,
        categoria: str | None,
    ) -> list[Lote]:
        lotes = self._repositorio.listar()

        if termino and termino.strip():
            texto = termino.strip().casefold()
            lotes = [
                lote
                for lote in lotes
                if texto
                in " ".join(
                    (
                        lote.id,
                        lote.codigo,
                        lote.categoria_principal,
                        lote.descripcion,
                        lote.destino,
                    )
                ).casefold()
            ]

        if estado is not None:
            lotes = [lote for lote in lotes if lote.estado == estado]

        if categoria and categoria.strip():
            categoria_texto = categoria.strip().casefold()
            lotes = [
                lote
                for lote in lotes
                if categoria_texto in lote.categoria_principal.casefold()
            ]

        return sorted(lotes, key=lambda lote: lote.fecha_ingreso, reverse=True)

    def listar(
        self,
        termino: str | None = None,
        estado: EstadoLote | None = None,
        categoria: str | None = None,
    ) -> list[Lote]:
        return self._filtrar(termino, estado, categoria)

    def listar_paginado(
        self,
        termino: str | None,
        estado: EstadoLote | None,
        categoria: str | None,
        pagina: int,
        tamano_pagina: int,
    ) -> RespuestaPaginada[Lote]:
        lotes = self._filtrar(termino, estado, categoria)
        inicio = (pagina - 1) * tamano_pagina
        return RespuestaPaginada(
            items=lotes[inicio : inicio + tamano_pagina],
            total=len(lotes),
            pagina=pagina,
            tamano_pagina=tamano_pagina,
        )

    def obtener(self, id_lote: str) -> Lote:
        lote = self._repositorio.obtener_por_id(id_lote)
        if lote is None:
            raise HTTPException(status_code=404, detail="Lote no encontrado.")
        return lote

    def crear(self, datos: LoteCrear) -> Lote:
        if not datos.categoria_principal.strip():
            raise HTTPException(
                status_code=400, detail="La categoria principal del lote es obligatoria."
            )
        if not datos.destino.strip():
            raise HTTPException(status_code=400, detail="El destino del lote es obligatorio.")

        fecha_ingreso = (
            normalizar_utc(datos.fecha_ingreso)
            if datos.fecha_ingreso is not None
            else utc_actual()
        )
        lotes_existentes = self._repositorio.listar()
        codigo = generar_codigo_lote(lotes_existentes, fecha_ingreso)
        secuencia = int(codigo.rsplit("-", 1)[1])
        id_lote = generar_id_lote(lotes_existentes, secuencia)

        lote = Lote(
            id=id_lote,
            codigo=codigo,
            fecha_ingreso=fecha_ingreso,
            categoria_principal=datos.categoria_principal.strip(),
            descripcion=datos.descripcion,
            volumen=calcular_peso_neto(datos.articulos),
            unidad=datos.unidad,
            destino=datos.destino.strip(),
            estado=datos.estado,
            familias_beneficiadas=datos.familias_beneficiadas,
            articulos=datos.articulos,
        )
        return self._repositorio.crear(lote)

    def cambiar_estado(self, id_lote: str, estado: EstadoLote) -> Lote:
        lote = self._repositorio.actualizar(id_lote, {"estado": estado})
        if lote is None:
            raise HTTPException(status_code=404, detail="Lote no encontrado.")
        return lote

    def eliminar(self, id_lote: str) -> None:
        if not self._repositorio.eliminar(id_lote):
            raise HTTPException(status_code=404, detail="Lote no encontrado.")

    def alertas(self) -> list[AlertaVencimiento]:
        alertas: list[AlertaVencimiento] = []
        for lote in self._repositorio.listar():
            for articulo in lote.articulos:
                if articulo.fecha_vencimiento is None:
                    continue
                dias_restantes = dias_hasta(articulo.fecha_vencimiento)
                if dias_restantes <= 15:
                    alertas.append(
                        AlertaVencimiento(
                            articulo_id=articulo.id,
                            lote_id=lote.id,
                            nombre=articulo.descripcion,
                            lote=lote.codigo,
                            fecha_vencimiento=articulo.fecha_vencimiento,
                            dias_restantes=dias_restantes,
                        )
                    )
        return sorted(alertas, key=lambda alerta: alerta.dias_restantes)

    def kpis(self) -> KpisInventario:
        lotes = self._repositorio.listar()
        return KpisInventario(
            total_acopiado=redondear(sum(lote.volumen for lote in lotes)),
            lotes_activos=sum(
                1 for lote in lotes if lote.estado != EstadoLote.ENTREGADO
            ),
            lotes_entregados=sum(
                1 for lote in lotes if lote.estado == EstadoLote.ENTREGADO
            ),
            articulos_criticos=len(self.alertas()),
        )

    def exportar_csv(
        self,
        termino: str | None,
        estado: EstadoLote | None,
        categoria: str | None,
    ) -> str:
        lotes = self._filtrar(termino, estado, categoria)
        buffer = io.StringIO(newline="")
        escribir = csv.writer(buffer)
        escribir.writerow(
            [
                "id",
                "codigo",
                "fechaIngreso",
                "categoriaPrincipal",
                "descripcion",
                "volumenKg",
                "unidad",
                "destino",
                "estado",
                "familiasBeneficiadas",
            ]
        )
        for lote in lotes:
            escribir.writerow(
                [
                    lote.id,
                    lote.codigo,
                    lote.fecha_ingreso.isoformat(),
                    lote.categoria_principal,
                    lote.descripcion,
                    f"{lote.volumen:.2f}",
                    lote.unidad.value,
                    lote.destino,
                    lote.estado.value,
                    lote.familias_beneficiadas,
                ]
            )
        return "\ufeff" + buffer.getvalue()
