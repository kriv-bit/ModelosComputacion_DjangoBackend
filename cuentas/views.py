from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from rest_framework import generics, permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import PerfilUsuario
from .serializers import (
    CambioPasswordSerializer,
    LoginSerializer,
    PerfilUsuarioSerializer,
    RegistroSerializer,
)


class RegistroView(generics.CreateAPIView):
    """Registra un nuevo usuario con su perfil."""

    serializer_class = RegistroSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response(
            {
                "mensaje": "Usuario registrado exitosamente.",
                "username": user.username,
                "email": user.email,
                "token": token.key,
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(generics.GenericAPIView):
    """Inicia sesión y retorna los datos del usuario con su token."""

    serializer_class = LoginSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data["username"]
        password = serializer.validated_data["password"]

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            token, _ = Token.objects.get_or_create(user=user)
            return Response(
                {
                    "mensaje": "Inicio de sesión exitoso.",
                    "username": user.username,
                    "email": user.email,
                    "user_id": user.id,
                    "token": token.key,
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {"error": "Credenciales inválidas."},
            status=status.HTTP_401_UNAUTHORIZED,
        )


class LogoutView(APIView):
    """Cierra la sesión del usuario."""

    def post(self, request):
        logout(request)
        return Response(
            {"mensaje": "Sesión cerrada exitosamente."},
            status=status.HTTP_200_OK,
        )


class PerfilView(generics.RetrieveUpdateAPIView):
    """Obtiene o actualiza el perfil del usuario autenticado."""

    serializer_class = PerfilUsuarioSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        perfil, _ = PerfilUsuario.objects.get_or_create(user=self.request.user)
        return perfil


class CambioPasswordView(generics.GenericAPIView):
    """Cambia la contraseña del usuario autenticado."""

    serializer_class = CambioPasswordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user

        if not user.check_password(serializer.validated_data["password_actual"]):
            return Response(
                {"password_actual": "La contraseña actual es incorrecta."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(serializer.validated_data["password_nueva"])
        user.save()
        update_session_auth_hash(request, user)

        return Response(
            {"mensaje": "Contraseña cambiada exitosamente."},
            status=status.HTTP_200_OK,
        )
