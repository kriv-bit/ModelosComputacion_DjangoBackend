from django.contrib import admin

from .models import IntentoPrueba, PruebaComprension


@admin.register(PruebaComprension)
class PruebaComprensionAdmin(admin.ModelAdmin):
    list_display = ("titulo", "libro", "dificultad", "activa")
    list_filter = ("dificultad", "activa")
    search_fields = ("titulo", "pregunta", "libro__titulo")


@admin.register(IntentoPrueba)
class IntentoPruebaAdmin(admin.ModelAdmin):
    list_display = ("usuario", "prueba", "respuesta", "correcta", "fecha_intento")
    list_filter = ("correcta", "fecha_intento")
    search_fields = ("usuario__username", "prueba__titulo")
    readonly_fields = ("correcta", "fecha_intento")
