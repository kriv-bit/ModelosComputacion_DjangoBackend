from django.contrib import admin

from .models import Logro, LogroUsuario


@admin.register(Logro)
class LogroAdmin(admin.ModelAdmin):
    list_display = (
        "icono",
        "nombre",
        "categoria",
        "tipo_requisito",
        "requisito_valor",
        "activo",
        "orden",
    )
    list_filter = ("categoria", "activo")
    search_fields = ("nombre", "descripcion")
    list_editable = ("orden", "activo")


@admin.register(LogroUsuario)
class LogroUsuarioAdmin(admin.ModelAdmin):
    list_display = ("usuario", "logro", "fecha_desbloqueo")
    list_filter = ("fecha_desbloqueo",)
    search_fields = ("usuario__username", "logro__nombre")
    readonly_fields = ("fecha_desbloqueo",)
