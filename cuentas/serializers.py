from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import PerfilUsuario


class RegistroSerializer(serializers.ModelSerializer):
    """Serializer para registro de nuevo usuario."""

    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={"input_type": "password"},
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password"},
        label="Confirmar contraseña",
    )
    fecha_nacimiento = serializers.DateField()
    genero = serializers.ChoiceField(choices=PerfilUsuario.GENERO_CHOICES)
    pais = serializers.CharField(max_length=100)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password",
            "password2",
            "fecha_nacimiento",
            "genero",
            "pais",
        ]

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError(
                {"password2": "Las contraseñas no coinciden."}
            )
        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password")
        validated_data.pop("password2")

        perfil_data = {
            "fecha_nacimiento": validated_data.pop("fecha_nacimiento"),
            "genero": validated_data.pop("genero"),
            "pais": validated_data.pop("pais"),
        }

        user = User(**validated_data)
        user.set_password(password)
        user.save()

        PerfilUsuario.objects.create(user=user, **perfil_data)

        return user


class LoginSerializer(serializers.Serializer):
    """Serializer para inicio de sesión."""

    username = serializers.CharField(required=True)
    password = serializers.CharField(
        required=True,
        style={"input_type": "password"},
        write_only=True,
    )


class PerfilUsuarioSerializer(serializers.ModelSerializer):
    """Serializer para leer/actualizar el perfil del usuario."""

    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    edad = serializers.IntegerField(read_only=True)

    class Meta:
        model = PerfilUsuario
        fields = [
            "id",
            "username",
            "email",
            "fecha_nacimiento",
            "edad",
            "genero",
            "pais",
            "fecha_registro",
        ]
        read_only_fields = ["id", "fecha_registro"]


class CambioPasswordSerializer(serializers.Serializer):
    """Serializer para cambiar contraseña."""

    password_actual = serializers.CharField(
        required=True,
        style={"input_type": "password"},
        write_only=True,
    )
    password_nueva = serializers.CharField(
        required=True,
        validators=[validate_password],
        style={"input_type": "password"},
        write_only=True,
    )
    password_nueva2 = serializers.CharField(
        required=True,
        style={"input_type": "password"},
        write_only=True,
        label="Confirmar nueva contraseña",
    )

    def validate(self, attrs):
        if attrs["password_nueva"] != attrs["password_nueva2"]:
            raise serializers.ValidationError(
                {"password_nueva2": "Las contraseñas nuevas no coinciden."}
            )
        return attrs
