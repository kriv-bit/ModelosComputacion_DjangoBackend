from django.contrib.auth.models import User
from django.db import models


class Autor(models.Model):
    nombre = models.CharField(max_length=200)
    pais = models.CharField(max_length=100)
    fecha_nacimiento = models.DateField()

    # pyrefly: ignore [bad-override]
    def __str__(self):
        return self.nombre


class Libro(models.Model):
    """Modelo de libro de la biblioteca."""

    titulo = models.CharField(max_length=200)
    autor = models.ForeignKey(
        Autor,
        on_delete=models.CASCADE,
        related_name="libros",
    )
    isbn = models.CharField(max_length=20, blank=True, null=True)
    fecha_publicacion = models.DateField(auto_now_add=True)
    genero = models.CharField(max_length=100, blank=True, null=True)
    numero_paginas = models.PositiveIntegerField(blank=True, null=True)
    editorial = models.CharField(max_length=200, blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    portada_url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name="URL de portada",
    )
    idioma = models.CharField(
        max_length=50,
        default="Español",
        verbose_name="Idioma",
    )
    disponible = models.BooleanField(
        default=True,
        verbose_name="Disponible",
    )
    pdf_file = models.FileField(
        upload_to="pdfs/",
        blank=True,
        null=True,
        verbose_name="Archivo PDF",
    )
    pdf_source_url = models.URLField(
        max_length=1000,
        blank=True,
        null=True,
        verbose_name="URL de origen del PDF",
    )

    # pyrefly: ignore [bad-override]
    def __str__(self):
        return self.titulo

    @property
    def rating(self) -> float:
        """Calificación promedio calculada desde las reseñas."""
        avg = self.resenas.aggregate(avg=models.Avg("calificacion"))["avg"]
        return round(avg, 1) if avg else 0.0

    @property
    def review_count(self) -> int:
        """Número total de reseñas."""
        return self.resenas.count()


class Resena(models.Model):
    """Reseña de un libro por un usuario."""

    libro = models.ForeignKey(
        Libro,
        on_delete=models.CASCADE,
        related_name="resenas",
        verbose_name="Libro",
    )
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="resenas",
        verbose_name="Usuario",
    )
    calificacion = models.PositiveSmallIntegerField(
        verbose_name="Calificación (1-5)",
    )
    comentario = models.TextField(
        verbose_name="Comentario",
    )
    marcada = models.BooleanField(
        default=False,
        verbose_name="Marcada para moderación",
    )
    razon_marca = models.CharField(
        max_length=200,
        blank=True,
        default="",
        verbose_name="Razón de la marca",
    )
    fecha = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha",
    )

    class Meta:
        verbose_name = "Reseña"
        verbose_name_plural = "Reseñas"
        ordering = ["-fecha"]
        unique_together = ["libro", "usuario"]

    def __str__(self):
        return f"{self.usuario.username} → {self.libro.titulo} ({self.calificacion}★)"


class Favorito(models.Model):
    """Libro marcado como favorito por un usuario."""

    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="favoritos",
        verbose_name="Usuario",
    )
    libro = models.ForeignKey(
        Libro,
        on_delete=models.CASCADE,
        related_name="favoritos",
        verbose_name="Libro",
    )
    fecha = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha",
    )

    class Meta:
        verbose_name = "Favorito"
        verbose_name_plural = "Favoritos"
        unique_together = ["usuario", "libro"]
        ordering = ["-fecha"]

    def __str__(self):
        return f"{self.usuario.username} ♥ {self.libro.titulo}"


class Prestamo(models.Model):
    """Préstamo de un libro a un usuario."""

    ESTADO_CHOICES = [
        ("active", "Activo"),
        ("overdue", "Vencido"),
        ("returned", "Devuelto"),
    ]

    libro = models.ForeignKey(
        Libro,
        on_delete=models.CASCADE,
        related_name="prestamos",
        verbose_name="Libro",
    )
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="prestamos",
        verbose_name="Usuario",
    )
    fecha_prestamo = models.DateField(
        auto_now_add=True,
        verbose_name="Fecha de préstamo",
    )
    fecha_vencimiento = models.DateField(
        verbose_name="Fecha de vencimiento",
    )
    fecha_devolucion = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fecha de devolución",
    )
    estado = models.CharField(
        max_length=10,
        choices=ESTADO_CHOICES,
        default="active",
        verbose_name="Estado",
    )

    class Meta:
        verbose_name = "Préstamo"
        verbose_name_plural = "Préstamos"
        ordering = ["-fecha_prestamo"]

    def __str__(self):
        return f"{self.libro.titulo} → {self.usuario.username} ({self.get_estado_display()})"
