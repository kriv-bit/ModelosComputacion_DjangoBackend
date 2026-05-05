from rest_framework import serializers

from .models import ProgresoLibro, SesionLectura


class SesionLecturaListSerializer(serializers.ModelSerializer):
    usuario_username = serializers.CharField(source="usuario.username", read_only=True)
    libro_titulo = serializers.CharField(
        source="libro.titulo", read_only=True, default=""
    )

    class Meta:
        model = SesionLectura
        fields = [
            "id",
            "usuario",
            "usuario_username",
            "libro",
            "libro_titulo",
            "fecha_inicio",
            "fecha_fin",
            "duracion_segundos",
            "paginas_leidas",
            "palabras_por_minuto",
            "activa",
            "notas",
        ]
        read_only_fields = [
            "usuario",
            "fecha_inicio",
            "fecha_fin",
            "duracion_segundos",
            "palabras_por_minuto",
            "activa",
        ]


class IniciarSesionSerializer(serializers.ModelSerializer):
    """Serializer para iniciar una sesión de lectura."""

    class Meta:
        model = SesionLectura
        fields = [
            "id",
            "libro",
            "palabras_por_pagina",
            "notas",
            "activa",
        ]
        read_only_fields = ["activa"]

    def create(self, validated_data):
        validated_data["usuario"] = self.context["request"].user
        return super().create(validated_data)


class FinalizarSesionSerializer(serializers.Serializer):
    """Serializer para finalizar una sesión de lectura."""

    paginas_leidas = serializers.IntegerField(
        required=True,
        min_value=1,
        help_text="Número de páginas leídas en esta sesión",
    )


class ProgresoLibroSerializer(serializers.ModelSerializer):
    """Serializer para el progreso de libros."""

    usuario_username = serializers.CharField(source="usuario.username", read_only=True)
    libro_titulo = serializers.CharField(source="libro.titulo", read_only=True)
    progreso_porcentaje = serializers.IntegerField(read_only=True)

    class Meta:
        model = ProgresoLibro
        fields = [
            "id",
            "usuario",
            "usuario_username",
            "libro",
            "libro_titulo",
            "pagina_actual",
            "paginas_totales",
            "progreso_porcentaje",
            "completado",
            "fecha_inicio",
            "fecha_completado",
            "calificacion",
            "fecha_actualizacion",
        ]
        read_only_fields = [
            "usuario",
            "completado",
            "fecha_inicio",
            "fecha_completado",
            "fecha_actualizacion",
        ]

    def validate(self, attrs):
        """Verifica que no exista ya un progreso para este usuario+libro."""
        request = self.context.get("request")
        if request and request.method == "POST":
            usuario = request.user
            libro = attrs.get("libro")
            if (
                libro
                and ProgresoLibro.objects.filter(usuario=usuario, libro=libro).exists()
            ):
                raise serializers.ValidationError(
                    "Ya existe un progreso para este libro."
                )
        return attrs

    def create(self, validated_data):
        validated_data["usuario"] = self.context["request"].user
        return super().create(validated_data)


class MarcarCompletadoSerializer(serializers.Serializer):
    """Serializer para marcar un libro como completado."""

    calificacion = serializers.IntegerField(
        required=False,
        min_value=1,
        max_value=5,
        help_text="Calificación del 1 al 5 (opcional)",
    )
