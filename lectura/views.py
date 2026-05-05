from django.db.models import Avg, Max, Sum
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ProgresoLibro, SesionLectura
from .serializers import (
    FinalizarSesionSerializer,
    IniciarSesionSerializer,
    MarcarCompletadoSerializer,
    ProgresoLibroSerializer,
    SesionLecturaListSerializer,
)


class SesionLecturaListCreate(generics.ListCreateAPIView):
    """Lista las sesiones del usuario o inicia una nueva."""

    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return IniciarSesionSerializer
        return SesionLecturaListSerializer

    def get_queryset(self):
        qs = SesionLectura.objects.filter(usuario=self.request.user)
        # Filtros opcionales
        libro = self.request.query_params.get("libro")
        if libro:
            qs = qs.filter(libro_id=libro)
        activa = self.request.query_params.get("activa")
        if activa is not None:
            qs = qs.filter(activa=(activa.lower() == "true"))
        desde = self.request.query_params.get("desde")
        if desde:
            qs = qs.filter(fecha_inicio__date__gte=desde)
        hasta = self.request.query_params.get("hasta")
        if hasta:
            qs = qs.filter(fecha_inicio__date__lte=hasta)
        return qs


class SesionLecturaDetail(generics.RetrieveUpdateDestroyAPIView):
    """Obtiene, actualiza o elimina una sesión de lectura."""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SesionLecturaListSerializer

    def get_queryset(self):
        return SesionLectura.objects.filter(usuario=self.request.user)


class FinalizarSesionView(APIView):
    """Finaliza una sesión de lectura activa y calcula métricas."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            sesion = SesionLectura.objects.get(pk=pk, usuario=request.user)
        except SesionLectura.DoesNotExist:
            return Response(
                {"error": "Sesión no encontrada."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not sesion.activa:
            return Response(
                {"error": "Esta sesión ya está finalizada."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = FinalizarSesionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        sesion.finalizar(paginas_leidas=serializer.validated_data["paginas_leidas"])

        return Response(
            SesionLecturaListSerializer(sesion).data,
            status=status.HTTP_200_OK,
        )


class ProgresoLibroListCreate(generics.ListCreateAPIView):
    """Lista el progreso del usuario o crea uno nuevo."""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProgresoLibroSerializer

    def get_queryset(self):
        qs = ProgresoLibro.objects.filter(usuario=self.request.user)
        libro = self.request.query_params.get("libro")
        if libro:
            qs = qs.filter(libro_id=libro)
        completado = self.request.query_params.get("completado")
        if completado is not None:
            qs = qs.filter(completado=(completado.lower() == "true"))
        return qs


class ProgresoLibroDetail(generics.RetrieveUpdateAPIView):
    """Obtiene o actualiza el progreso de un libro."""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProgresoLibroSerializer

    def get_queryset(self):
        return ProgresoLibro.objects.filter(usuario=self.request.user)


class MarcarCompletadoView(APIView):
    """Marca un libro como completado."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            progreso = ProgresoLibro.objects.get(pk=pk, usuario=request.user)
        except ProgresoLibro.DoesNotExist:
            return Response(
                {"error": "Progreso no encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if progreso.completado:
            return Response(
                {"error": "Este libro ya está marcado como completado."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = MarcarCompletadoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        progreso.marcar_completado(
            calificacion=serializer.validated_data.get("calificacion")
        )

        return Response(
            ProgresoLibroSerializer(progreso).data,
            status=status.HTTP_200_OK,
        )


class EstadisticasView(APIView):
    """Obtiene estadísticas de lectura del usuario."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        usuario = request.user
        sesiones = SesionLectura.objects.filter(usuario=usuario)
        sesiones_finalizadas = sesiones.filter(activa=False)

        # Estadísticas generales
        stats = {
            "total_sesiones": sesiones.count(),
            "sesiones_activas": sesiones.filter(activa=True).count(),
            "total_tiempo_minutos": self._calcular_tiempo_total(sesiones_finalizadas),
            "total_paginas": self._calcular_paginas_totales(sesiones_finalizadas),
            "ppm_promedio": self._calcular_ppm_promedio(sesiones_finalizadas),
            "ppm_maximo": self._calcular_ppm_maximo(sesiones_finalizadas),
            "racha_actual_dias": self._calcular_racha_actual(usuario),
            "racha_maxima_dias": self._calcular_racha_maxima(usuario),
            "libros_completados": ProgresoLibro.objects.filter(
                usuario=usuario, completado=True
            ).count(),
            "libros_en_lectura": ProgresoLibro.objects.filter(
                usuario=usuario, completado=False
            ).count(),
        }

        # Sesiones recientes (últimos 7 días)
        stats["sesiones_ultimos_7_dias"] = self._sesiones_por_dia(
            sesiones_finalizadas, 7
        )

        return Response(stats)

    def _calcular_tiempo_total(self, sesiones):
        """Calcula el tiempo total de lectura en minutos."""
        resultado = sesiones.aggregate(total=Sum("duracion_segundos"))
        segundos = resultado["total"] or 0
        return round(segundos / 60, 1)

    def _calcular_paginas_totales(self, sesiones):
        """Calcula el total de páginas leídas."""
        resultado = sesiones.aggregate(total=Sum("paginas_leidas"))
        return resultado["total"] or 0

    def _calcular_ppm_promedio(self, sesiones):
        """Calcula el promedio de palabras por minuto."""
        resultado = sesiones.aggregate(promedio=Avg("palabras_por_minuto"))
        return round(resultado["promedio"]) if resultado["promedio"] else 0

    def _calcular_ppm_maximo(self, sesiones):
        """Calcula el máximo de palabras por minuto."""
        resultado = sesiones.aggregate(maximo=Max("palabras_por_minuto"))
        return round(resultado["maximo"]) if resultado["maximo"] else 0

    def _calcular_racha_actual(self, usuario):
        """Calcula los días consecutivos de lectura hasta hoy."""
        fechas = set(
            SesionLectura.objects.filter(usuario=usuario, activa=False)
            .dates("fecha_inicio", "day")
            .distinct()
            .order_by("-fecha_inicio")
        )
        fechas_list = sorted(fechas, reverse=True) if fechas else []
        return self._contar_dias_consecutivos(fechas_list)

    def _calcular_racha_maxima(self, usuario):
        """Calcula la racha máxima histórica de días consecutivos."""
        fechas = set(
            SesionLectura.objects.filter(usuario=usuario, activa=False)
            .dates("fecha_inicio", "day")
            .distinct()
            .order_by("-fecha_inicio")
        )
        fechas_list = sorted(fechas, reverse=True) if fechas else []
        if not fechas_list:
            return 0
        # Calcular la racha máxima
        fechas_list = sorted(fechas)  # Ascendente
        max_racha = 1
        racha_actual = 1
        for i in range(1, len(fechas_list)):
            diff = (fechas_list[i] - fechas_list[i - 1]).days
            if diff == 1:
                racha_actual += 1
                max_racha = max(max_racha, racha_actual)
            elif diff > 1:
                racha_actual = 1
        return max_racha

    def _contar_dias_consecutivos(self, fechas_desc):
        """Cuenta días consecutivos desde una fecha hacia atrás."""
        if not fechas_desc:
            return 0
        hoy = timezone.now().date()
        ayer = hoy - timezone.timedelta(days=1)
        dia_mas_reciente = fechas_desc[0]

        # Si el día más reciente no es hoy ni ayer, racha = 0
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

    def _sesiones_por_dia(self, sesiones, dias):
        """Agrupa sesiones por día para los últimos N días."""
        desde = timezone.now().date() - timezone.timedelta(days=dias - 1)
        sesiones_filtro = sesiones.filter(fecha_inicio__date__gte=desde)

        dias_dict = {}
        for s in sesiones_filtro:
            fecha = s.fecha_inicio.date()
            if fecha not in dias_dict:
                dias_dict[fecha] = {"sesiones": 0, "minutos": 0, "paginas": 0}
            dias_dict[fecha]["sesiones"] += 1
            dias_dict[fecha]["minutos"] += (s.duracion_segundos or 0) / 60
            dias_dict[fecha]["paginas"] += s.paginas_leidas or 0

        resultado = [
            {
                "fecha": str(desde + timezone.timedelta(days=i)),
                "sesiones": dias_dict.get(desde + timezone.timedelta(days=i), {}).get(
                    "sesiones", 0
                ),
                "minutos": round(
                    dias_dict.get(desde + timezone.timedelta(days=i), {}).get(
                        "minutos", 0
                    ),
                    1,
                ),
                "paginas": dias_dict.get(desde + timezone.timedelta(days=i), {}).get(
                    "paginas", 0
                ),
            }
            for i in range(dias)
        ]
        return resultado
