from django.contrib import admin
from .models import Autor, Favorito, Libro, Prestamo, Resena


@admin.register(Autor)
class AutorAdmin(admin.ModelAdmin):
    # pyrefly: ignore [bad-override-mutable-attribute]
    list_display = ("nombre", "pais", "fecha_nacimiento")
    search_fields = ("nombre",)


@admin.register(Libro)
class LibroAdmin(admin.ModelAdmin):
    # pyrefly: ignore [bad-override-mutable-attribute]
    list_display = ("titulo", "autor", "genero", "idioma", "disponible")
    list_filter = ("genero", "idioma", "disponible")
    search_fields = ("titulo", "isbn")


@admin.register(Resena)
class ResenaAdmin(admin.ModelAdmin):
    # pyrefly: ignore [bad-override-mutable-attribute]
    list_display = ("libro", "usuario", "calificacion", "marcada", "fecha")
    list_filter = ("marcada", "calificacion")


@admin.register(Favorito)
class FavoritoAdmin(admin.ModelAdmin):
    # pyrefly: ignore [bad-override-mutable-attribute]
    list_display = ("usuario", "libro", "fecha")


@admin.register(Prestamo)
class PrestamoAdmin(admin.ModelAdmin):
    # pyrefly: ignore [bad-override-mutable-attribute]
    list_display = ("libro", "usuario", "estado", "fecha_prestamo", "fecha_vencimiento")
    list_filter = ("estado",)
