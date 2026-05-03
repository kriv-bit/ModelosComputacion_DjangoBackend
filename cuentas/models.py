from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class PerfilUsuario(models.Model):
    GENERO_CHOICES = [
        ("M", "Masculino"),
        ("F", "Femenino"),
        ("O", "Otro"),
        ("N", "Prefiero no decirlo"),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="perfil",
        verbose_name="Usuario",
    )
    fecha_nacimiento = models.DateField(
        verbose_name="Fecha de nacimiento",
    )
    genero = models.CharField(
        max_length=1,
        choices=GENERO_CHOICES,
        verbose_name="Género",
    )
    pais = models.CharField(
        max_length=100,
        verbose_name="País",
    )
    fecha_registro = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de registro",
    )

    class Meta:
        verbose_name = "Perfil de usuario"
        verbose_name_plural = "Perfiles de usuarios"

    def __str__(self):
        return f"Perfil de {self.user.username}"

    @property
    def edad(self):
        """Calcula la edad a partir de la fecha de nacimiento."""
        hoy = timezone.now().date()
        return (
            hoy.year
            - self.fecha_nacimiento.year
            - (
                (hoy.month, hoy.day)
                < (self.fecha_nacimiento.month, self.fecha_nacimiento.day)
            )
        )
