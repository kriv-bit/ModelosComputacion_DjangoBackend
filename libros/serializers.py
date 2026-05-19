from django.db.models import Avg
from rest_framework import serializers

from .models import Autor, Favorito, Libro, Prestamo, Resena


class AutorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Autor
        fields = "__all__"


class LibroSerializer(serializers.ModelSerializer):
    """Serializer que mapea Libro de Django al formato Book del frontend."""

    id = serializers.IntegerField(read_only=True)
    author = serializers.CharField(source="autor.nombre", read_only=True)
    autor_id = serializers.PrimaryKeyRelatedField(
        queryset=Autor.objects.all(), source="autor", write_only=True
    )
    title = serializers.CharField(source="titulo")
    isbn = serializers.CharField(required=False, allow_blank=True)
    category = serializers.CharField(source="genero", required=False, allow_blank=True)
    language = serializers.CharField(source="idioma", required=False)
    publisher = serializers.CharField(
        source="editorial", required=False, allow_blank=True
    )
    publishDate = serializers.DateField(source="fecha_publicacion", read_only=True)
    pages = serializers.IntegerField(source="numero_paginas", required=False)
    description = serializers.CharField(
        source="descripcion", required=False, allow_blank=True
    )
    coverUrl = serializers.URLField(
        source="portada_url", required=False, allow_blank=True
    )
    available = serializers.BooleanField(source="disponible", required=False)
    rating = serializers.SerializerMethodField()
    reviewCount = serializers.SerializerMethodField()
    hasPdf = serializers.SerializerMethodField()
    pdfUrl = serializers.SerializerMethodField()

    class Meta:
        model = Libro
        fields = [
            "id",
            "title",
            "author",
            "autor_id",
            "isbn",
            "category",
            "language",
            "publisher",
            "publishDate",
            "pages",
            "description",
            "coverUrl",
            "available",
            "rating",
            "reviewCount",
            "hasPdf",
            "pdfUrl",
        ]

    def get_rating(self, obj: Libro) -> float:
        avg = obj.resenas.aggregate(avg=Avg("calificacion"))["avg"]
        return round(avg, 1) if avg else 0.0

    def get_reviewCount(self, obj: Libro) -> int:
        return obj.resenas.count()

    def get_hasPdf(self, obj: Libro) -> bool:
        return bool(obj.pdf_file)

    def get_pdfUrl(self, obj: Libro) -> str | None:
        if not obj.pdf_file:
            return None
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(f"/api/libros/{obj.pk}/pdf/")
        return f"/api/libros/{obj.pk}/pdf/"



class ResenaSerializer(serializers.ModelSerializer):
    """Serializer que mapea Resena de Django al formato Review del frontend."""

    id = serializers.IntegerField(read_only=True)
    bookId = serializers.PrimaryKeyRelatedField(
        source="libro", queryset=Libro.objects.all()
    )
    userId = serializers.PrimaryKeyRelatedField(source="usuario", read_only=True)
    userName = serializers.CharField(source="usuario.get_full_name", read_only=True)
    rating = serializers.IntegerField(source="calificacion")
    comment = serializers.CharField(source="comentario")
    date = serializers.DateTimeField(source="fecha", read_only=True, format="%Y-%m-%d")
    flagged = serializers.BooleanField(source="marcada", read_only=True)
    flagReason = serializers.CharField(
        source="razon_marca", read_only=True, allow_blank=True
    )

    class Meta:
        model = Resena
        fields = [
            "id",
            "bookId",
            "userId",
            "userName",
            "rating",
            "comment",
            "date",
            "flagged",
            "flagReason",
        ]


class FavoritoSerializer(serializers.ModelSerializer):
    """Serializer para favoritos."""

    bookId = serializers.PrimaryKeyRelatedField(
        source="libro", queryset=Libro.objects.all()
    )

    class Meta:
        model = Favorito
        fields = ["id", "bookId"]


class PrestamoSerializer(serializers.ModelSerializer):
    """Serializer que mapea Prestamo al formato Loan del frontend."""

    id = serializers.IntegerField(read_only=True)
    bookId = serializers.PrimaryKeyRelatedField(
        source="libro", queryset=Libro.objects.all()
    )
    bookTitle = serializers.CharField(source="libro.titulo", read_only=True)
    userId = serializers.PrimaryKeyRelatedField(source="usuario", read_only=True)
    userName = serializers.CharField(source="usuario.get_full_name", read_only=True)
    loanDate = serializers.DateField(source="fecha_prestamo", read_only=True)
    dueDate = serializers.DateField(source="fecha_vencimiento")
    returnDate = serializers.DateField(
        source="fecha_devolucion", read_only=True, allow_null=True
    )
    status = serializers.CharField(source="estado", read_only=True)

    class Meta:
        model = Prestamo
        fields = [
            "id",
            "bookId",
            "bookTitle",
            "userId",
            "userName",
            "loanDate",
            "dueDate",
            "returnDate",
            "status",
        ]
