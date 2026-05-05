from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Logro, LogroUsuario
from .serializers import (
    LogroSerializer,
    LogroUsuarioSerializer,
    ProgresoLogroSerializer,
)
from .services import progreso_logros, verificar_logros


class LogroListView(generics.ListAPIView):
    """Lista todos los logros disponibles (catálogo)."""

    queryset = Logro.objects.filter(activo=True).order_by("orden", "id")
    serializer_class = LogroSerializer
    permission_classes = [permissions.IsAuthenticated]


class MisLogrosView(generics.ListAPIView):
    """Lista los logros desbloqueados por el usuario autenticado."""

    serializer_class = LogroUsuarioSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return LogroUsuario.objects.filter(usuario=self.request.user)


class ProgresoLogrosView(APIView):
    """Muestra el progreso del usuario hacia todos los logros."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        data = progreso_logros(request.user)
        serializer = ProgresoLogroSerializer(data, many=True)
        return Response(serializer.data)


class VerificarLogrosView(APIView):
    """Verifica y desbloquea nuevos logros para el usuario."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        nuevos = verificar_logros(request.user)
        return Response(
            {
                "nuevos_logros": LogroSerializer(nuevos, many=True).data,
                "total_nuevos": len(nuevos),
                "mensaje": f"🎉 ¡Has desbloqueado {len(nuevos)} logro(s)!"
                if nuevos
                else "No hay nuevos logros.",
            }
        )
