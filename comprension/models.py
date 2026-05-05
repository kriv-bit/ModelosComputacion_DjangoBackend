from django.contrib.auth.models import User
from django.db import models


class PruebaComprension(models.Model):
    """Pregunta de comprensión sobre un libro."""

    class Dificultad(models.TextChoices):
        FACIL = "facil", "Fácil"
        MEDIA = "media", "Media"
        DIFICIL = "dificil", "Difícil"

    libro = models.ForeignKey(
        "libros.Libro",
        on_delete=models.CASCADE,
        related_name="pruebas_comprension",
        verbose_name="Libro",
    )
    titulo = models.CharField(
        max_length=200,
        verbose_name="Título de la prueba",
        help_text="Ej: Comprensión del Capítulo 1",
    )
    pregunta = models.TextField(
        verbose_name="Pregunta",
    )
    opcion_a = models.CharField(
        max_length=500,
        verbose_name="Opción A",
    )
    opcion_b = models.CharField(
        max_length=500,
        verbose_name="Opción B",
    )
    opcion_c = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="Opción C (opcional)",
    )
    opcion_d = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="Opción D (opcional)",
    )
    respuesta_correcta = models.CharField(
        max_length=1,
        choices=[("A", "A"), ("B", "B"), ("C", "C"), ("D", "D")],
        verbose_name="Respuesta correcta",
    )
    dificultad = models.CharField(
        max_length=10,
        choices=Dificultad.choices,
        default=Dificultad.MEDIA,
        verbose_name="Dificultad",
    )
    activa = models.BooleanField(
        default=True,
        verbose_name="Activa",
    )
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        verbose_name = "Prueba de comprensión"
        verbose_name_plural = "Pruebas de comprensión"
        ordering = ["libro", "dificultad", "id"]

    def __str__(self):
        return f"{self.libro.titulo} - {self.titulo}"


class IntentoPrueba(models.Model):
    """Intento de respuesta a una prueba de comprensión."""

    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="intentos_pruebas",
        verbose_name="Usuario",
    )
    prueba = models.ForeignKey(
        PruebaComprension,
        on_delete=models.CASCADE,
        related_name="intentos",
        verbose_name="Prueba",
    )
    respuesta = models.CharField(
        max_length=1,
        choices=[("A", "A"), ("B", "B"), ("C", "C"), ("D", "D")],
        verbose_name="Respuesta del usuario",
    )
    correcta = models.BooleanField(
        verbose_name="¿Correcta?",
    )
    fecha_intento = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha del intento",
    )

    class Meta:
        verbose_name = "Intento de prueba"
        verbose_name_plural = "Intentos de pruebas"
        ordering = ["-fecha_intento"]

    def __str__(self):
        return (
            f"{self.usuario.username} - {self.prueba.titulo} "
            f"({'✅' if self.correcta else '❌'})"
        )

    def save(self, *args, **kwargs):
        """Auto-verifica si la respuesta es correcta al guardar."""
        self.correcta = self.respuesta == self.prueba.respuesta_correcta
        super().save(*args, **kwargs)
