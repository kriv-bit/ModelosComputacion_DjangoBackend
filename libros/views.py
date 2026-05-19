import os
import re
import uuid

import requests as http_requests
from django.core.files.base import ContentFile
from django.db.models import Avg, Count, Q
from django.http import FileResponse, StreamingHttpResponse
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView

from .ai_service import build_book_chat_messages, stream_chat_response
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
    permission_classes = [permissions.AllowAny]


class AutorRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Autor.objects.all()
    serializer_class = AutorSerializer
    permission_classes = [permissions.AllowAny]


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

    permission_classes = [permissions.IsAuthenticated]

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


# ─── PDF: Download from URL ───────────────────────────────────────


class LibroPDFDownloadView(APIView):
    """
    POST /api/libros/<id>/download-pdf/
    Descarga un PDF desde una URL externa, lo guarda en media/pdfs/
    y lo asocia al libro. Solo admin/librarian.
    Body: { "url": "https://..." }
    """

    permission_classes = [IsAdminOrLibrarian]

    def post(self, request, pk):
        try:
            libro = Libro.objects.get(pk=pk)
        except Libro.DoesNotExist:
            return Response(
                {"error": "Libro no encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )

        url = request.data.get("url", "").strip()
        if not url:
            return Response(
                {"error": "Se requiere el campo 'url'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validación básica de URL
        if not url.startswith(("http://", "https://")):
            return Response(
                {"error": "URL inválida. Debe comenzar con http:// o https://."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            response = http_requests.get(url, timeout=60, stream=True)
            response.raise_for_status()

            content_type = response.headers.get("Content-Type", "")
            if "pdf" not in content_type.lower() and not url.lower().endswith(".pdf"):
                return Response(
                    {"error": f"El recurso no parece ser un PDF (Content-Type: {content_type})."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Generar nombre único para el archivo
            safe_title = re.sub(r"[^a-zA-Z0-9_-]", "_", libro.titulo[:40])
            filename = f"{safe_title}_{uuid.uuid4().hex[:8]}.pdf"

            content = b"".join(response.iter_content(chunk_size=8192))
            pdf_file = ContentFile(content, name=filename)

            # Eliminar PDF anterior si existe
            if libro.pdf_file:
                libro.pdf_file.delete(save=False)

            libro.pdf_file = pdf_file
            libro.pdf_source_url = url
            libro.save(update_fields=["pdf_file", "pdf_source_url"])

        except http_requests.exceptions.Timeout:
            return Response(
                {"error": "Tiempo de espera agotado al descargar el PDF."},
                status=status.HTTP_504_GATEWAY_TIMEOUT,
            )
        except http_requests.exceptions.RequestException as e:
            return Response(
                {"error": f"Error al descargar el PDF: {str(e)}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        return Response(
            {
                "message": "PDF descargado y guardado exitosamente.",
                "filename": filename,
                "pdfUrl": request.build_absolute_uri(libro.pdf_file.url),
            },
            status=status.HTTP_200_OK,
        )


# ─── PDF: Serve (stream) ──────────────────────────────────────────


class LibroPDFServeView(APIView):
    """
    GET /api/libros/<id>/pdf/
    Sirve el PDF del libro.
    Permiso: usuario autenticado con préstamo activo del libro.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            libro = Libro.objects.get(pk=pk)
        except Libro.DoesNotExist:
            return Response(
                {"error": "Libro no encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not libro.pdf_file:
            return Response(
                {"error": "Este libro no tiene un PDF disponible."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Verificar que el usuario tiene un préstamo activo para este libro
        has_active_loan = Prestamo.objects.filter(
            usuario=request.user,
            libro=libro,
            estado="active",
        ).exists()

        # Admins y bibliotecarios pueden acceder sin préstamo
        is_privileged = (
            request.user.is_staff
            or (hasattr(request.user, "perfil") and request.user.perfil.rol in ("admin", "librarian"))
        )

        if not has_active_loan and not is_privileged:
            return Response(
                {"error": "Debes tener un préstamo activo para leer este libro."},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            pdf_file = libro.pdf_file.open("rb")
            response = FileResponse(
                pdf_file,
                content_type="application/pdf",
                as_attachment=False,
                filename=os.path.basename(libro.pdf_file.name),
            )
            # Desactivar buffering en Nginx para que funcione bien el stream
            response["X-Accel-Buffering"] = "no"
            response["Content-Disposition"] = f'inline; filename="{os.path.basename(libro.pdf_file.name)}"'
            return response
        except Exception as e:
            return Response(
                {"error": f"Error al leer el PDF: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# ─── Chat IA con DeepSeek ─────────────────────────────────────────


class ChatView(APIView):
    """
    POST /api/chat/
    Recibe contexto del libro + texto seleccionado + pregunta,
    y retorna la respuesta de DeepSeek en streaming SSE.

    Body:
    {
        "bookId": 1,
        "selectedText": "...",
        "context": "...",
        "question": "¿Qué significa esto?",
        "history": [{"role": "user", "content": "..."}, ...]
    }
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        book_id = request.data.get("bookId")
        selected_text = request.data.get("selectedText", "")
        context = request.data.get("context", "")
        question = request.data.get("question", "").strip()
        history = request.data.get("history", [])

        if not question:
            return Response(
                {"error": "Se requiere el campo 'question'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Obtener datos del libro si se provee bookId
        book_title = "libro"
        book_author = "autor desconocido"
        if book_id:
            try:
                libro = Libro.objects.select_related("autor").get(pk=book_id)
                book_title = libro.titulo
                book_author = libro.autor.nombre
                if not context:
                    context = libro.descripcion or ""

                # Verificar acceso al libro (préstamo activo o admin/librarian)
                has_loan = Prestamo.objects.filter(
                    usuario=request.user,
                    libro=libro,
                    estado="active",
                ).exists()
                is_privileged = (
                    request.user.is_staff
                    or (
                        hasattr(request.user, "perfil")
                        and request.user.perfil.rol in ("admin", "librarian")
                    )
                )
                if not has_loan and not is_privileged:
                    return Response(
                        {"error": "Debes tener un préstamo activo para usar el chat de este libro."},
                        status=status.HTTP_403_FORBIDDEN,
                    )
            except Libro.DoesNotExist:
                pass

        messages = build_book_chat_messages(
            book_title=book_title,
            book_author=book_author,
            selected_text=selected_text,
            context=context,
            question=question,
            history=history or None,
        )

        def event_stream():
            """Genera Server-Sent Events desde el stream de DeepSeek."""
            try:
                for chunk in stream_chat_response(messages):
                    # Escapar saltos de línea para SSE
                    safe_chunk = chunk.replace("\n", "\\n")
                    yield f"data: {safe_chunk}\n\n"
            except Exception as e:
                yield f"data: [ERROR] {str(e)}\n\n"
            yield "data: [DONE]\n\n"

        response = StreamingHttpResponse(
            event_stream(),
            content_type="text/event-stream",
        )
        response["Cache-Control"] = "no-cache"
        response["X-Accel-Buffering"] = "no"
        return response

