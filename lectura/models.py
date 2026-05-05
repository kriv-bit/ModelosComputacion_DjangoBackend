from django.contrib.auth.models import User
from django.db import models


class SesionLectura(models.Model):
    """Registra una sesión de lectura del usuario."""

    PALABRAS_POR_PAGINA_DEFAULT = 250

    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sesiones_lectura",
        verbose_name="Usuario",
    )
    libro = models.ForeignKey(
        "libros.Libro",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sesiones_lectura",
        verbose_name="Libro",
    )
    fecha_inicio = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Inicio de la sesión",
    )
    fecha_fin = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fin de la sesión",
    )
    duracion_segundos = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Duración (segundos)",
        help_text="Calculado automáticamente al finalizar",
    )
    paginas_leidas = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Páginas leídas",
    )
    palabras_por_pagina = models.PositiveIntegerField(
        default=PALABRAS_POR_PAGINA_DEFAULT,
        verbose_name="Palabras por página",
        help_text="Se usa para calcular palabras por minuto",
    )
    palabras_por_minuto = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Palabras por minuto (PPM)",
        help_text="Calculado automáticamente al finalizar",
    )
    activa = models.BooleanField(
        default=True,
        verbose_name="¿Sesión activa?",
    )
    notas = models.TextField(
        blank=True,
        verbose_name="Notas",
        help_text="Apuntes sobre esta sesión de lectura",
    )
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
    )
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        verbose_name = "Sesión de lectura"
        verbose_name_plural = "Sesiones de lectura"
        ordering = ["-fecha_inicio"]

    def __str__(self):
        libro_info = f" - {self.libro.titulo}" if self.libro else ""
        return (
            f"Sesión de {self.usuario.username}{libro_info} "
            f"({self.fecha_inicio.date()})"
        )

    def finalizar(self, paginas_leidas=None):
        """Finaliza la sesión y calcula las métricas."""
        from django.utils import timezone

        self.fecha_fin = timezone.now()
        self.activa = False

        if paginas_leidas is not None:
            self.paginas_leidas = paginas_leidas

        # Calcular duración en segundos
        delta = self.fecha_fin - self.fecha_inicio
        self.duracion_segundos = int(delta.total_seconds())

        # Calcular PPM si tenemos páginas leídas
        if self.paginas_leidas and self.duracion_segundos > 0:
            minutos = self.duracion_segundos / 60
            total_palabras = self.paginas_leidas * self.palabras_por_pagina
            self.palabras_por_minuto = round(total_palabras / minutos)

        self.save(
            update_fields=[
                "fecha_fin",
                "activa",
                "paginas_leidas",
                "duracion_segundos",
                "palabras_por_minuto",
            ]
        )

        # Actualizar progreso del libro si aplica
        if self.libro:
            self._actualizar_progreso_libro()

    def _actualizar_progreso_libro(self):
        """Actualiza el progreso del libro asociado."""
        progreso, _ = ProgresoLibro.objects.get_or_create(
            usuario=self.usuario,
            libro=self.libro,
            defaults={
                "pagina_actual": self.paginas_leidas or 0,
            },
        )
        if self.paginas_leidas:
            progreso.pagina_actual = max(progreso.pagina_actual, self.paginas_leidas)
            progreso.save(update_fields=["pagina_actual", "fecha_actualizacion"])


class ProgresoLibro(models.Model):
    """Seguimiento del progreso de un usuario en un libro."""

    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="progresos_libros",
        verbose_name="Usuario",
    )
    libro = models.ForeignKey(
        "libros.Libro",
        on_delete=models.CASCADE,
        related_name="progresos",
        verbose_name="Libro",
    )
    pagina_actual = models.PositiveIntegerField(
        default=0,
        verbose_name="Página actual",
    )
    paginas_totales = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Total de páginas",
        help_text="Opcional, se usa para calcular el % de progreso",
    )
    completado = models.BooleanField(
        default=False,
        verbose_name="¿Completado?",
    )
    fecha_inicio = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Iniciado",
    )
    fecha_completado = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Completado",
    )
    calificacion = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name="Calificación (1-5)",
        help_text="Evaluación personal del libro",
    )
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        verbose_name = "Progreso de libro"
        verbose_name_plural = "Progresos de libros"
        unique_together = ["usuario", "libro"]
        ordering = ["-fecha_actualizacion"]

    def __str__(self):
        return (
            f"{self.usuario.username} - {self.libro.titulo} ({self.pagina_actual} págs)"
        )

    @property
    def progreso_porcentaje(self):
        """Calcula el porcentaje de progreso si hay total de páginas."""
        if self.paginas_totales and self.paginas_totales > 0:
            return round((self.pagina_actual / self.paginas_totales) * 100, 1)
        return None

    def marcar_completado(self, calificacion=None):
        """Marca el libro como completado."""
        from django.utils import timezone

        self.completado = True
        self.fecha_completado = timezone.now()
        if calificacion is not None:
            self.calificacion = calificacion
        self.save(update_fields=["completado", "fecha_completado", "calificacion"])
