from rest_framework import serializers

from .models import MetaLectura


class MetaLecturaSerializer(serializers.ModelSerializer):
    """Serializer para CRUD de metas."""

    tipo_display = serializers.CharField(source="get_tipo_display", read_only=True)
    tipo_objetivo_display = serializers.CharField(
        source="get_tipo_objetivo_display", read_only=True
    )

    class Meta:
        model = MetaLectura
        fields = [
            "id",
            "usuario",
            "nombre",
            "tipo",
            "tipo_display",
            "tipo_objetivo",
            "tipo_objetivo_display",
            "objetivo_valor",
            "activa",
            "fecha_creacion",
            "fecha_actualizacion",
        ]
        read_only_fields = ["usuario", "fecha_creacion", "fecha_actualizacion"]

    def create(self, validated_data):
        validated_data["usuario"] = self.context["request"].user
        return super().create(validated_data)


class ProgresoMetaSerializer(serializers.Serializer):
    """Serializer para el progreso de una meta."""

    meta_id = serializers.IntegerField()
    meta_nombre = serializers.CharField()
    meta_tipo = serializers.CharField()
    meta_tipo_objetivo = serializers.CharField()
    valor_actual = serializers.IntegerField()
    objetivo = serializers.IntegerField()
    progreso_porcentaje = serializers.IntegerField()
    cumplido = serializers.BooleanField()
