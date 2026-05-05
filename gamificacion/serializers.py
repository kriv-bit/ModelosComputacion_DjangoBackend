from rest_framework import serializers

from .models import Logro, LogroUsuario


class LogroSerializer(serializers.ModelSerializer):
    categoria_display = serializers.CharField(
        source="get_categoria_display", read_only=True
    )

    class Meta:
        model = Logro
        fields = [
            "id",
            "nombre",
            "descripcion",
            "icono",
            "categoria",
            "categoria_display",
            "tipo_requisito",
            "requisito_valor",
            "orden",
        ]


class LogroUsuarioSerializer(serializers.ModelSerializer):
    """Serializer para logros desbloqueados por el usuario."""

    logro_nombre = serializers.CharField(source="logro.nombre", read_only=True)
    logro_descripcion = serializers.CharField(
        source="logro.descripcion", read_only=True
    )
    logro_icono = serializers.CharField(source="logro.icono", read_only=True)
    logro_categoria = serializers.CharField(source="logro.categoria", read_only=True)

    class Meta:
        model = LogroUsuario
        fields = [
            "id",
            "logro",
            "logro_nombre",
            "logro_descripcion",
            "logro_icono",
            "logro_categoria",
            "fecha_desbloqueo",
        ]
        read_only_fields = ["fecha_desbloqueo"]


class ProgresoLogroSerializer(serializers.Serializer):
    """Serializer para el progreso hacia cada logro."""

    logro_id = serializers.IntegerField()
    logro_nombre = serializers.CharField()
    logro_icono = serializers.CharField()
    logro_descripcion = serializers.CharField()
    logro_categoria = serializers.CharField()
    valor_actual = serializers.IntegerField()
    requisito_valor = serializers.IntegerField()
    progreso_porcentaje = serializers.IntegerField()
    desbloqueado = serializers.BooleanField()
