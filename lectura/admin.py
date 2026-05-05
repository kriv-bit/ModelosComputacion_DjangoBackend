from django.contrib import admin

from .models import ProgresoLibro, SesionLectura


@admin.register(SesionLectura)
class SesionLecturaAdmin(admin.ModelAdmin):
    list_display = (
        "usuario",
        "libro",
        "fecha_inicio",
        "activa",
        "duracion_segundos",
        "palabras_por_minuto",
    )
    list_filter = ("activa", "fecha_inicio")
    search_fields = ("usuario__username", "libro__titulo", "notas")
    readonly_fields = (
        "duracion_segundos",
        "palabras_por_minuto",
        "fecha_creacion",
        "fecha_actualizacion",
    )


@admin.register(ProgresoLibro)
class ProgresoLibroAdmin(admin.ModelAdmin):
    list_display = ("usuario", "libro", "pagina_actual", "completado", "calificacion")
    list_filter = ("completado",)
    search_fields = ("usuario__username", "libro__titulo")
