"""Sincronizacion entre el estado de un lote y el Portal de Transparencia."""

from datetime import datetime, timezone

from backend.schemas import (
    ArticuloDonacion,
    Entrega,
    EstadoEntrega,
    EstadoLote,
    Lote,
    RolUsuario,
    UnidadMedida,
    Usuario,
)
from backend.services.lotes import ServicioLotes


def _lote(estado: EstadoLote = EstadoLote.PENDIENTE) -> Lote:
    return Lote(
        id="7",
        codigo="#PX-LOT-2026-007",
        fecha_ingreso=datetime(2026, 11, 25, tzinfo=timezone.utc),
        categoria_principal="Menestras y Granos",
        descripcion="Lenteja serrana seleccionada",
        volumen=15.0,
        unidad=UnidadMedida.KG,
        destino="Comedor Popular Santa Rosa",
        estado=estado,
        familias_beneficiadas=12,
        articulos=[
            ArticuloDonacion(
                id="1",
                categoria="Menestras y Granos",
                descripcion="Lenteja serrana (Bolsa 1Kg)",
                cantidad=15,
                unidad=UnidadMedida.KG,
                peso_unitario_kg=1.0,
                fecha_vencimiento=datetime(2027, 3, 20, tzinfo=timezone.utc),
            )
        ],
    )


def _admin() -> Usuario:
    return Usuario(
        id="A001",
        id_usuario=1,
        nombre="Prof. Taipe",
        telefono="+51 999 999 999",
        correo="pastoral@sanpiox.edu.pe",
        rol=RolUsuario.ADMINISTRATIVO,
        activo=True,
    )


class _FakeLotes:
    def __init__(self, lote: Lote) -> None:
        self.lote = lote

    def obtener_por_id(self, id_: str) -> Lote | None:
        return self.lote if id_ in (self.lote.id, self.lote.codigo) else None

    def actualizar_estado(self, id_: str, estado: EstadoLote) -> Lote | None:
        if self.obtener_por_id(id_) is None:
            return None
        self.lote = self.lote.model_copy(update={"estado": estado})
        return self.lote

    def obtener_agente_pastoral(self, id_: str) -> int | None:
        return 1


class _FakeEntregas:
    def __init__(self) -> None:
        self.entregas: dict[int, Entrega] = {}
        self.secuencia = 0

    def obtener_por_donacion(self, id_donacion: int) -> Entrega | None:
        return self.entregas.get(id_donacion)

    def siguiente_codigo_acta(self) -> str:
        self.secuencia += 1
        return f"#ACTA-{self.secuencia:04d}"

    def crear(self, datos, id_agente_registra: int) -> Entrega:
        entrega = Entrega(
            id=len(self.entregas) + 1,
            id_donacion=datos.id_donacion,
            codigo_publico_lote=datos.codigo_publico_lote,
            titulo_entrega=datos.titulo_entrega,
            descripcion_entrega=datos.descripcion_entrega,
            coordinador_recepcion=datos.coordinador_recepcion,
            codigo_acta=datos.codigo_acta,
            estado_entrega=datos.estado_entrega,
            fecha_entrega=datos.fecha_entrega,
        )
        self.entregas[datos.id_donacion] = entrega
        return entrega

    def marcar_entregada_por_donacion(self, id_donacion: int) -> None:
        entrega = self.entregas[id_donacion]
        self.entregas[id_donacion] = entrega.model_copy(
            update={"estado_entrega": EstadoEntrega.ENTREGADO}
        )

    def eliminar_por_donacion(self, id_donacion: int) -> int:
        return 1 if self.entregas.pop(id_donacion, None) else 0


def _servicio() -> tuple[ServicioLotes, _FakeEntregas]:
    entregas = _FakeEntregas()
    servicio = ServicioLotes(_FakeLotes(_lote()), entregas)  # type: ignore[arg-type]
    return servicio, entregas


def test_entregado_publica_hito_en_transparencia() -> None:
    servicio, entregas = _servicio()

    servicio.cambiar_estado("7", EstadoLote.ENTREGADO, _admin())

    assert len(entregas.entregas) == 1
    hito = entregas.entregas[7]
    assert hito.estado_entrega == EstadoEntrega.ENTREGADO
    assert hito.codigo_acta == "#ACTA-0001"
    assert hito.codigo_publico_lote == "#PX-LOT-2026-007"
    assert "Comedor Popular Santa Rosa" in hito.titulo_entrega
    assert "Lenteja serrana" in hito.descripcion_entrega
    assert hito.coordinador_recepcion.startswith("Prof. Taipe")


def test_entregado_repetido_no_duplica_el_hito() -> None:
    servicio, entregas = _servicio()

    servicio.cambiar_estado("7", EstadoLote.ENTREGADO, _admin())
    servicio.cambiar_estado("7", EstadoLote.ENTREGADO, _admin())

    assert len(entregas.entregas) == 1
    assert entregas.secuencia == 1


def test_revertir_estado_retira_el_hito() -> None:
    servicio, entregas = _servicio()

    servicio.cambiar_estado("7", EstadoLote.ENTREGADO, _admin())
    servicio.cambiar_estado("7", EstadoLote.PENDIENTE, _admin())

    assert entregas.entregas == {}


def test_cambiar_a_preparacion_sin_hito_previo_no_crea_entregas() -> None:
    servicio, entregas = _servicio()

    servicio.cambiar_estado("7", EstadoLote.PREPARACION, _admin())

    assert entregas.entregas == {}
