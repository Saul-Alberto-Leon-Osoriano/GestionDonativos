import csv
import io
from datetime import datetime

from fastapi import HTTPException

from backend.repositories import RepositorioLotes
from backend.schemas import (
    AlertaVencimiento,
    DonativoDraft,
    EstadoLote,
    KpisInventario,
    Lote,
    LoteCrear,
    RespuestaPaginada,
)

from .donativos import (
    calcular_peso_neto,
    categoria_principal,
    descripcion_lote,
    redondear,
)
from .fechas import dias_hasta, normalizar_utc, utc_actual


class ServicioLotes:
    """Reglas de negocio y consultas sobre lotes."""

    def __init__(self, repositorio: RepositorioLotes) -> None:
        self._repositorio = repositorio

    def listar(
        self,
        termino: str | None = None,
        estado: EstadoLote | None = None,
        categoria: str | None = None,
    ) -> list[Lote]:
        return self._repositorio.listar(termino, estado, categoria)

    def listar_paginado(
        self,
        termino: str | None,
        estado: EstadoLote | None,
        categoria: str | None,
        pagina: int,
        tamano_pagina: int,
    ) -> RespuestaPaginada[Lote]:
        items, total = self._repositorio.listar_paginado(
            termino, estado, categoria, pagina, tamano_pagina
        )
        return RespuestaPaginada(
            items=items,
            total=total,
            pagina=pagina,
            tamano_pagina=tamano_pagina,
        )

    def obtener(self, id_lote: str) -> Lote:
        lote = self._repositorio.obtener_por_id(id_lote)
        if lote is None:
            raise HTTPException(status_code=404, detail="Lote no encontrado.")
        return lote

    def _validar(self, datos: LoteCrear) -> None:
        if not datos.categoria_principal.strip():
            raise HTTPException(
                status_code=400,
                detail="La categoria principal del lote es obligatoria.",
            )
        if not datos.destino.strip():
            raise HTTPException(
                status_code=400,
                detail="El destino del lote es obligatorio.",
            )
        for articulo in datos.articulos:
            if articulo.fecha_vencimiento is None:
                raise HTTPException(
                    status_code=400,
                    detail="La fecha de vencimiento es obligatoria para cada articulo.",
                )

    def crear(self, datos: LoteCrear, id_agente_pastoral: int) -> Lote:
        self._validar(datos)
        if datos.fecha_ingreso is not None:
            datos = datos.model_copy(
                update={"fecha_ingreso": normalizar_utc(datos.fecha_ingreso)}
            )
        return self._repositorio.crear(datos, id_agente_pastoral)

    def crear_desde_donativo(
        self, draft: DonativoDraft, id_agente_pastoral: int
    ) -> Lote:
        if not draft.destino or not draft.destino.strip():
            raise HTTPException(
                status_code=400,
                detail="El destino del donativo es obligatorio.",
            )

        resumen = calcular_peso_neto(draft.articulos)
        descripcion = (
            f"{descripcion_lote(draft)} | Peso neto: {resumen:.2f} kg"
        )
        datos = LoteCrear(
            fecha_ingreso=normalizar_utc(utc_actual()),
            categoria_principal=categoria_principal(draft.articulos),
            descripcion=descripcion,
            unidad="Kg",
            destino=draft.destino.strip(),
            estado=EstadoLote.PENDIENTE,
            familias_beneficiadas=0,
            articulos=draft.articulos,
        )
        self._validar(datos)
        return self._repositorio.crear_desde_donativo(
            draft, datos, id_agente_pastoral
        )

    def cambiar_estado(self, id_lote: str, estado: EstadoLote) -> Lote:
        lote = self._repositorio.actualizar_estado(id_lote, estado)
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
        lotes = self._repositorio.listar(termino, estado, categoria)
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
