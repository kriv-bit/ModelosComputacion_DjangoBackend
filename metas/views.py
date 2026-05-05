from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import MetaLectura
from .serializers import MetaLecturaSerializer, ProgresoMetaSerializer
from .services import calcular_progreso_usuario


class MetaLecturaListCreate(generics.ListCreateAPIView):
    """Lista las metas del usuario o crea una nueva."""

    serializer_class = MetaLecturaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return MetaLectura.objects.filter(usuario=self.request.user)


class MetaLecturaDetail(generics.RetrieveUpdateDestroyAPIView):
    """Obtiene, actualiza o elimina una meta."""

    serializer_class = MetaLecturaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return MetaLectura.objects.filter(usuario=self.request.user)


class ProgresoMetasView(APIView):
    """Muestra el progreso de todas las metas activas del usuario."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        data = calcular_progreso_usuario(request.user)
        return Response(data)
