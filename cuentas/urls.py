from django.urls import path

from .views import (
    CambioPasswordView,
    LoginView,
    LogoutView,
    PerfilView,
    RegistroView,
)

urlpatterns = [
    path("auth/registro/", RegistroView.as_view(), name="registro"),
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
    path("auth/perfil/", PerfilView.as_view(), name="perfil"),
    path(
        "auth/cambiar-password/", CambioPasswordView.as_view(), name="cambiar-password"
    ),
]
