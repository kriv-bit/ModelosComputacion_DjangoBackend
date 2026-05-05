from rest_framework import serializers

from .models import IntentoPrueba, PruebaComprension


class PruebaComprensionSerializer(serializers.ModelSerializer):
    """Serializer para listar pruebas (sin respuesta correcta)."""

    libro_titulo = serializers.CharField(source="libro.titulo", read_only=True)
    dificultad_display = serializers.CharField(
        source="get_dificultad_display", read_only=True
    )

    class Meta:
        model = PruebaComprension
        fields = [
            "id",
            "libro",
            "libro_titulo",
            "titulo",
            "pregunta",
            "opcion_a",
            "opcion_b",
            "opcion_c",
            "opcion_d",
            "dificultad",
            "dificultad_display",
            "activa",
            "fecha_creacion",
        ]
        read_only_fields = ["fecha_creacion"]
        # La respuesta correcta NO se incluye al listar

    def validate(self, attrs):
        """Verifica que la respuesta correcta sea una opción existente."""
        correcta = attrs.get("respuesta_correcta")
        if correcta == "C" and not attrs.get("opcion_c"):
            raise serializers.ValidationError(
                "La opción C está marcada como correcta pero no tiene contenido."
            )
        if correcta == "D" and not attrs.get("opcion_d"):
            raise serializers.ValidationError(
                "La opción D está marcada como correcta pero no tiene contenido."
            )
        return attrs


class IntentoPruebaSerializer(serializers.ModelSerializer):
    """Serializer para responder una prueba."""

    prueba_pregunta = serializers.CharField(source="prueba.pregunta", read_only=True)
    prueba_titulo = serializers.CharField(source="prueba.titulo", read_only=True)

    class Meta:
        model = IntentoPrueba
        fields = [
            "id",
            "usuario",
            "prueba",
            "prueba_pregunta",
            "prueba_titulo",
            "respuesta",
            "correcta",
            "fecha_intento",
        ]
        read_only_fields = ["usuario", "correcta", "fecha_intento"]

    def create(self, validated_data):
        validated_data["usuario"] = self.context["request"].user
        return super().create(validated_data)


class ResultadosPruebaSerializer(serializers.Serializer):
    """Serializer para resultados de pruebas."""

    total_pruebas = serializers.IntegerField()
    total_correctas = serializers.IntegerField()
    total_incorrectas = serializers.IntegerField()
    porcentaje_aciertos = serializers.FloatField()
