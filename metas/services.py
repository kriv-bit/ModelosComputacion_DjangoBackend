"""Servicio para calcular el progreso de las metas de lectura."""

from datetime import date, timedelta

from django.db.models import Count, Sum
from django.utils import timezone

from lectura.models import SesionLectura

from .models import MetaLectura


def obtener_inicio_periodo(tipo):
    """Retorna la fecha de inicio del período según el tipo."""
    hoy = timezone.now().date()
    if tipo == MetaLectura.Tipo.DIARIA:
        return hoy
    elif tipo == MetaLectura.Tipo.SEMANAL:
        return hoy - timedelta(days=hoy.weekday())  # Lunes
    elif tipo == MetaLectura.Tipo.MENSUAL:
        return hoy.replace(day=1)
    return hoy


def calcular_progreso_meta(meta, usuario=None):
    """
    Calcula el progreso actual de una meta específica.
    Retorna dict con valor_actual, objetivo, porcentaje y cumplido.
    """
    user = meta.usuario if not usuario else usuario
    inicio = obtener_inicio_periodo(meta.tipo)
    ahora = timezone.now()

    sesiones = SesionLectura.objects.filter(
        usuario=user,
        activa=False,
        fecha_inicio__date__gte=inicio,
        fecha_inicio__date__lte=ahora.date(),
    )

    if meta.tipo_objetivo == MetaLectura.TipoObjetivo.PAGINAS:
        valor_actual = sesiones.aggregate(total=Sum("paginas_leidas"))["total"] or 0
    elif meta.tipo_objetivo == MetaLectura.TipoObjetivo.MINUTOS:
        total_segundos = (
            sesiones.aggregate(total=Sum("duracion_segundos"))["total"] or 0
        )
        valor_actual = total_segundos // 60
    elif meta.tipo_objetivo == MetaLectura.TipoObjetivo.SESIONES:
        valor_actual = sesiones.count()
    else:
        valor_actual = 0

    objetivo = meta.objetivo_valor
    porcentaje = min(int((valor_actual / objetivo) * 100), 100) if objetivo > 0 else 0
    cumplido = valor_actual >= objetivo

    return {
        "meta_id": meta.id,
        "meta_nombre": meta.nombre,
        "meta_tipo": meta.tipo,
        "meta_tipo_objetivo": meta.tipo_objetivo,
        "valor_actual": valor_actual,
        "objetivo": objetivo,
        "progreso_porcentaje": porcentaje,
        "cumplido": cumplido,
    }


def calcular_progreso_usuario(usuario):
    """
    Calcula el progreso de todas las metas activas de un usuario.
    Retorna una lista con el progreso de cada meta.
    """
    metas = MetaLectura.objects.filter(usuario=usuario, activa=True)
    return [calcular_progreso_meta(meta) for meta in metas]
