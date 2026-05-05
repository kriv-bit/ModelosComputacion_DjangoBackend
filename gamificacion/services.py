"""Servicio para verificar y desbloquear logros de usuarios."""

from django.db.models import Count, Max, Sum
from django.utils import timezone

from lectura.models import ProgresoLibro, SesionLectura

from .models import Logro, LogroUsuario


def verificar_logros(usuario):
    """
    Verifica todos los logros para un usuario y desbloquea los que cumpla.
    Retorna una lista de los nuevos logros desbloqueados.
    """
    stats = _obtener_stats(usuario)
    logros = Logro.objects.filter(activo=True)
    nuevos = []

    for logro in logros:
        if LogroUsuario.objects.filter(usuario=usuario, logro=logro).exists():
            continue

        if _cumple_requisito(logro, stats, usuario):
            LogroUsuario.objects.create(usuario=usuario, logro=logro)
            nuevos.append(logro)

    return nuevos


def _obtener_stats(usuario):
    """Obtiene las estadísticas actuales del usuario."""
    sesiones = SesionLectura.objects.filter(usuario=usuario, activa=False)
    progresos = ProgresoLibro.objects.filter(usuario=usuario)

    stats = {
        "total_sesiones": SesionLectura.objects.filter(usuario=usuario).count(),
        "total_paginas": sesiones.aggregate(total=Sum("paginas_leidas"))["total"] or 0,
        "total_tiempo_minutos": (
            sesiones.aggregate(total=Sum("duracion_segundos"))["total"] or 0
        )
        // 60,
        "ppm_maximo": sesiones.aggregate(maximo=Max("palabras_por_minuto"))["maximo"]
        or 0,
        "libros_completados": progresos.filter(completado=True).count(),
        "calificaciones": progresos.exclude(calificacion__isnull=True).count(),
    }

    # Calcular racha actual
    fechas = set(
        SesionLectura.objects.filter(usuario=usuario, activa=False)
        .dates("fecha_inicio", "day")
        .distinct()
        .order_by("-fecha_inicio")
    )
    fechas_list = sorted(fechas, reverse=True) if fechas else []
    stats["racha_actual_dias"] = _contar_racha(fechas_list)

    return stats


def _contar_racha(fechas_desc):
    """Cuenta días consecutivos desde la fecha más reciente."""
    if not fechas_desc:
        return 0
    hoy = timezone.now().date()
    ayer = hoy - timezone.timedelta(days=1)
    dia_mas_reciente = fechas_desc[0]

    if dia_mas_reciente not in (hoy, ayer):
        return 0

    racha = 0
    fecha_esperada = dia_mas_reciente
    for fecha in fechas_desc:
        if fecha == fecha_esperada:
            racha += 1
            fecha_esperada -= timezone.timedelta(days=1)
        else:
            break
    return racha


def _cumple_requisito(logro, stats, usuario):
    """Verifica si el usuario cumple el requisito de un logro."""
    mapa = {
        Logro.TipoRequisito.SESIONES: stats["total_sesiones"],
        Logro.TipoRequisito.PAGINAS: stats["total_paginas"],
        Logro.TipoRequisito.TIEMPO_MINUTOS: stats["total_tiempo_minutos"],
        Logro.TipoRequisito.PPM: stats["ppm_maximo"],
        Logro.TipoRequisito.RACHA_DIAS: stats["racha_actual_dias"],
        Logro.TipoRequisito.LIBROS_COMPLETADOS: stats["libros_completados"],
        Logro.TipoRequisito.CALIFICACIONES: stats["calificaciones"],
    }
    valor_actual = mapa.get(logro.tipo_requisito, 0)
    return valor_actual >= logro.requisito_valor


def progreso_logros(usuario):
    """
    Retorna el progreso del usuario hacia cada logro activo.
    """
    stats = _obtener_stats(usuario)
    logros = Logro.objects.filter(activo=True).order_by("orden", "id")
    resultados = []

    for logro in logros:
        desbloqueado = LogroUsuario.objects.filter(
            usuario=usuario, logro=logro
        ).exists()

        mapa = {
            Logro.TipoRequisito.SESIONES: stats["total_sesiones"],
            Logro.TipoRequisito.PAGINAS: stats["total_paginas"],
            Logro.TipoRequisito.TIEMPO_MINUTOS: stats["total_tiempo_minutos"],
            Logro.TipoRequisito.PPM: stats["ppm_maximo"],
            Logro.TipoRequisito.RACHA_DIAS: stats["racha_actual_dias"],
            Logro.TipoRequisito.LIBROS_COMPLETADOS: stats["libros_completados"],
            Logro.TipoRequisito.CALIFICACIONES: stats["calificaciones"],
        }
        valor_actual = mapa.get(logro.tipo_requisito, 0)
        progreso = (
            min(int((valor_actual / logro.requisito_valor) * 100), 100)
            if logro.requisito_valor > 0
            else 0
        )
        resultados.append(
            {
                "logro_id": logro.id,
                "logro_nombre": logro.nombre,
                "logro_icono": logro.icono,
                "logro_descripcion": logro.descripcion,
                "logro_categoria": logro.categoria,
                "valor_actual": valor_actual,
                "requisito_valor": logro.requisito_valor,
                "progreso_porcentaje": progreso,
                "desbloqueado": desbloqueado,
            }
        )

    return resultados
