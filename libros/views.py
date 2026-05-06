from django.db.models import Avg, Count, Q
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Autor, Favorito, Libro, Prestamo, Resena
from .serializers import (
    AutorSerializer,
    FavoritoSerializer,
    LibroSerializer,
    PrestamoSerializer,
    ResenaSerializer,
)


# ─── Permissions ──────────────────────────────────────────────────


class IsAdminOrLibrarian(permissions.BasePermission):
    """Permite acceso solo a admin o bibliotecarios."""

    # pyrefly: ignore [bad-override]
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        try:
            return request.user.perfil.rol in ("admin", "librarian")
        except Exception:
            return request.user.is_staff


# ─── Health ───────────────────────────────────────────────────────


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def health_check(request):
    return Response(
        {"status": "ok", "message": "Conexión exitosa con Django! 🚀"}
    )


# ─── Autores ──────────────────────────────────────────────────────


class AutorListCreate(generics.ListCreateAPIView):
    queryset = Autor.objects.all()
    serializer_class = AutorSerializer


class AutorRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Autor.objects.all()
    serializer_class = AutorSerializer


# ─── Libros ───────────────────────────────────────────────────────


class LibroListCreate(generics.ListCreateAPIView):
    """Lista todos los libros (público) o crea uno nuevo (admin)."""

    queryset = Libro.objects.select_related("autor").all()
    serializer_class = LibroSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAdminOrLibrarian()]
        return [permissions.AllowAny()]


class LibroRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    """Obtiene, actualiza o elimina un libro."""

    queryset = Libro.objects.select_related("autor").all()
    serializer_class = LibroSerializer

    def get_permissions(self):
        if self.request.method in ("PUT", "PATCH", "DELETE"):
            return [IsAdminOrLibrarian()]
        return [permissions.AllowAny()]


# ─── Reseñas ──────────────────────────────────────────────────────


class ResenaListCreate(generics.ListCreateAPIView):
    """Lista reseñas (filtrable por bookId/userId) o crea una nueva."""

    serializer_class = ResenaSerializer

    def get_queryset(self):
        qs = Resena.objects.select_related("usuario", "libro").all()
        book_id = self.request.query_params.get("bookId")
        user_id = self.request.query_params.get("userId")
        if book_id:
            qs = qs.filter(libro_id=book_id)
        if user_id:
            qs = qs.filter(usuario_id=user_id)
        return qs

    def get_permissions(self):
        if self.request.method == "POST":
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)


class ResenaDestroy(generics.DestroyAPIView):
    """Elimina una reseña propia."""

    serializer_class = ResenaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Resena.objects.filter(usuario=self.request.user)


class ResenaFlagView(APIView):
    """Marca o desmarca una reseña para moderación (admin/librarian)."""

    permission_classes = [IsAdminOrLibrarian]

    def post(self, request, pk):
        """Marca una reseña."""
        try:
            resena = Resena.objects.get(pk=pk)
        except Resena.DoesNotExist:
            return Response(
                {"error": "Reseña no encontrada."},
                status=status.HTTP_404_NOT_FOUND,
            )
        resena.marcada = True
        resena.razon_marca = request.data.get("reason", "")
        resena.save(update_fields=["marcada", "razon_marca"])
        return Response(ResenaSerializer(resena).data)


class ResenaUnflagView(APIView):
    """Desmarca una reseña."""

    permission_classes = [IsAdminOrLibrarian]

    def post(self, request, pk):
        try:
            resena = Resena.objects.get(pk=pk)
        except Resena.DoesNotExist:
            return Response(
                {"error": "Reseña no encontrada."},
                status=status.HTTP_404_NOT_FOUND,
            )
        resena.marcada = False
        resena.razon_marca = ""
        resena.save(update_fields=["marcada", "razon_marca"])
        return Response(ResenaSerializer(resena).data)


# ─── Favoritos ────────────────────────────────────────────────────


class FavoritoListCreate(generics.ListCreateAPIView):
    """Lista los favoritos del usuario o añade uno."""

    serializer_class = FavoritoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Favorito.objects.filter(usuario=self.request.user)

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)


class FavoritoDestroy(APIView):
    """Elimina un favorito por bookId."""

    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, book_id):
        deleted, _ = Favorito.objects.filter(
            usuario=request.user, libro_id=book_id
        ).delete()
        if deleted:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {"error": "Favorito no encontrado."},
            status=status.HTTP_404_NOT_FOUND,
        )


# ─── Préstamos ────────────────────────────────────────────────────


class PrestamoListCreate(generics.ListCreateAPIView):
    """Lista préstamos o crea uno nuevo (admin)."""

    serializer_class = PrestamoSerializer

    def get_queryset(self):
        qs = Prestamo.objects.select_related("libro", "usuario").all()
        estado = self.request.query_params.get("status")
        if estado:
            qs = qs.filter(estado=estado)
        return qs

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAdminOrLibrarian()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        libro = serializer.validated_data.get("libro")
        if libro and not libro.disponible:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({"bookId": "Este libro no está disponible para préstamo."})
        prestamo = serializer.save(usuario=self.request.user, estado="active")
        # Marcar libro como no disponible
        prestamo.libro.disponible = False
        prestamo.libro.save(update_fields=["disponible"])


class PrestamoReturnView(APIView):
    """Marca un préstamo como devuelto."""

    permission_classes = [IsAdminOrLibrarian]

    def post(self, request, pk):
        try:
            prestamo = Prestamo.objects.get(pk=pk)
        except Prestamo.DoesNotExist:
            return Response(
                {"error": "Préstamo no encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )
        from django.utils import timezone

        prestamo.estado = "returned"
        prestamo.fecha_devolucion = timezone.now().date()
        prestamo.save(update_fields=["estado", "fecha_devolucion"])
        # Marcar libro como disponible
        prestamo.libro.disponible = True
        prestamo.libro.save(update_fields=["disponible"])
        return Response(PrestamoSerializer(prestamo).data)


# ─── Estadísticas (Admin Dashboard) ──────────────────────────────


class EstadisticasAdminView(APIView):
    """Estadísticas generales para el dashboard de admin."""

    permission_classes = [permissions.AllowAny]

    def get(self, request):
        libros = Libro.objects.all()
        prestamos = Prestamo.objects.all()
        resenas = Resena.objects.all()

        total_books = libros.count()
        avg_rating = libros.annotate(
            avg_r=Avg("resenas__calificacion")
        ).aggregate(total_avg=Avg("avg_r"))["total_avg"]

        stats = {
            "totalBooks": total_books,
            "availableBooks": libros.filter(disponible=True).count(),
            "categories": libros.values("genero").distinct().count(),
            "avgRating": str(round(avg_rating, 1)) if avg_rating else "0.0",
            "totalUsers": 0,  # Se calcula con auth.User
            "totalLoans": prestamos.count(),
            "activeLoans": prestamos.filter(estado="active").count(),
            "overdueLoans": prestamos.filter(estado="overdue").count(),
        }

        from django.contrib.auth.models import User

        stats["totalUsers"] = User.objects.count()

        return Response(stats)
