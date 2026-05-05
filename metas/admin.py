from django.contrib import admin

from .models import MetaLectura


@admin.register(MetaLectura)
class MetaLecturaAdmin(admin.ModelAdmin):
    list_display = (
        "usuario",
        "nombre",
        "tipo",
        "tipo_objetivo",
        "objetivo_valor",
        "activa",
    )
    list_filter = ("tipo", "tipo_objetivo", "activa")
    search_fields = ("nombre", "usuario__username")
