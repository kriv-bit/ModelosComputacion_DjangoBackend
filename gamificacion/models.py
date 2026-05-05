from django.contrib.auth.models import User
from django.db import models


class Logro(models.Model):
    """Catálogo de logros/insignias disponibles."""

    class Categoria(models.TextChoices):
        SESIONES = "sesiones", "Sesiones"
        PAGINAS = "paginas", "Páginas"
        TIEMPO = "tiempo", "Tiempo de lectura"
        VELOCIDAD = "velocidad", "Velocidad"
        RACHA = "racha", "Rachas"
        LIBROS = "libros", "Libros completados"
        ESPECIAL = "especial", "Especial"

    class TipoRequisito(models.TextChoices):
        SESIONES = "sesiones", "Nº de sesiones"
        PAGINAS = "paginas", "Páginas leídas"
        TIEMPO_MINUTOS = "tiempo_minutos", "Minutos de lectura"
        PPM = "ppm", "Palabras por minuto (PPM)"
        RACHA_DIAS = "racha_dias", "Días de racha"
        LIBROS_COMPLETADOS = "libros_completados", "Libros completados"
        CALIFICACIONES = "calificaciones", "Libros calificados"

    nombre = models.CharField(
        max_length=200,
        verbose_name="Nombre del logro",
    )
    descripcion = models.TextField(
        verbose_name="Descripción",
        help_text="¿Qué debe hacer el usuario para obtenerlo?",
    )
    icono = models.CharField(
        max_length=50,
        default="🏆",
        verbose_name="Icono (emoji)",
        help_text="Emoji que representa el logro, ej: 📖 ⚡ 🔥",
    )
    categoria = models.CharField(
        max_length=20,
        choices=Categoria.choices,
        default=Categoria.SESIONES,
        verbose_name="Categoría",
    )
    tipo_requisito = models.CharField(
        max_length=25,
        choices=TipoRequisito.choices,
        verbose_name="Tipo de requisito",
        help_text="Qué estadística debe alcanzar",
    )
    requisito_valor = models.PositiveIntegerField(
        verbose_name="Valor del requisito",
        help_text="Cantidad necesaria para desbloquear el logro",
    )
    orden = models.PositiveIntegerField(
        default=0,
        verbose_name="Orden",
        help_text="Para ordenar los logros en la lista",
    )
    activo = models.BooleanField(
        default=True,
        verbose_name="Activo",
    )

    class Meta:
        verbose_name = "Logro"
        verbose_name_plural = "Logros"
        ordering = ["orden", "id"]

    def __str__(self):
        return f"{self.icono} {self.nombre}"


class LogroUsuario(models.Model):
    """Logro desbloqueado por un usuario."""

    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="logros",
        verbose_name="Usuario",
    )
    logro = models.ForeignKey(
        Logro,
        on_delete=models.CASCADE,
        related_name="usuarios",
        verbose_name="Logro",
    )
    fecha_desbloqueo = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de desbloqueo",
    )

    class Meta:
        verbose_name = "Logro de usuario"
        verbose_name_plural = "Logros de usuarios"
        unique_together = ["usuario", "logro"]
        ordering = ["-fecha_desbloqueo"]

    def __str__(self):
        return f"{self.usuario.username} - {self.logro.nombre}"
