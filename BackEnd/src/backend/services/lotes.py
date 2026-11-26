import csv
import io
from datetime import datetime

from fastapi import HTTPException

from backend.repositories import RepositorioEntregas, RepositorioLotes
from backend.schemas import (
    AlertaVencimiento,
    DonativoDraft,
    EntregaCrear,
    EstadoEntrega,
    EstadoLote,
    KpisInventario,
    Lote,
    LoteCrear,
    RespuestaPaginada,
    Usuario,
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

    def __init__(
        self,
        repositorio: RepositorioLotes,
        repositorio_entregas: RepositorioEntregas,
    ) -> None:
        self._repositorio = repositorio
        self._repositorio_entregas = repositorio_entregas

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

    def cambiar_estado(
        self,
        id_lote: str,
        estado: EstadoLote,
        admin: Usuario | None = None,
    ) -> Lote:
        if self._repositorio.obtener_por_id(id_lote) is None:
            raise HTTPException(status_code=404, detail="Lote no encontrado.")

        lote = self._repositorio.actualizar_estado(id_lote, estado)
        if lote is None:
            raise HTTPException(status_code=404, detail="Lote no encontrado.")

        if estado == EstadoLote.ENTREGADO:
            self._publicar_entrega(lote, admin)
        else:
            self._retirar_entrega(lote)

        return lote

    def _publicar_entrega(self, lote: Lote, admin: Usuario | None) -> None:
        """Refleja el lote entregado en el Portal de Transparencia."""

        id_donacion = int(lote.id)
        existente = self._repositorio_entregas.obtener_por_donacion(id_donacion)
        if existente is not None:
            if existente.estado_entrega != EstadoEntrega.ENTREGADO:
                self._repositorio_entregas.marcar_entregada_por_donacion(
                    id_donacion
                )
            return

        id_agente = (admin.id_usuario if admin else None) or (
            self._repositorio.obtener_agente_pastoral(lote.id)
        )
        if id_agente is None:
            raise HTTPException(
                status_code=400,
                detail="No se pudo identificar al agente pastoral del lote.",
            )

        datos = EntregaCrear(
            id_donacion=id_donacion,
            codigo_publico_lote=lote.codigo,
            titulo_entrega=self._titulo_entrega(lote),
            descripcion_entrega=self._descripcion_entrega(lote),
            coordinador_recepcion=self._responsable_entrega(admin),
            codigo_acta=self._repositorio_entregas.siguiente_codigo_acta(),
            estado_entrega=EstadoEntrega.ENTREGADO,
            fecha_entrega=utc_actual().date(),
        )
        self._repositorio_entregas.crear(datos, id_agente)

    def _retirar_entrega(self, lote: Lote) -> None:
        """Quita el hito publico cuando el lote deja de estar entregado."""

        self._repositorio_entregas.eliminar_por_donacion(int(lote.id))

    @staticmethod
    def _titulo_entrega(lote: Lote) -> str:
        return f"Entrega de donativos en {lote.destino}"[:180]

    @staticmethod
    def _descripcion_entrega(lote: Lote) -> str:
        total = len(lote.articulos)
        if total == 0:
            return (
                f"Entrega del lote {lote.codigo} ({lote.volumen:.2f} kg) "
                f"al destino solidario {lote.destino}."
            )

        detalle = "; ".join(
            f"{articulo.cantidad:g} {articulo.unidad.value} de "
            f"{articulo.descripcion}"
            for articulo in lote.articulos[:4]
        )
        if total > 4:
            detalle += f"; y {total - 4} articulo(s) mas"

        return (
            f"Entrega del lote {lote.codigo} con {total} tipo(s) de viveres "
            f"({lote.volumen:.2f} kg). Contenido: {detalle}. "
            f"Destino solidario: {lote.destino}."
        )

    @staticmethod
    def _responsable_entrega(admin: Usuario | None) -> str:
        if admin is None or not admin.nombre.strip():
            return "Equipo de Pastoral San Pio X"
        return f"{admin.nombre} (Agente Pastoral)"[:150]

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
