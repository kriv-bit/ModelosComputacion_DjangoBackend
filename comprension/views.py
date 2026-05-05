from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import IntentoPrueba, PruebaComprension
from .serializers import (
    IntentoPruebaSerializer,
    PruebaComprensionSerializer,
    ResultadosPruebaSerializer,
)


class PruebaList(generics.ListAPIView):
    """Lista las pruebas de comprensión de un libro."""

    serializer_class = PruebaComprensionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        libro_id = self.kwargs.get("libro_id")
        return PruebaComprension.objects.filter(libro_id=libro_id, activa=True)


class PruebaDetail(generics.RetrieveUpdateDestroyAPIView):
    """CRUD de pruebas individuales."""

    queryset = PruebaComprension.objects.all()
    serializer_class = PruebaComprensionSerializer
    permission_classes = [permissions.IsAuthenticated]


class ResponderPruebaView(generics.CreateAPIView):
    """Responde una prueba y verifica si es correcta."""

    serializer_class = IntentoPruebaSerializer
    permission_classes = [permissions.IsAuthenticated]


class HistorialIntentosView(generics.ListAPIView):
    """Historial de intentos del usuario."""

    serializer_class = IntentoPruebaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = IntentoPrueba.objects.filter(usuario=self.request.user)
        libro_id = self.request.query_params.get("libro")
        if libro_id:
            qs = qs.filter(prueba__libro_id=libro_id)
        return qs


class ResultadosView(APIView):
    """Resultados generales de comprensión del usuario."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        intentos = IntentoPrueba.objects.filter(usuario=request.user)
        total = intentos.count()
        correctas = intentos.filter(correcta=True).count()
        incorrectas = total - correctas
        porcentaje = round((correctas / total * 100), 1) if total > 0 else 0.0

        data = {
            "total_pruebas": total,
            "total_correctas": correctas,
            "total_incorrectas": incorrectas,
            "porcentaje_aciertos": porcentaje,
        }
        serializer = ResultadosPruebaSerializer(data)
        return Response(serializer.data)
