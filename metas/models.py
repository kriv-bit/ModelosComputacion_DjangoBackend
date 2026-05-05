from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class MetaLectura(models.Model):
    """Meta de lectura del usuario (diaria, semanal o mensual)."""

    class Tipo(models.TextChoices):
        DIARIA = "diaria", "Diaria"
        SEMANAL = "semanal", "Semanal"
        MENSUAL = "mensual", "Mensual"

    class TipoObjetivo(models.TextChoices):
        PAGINAS = "paginas", "Páginas"
        MINUTOS = "minutos", "Minutos"
        SESIONES = "sesiones", "Sesiones"

    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="metas_lectura",
        verbose_name="Usuario",
    )
    nombre = models.CharField(
        max_length=200,
        verbose_name="Nombre de la meta",
        help_text='Ej: "Leer 20 páginas al día"',
    )
    tipo = models.CharField(
        max_length=10,
        choices=Tipo.choices,
        verbose_name="Periodicidad",
    )
    tipo_objetivo = models.CharField(
        max_length=10,
        choices=TipoObjetivo.choices,
        verbose_name="Tipo de objetivo",
    )
    objetivo_valor = models.PositiveIntegerField(
        verbose_name="Valor del objetivo",
        help_text="Cantidad a alcanzar (ej: 20 páginas, 30 minutos, 3 sesiones)",
    )
    activa = models.BooleanField(
        default=True,
        verbose_name="Activa",
    )
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Creada",
    )
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name="Actualizada",
    )

    class Meta:
        verbose_name = "Meta de lectura"
        verbose_name_plural = "Metas de lectura"
        ordering = ["-activa", "tipo", "fecha_creacion"]

    def __str__(self):
        return (
            f"{self.nombre} ({self.get_tipo_display()})"
            f" - {'✅ Activa' if self.activa else '❌ Inactiva'}"
        )
