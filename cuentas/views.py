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
    UserMeSerializer,
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
        perfil = user.perfil
        return Response(
            {
                "mensaje": "Usuario registrado exitosamente.",
                "user": {
                    "id": user.id,
                    "name": user.get_full_name() or user.username,
                    "email": user.email,
                    "role": perfil.rol,
                },
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
            try:
                perfil = PerfilUsuario.objects.get(user=user)
                rol = perfil.rol
            except PerfilUsuario.DoesNotExist:
                rol = "user"
            return Response(
                {
                    "mensaje": "Inicio de sesión exitoso.",
                    "user": {
                        "id": user.id,
                        "name": user.get_full_name() or user.username,
                        "email": user.email,
                        "role": rol,
                    },
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

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        # Eliminar token si existe
        if request.user.is_authenticated:
            Token.objects.filter(user=request.user).delete()
        logout(request)
        return Response(
            {"mensaje": "Sesión cerrada exitosamente."},
            status=status.HTTP_200_OK,
        )


class MeView(APIView):
    """Retorna los datos del usuario autenticado (para rehidratar sesión)."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            perfil = PerfilUsuario.objects.get(user=request.user)
        except PerfilUsuario.DoesNotExist:
            return Response(
                {"id": request.user.id, "name": request.user.username, "email": request.user.email, "role": "user"},
                status=status.HTTP_200_OK,
            )
        serializer = UserMeSerializer(perfil)
        return Response(serializer.data)


class PerfilView(generics.RetrieveUpdateAPIView):
    """Obtiene o actualiza el perfil del usuario autenticado."""

    serializer_class = PerfilUsuarioSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        try:
            return PerfilUsuario.objects.get(user=self.request.user)
        except PerfilUsuario.DoesNotExist:
            from rest_framework.exceptions import NotFound
            raise NotFound("Perfil no encontrado. Completa tu registro.")


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
