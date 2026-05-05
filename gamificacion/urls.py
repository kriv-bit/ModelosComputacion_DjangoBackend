from django.urls import path

from .views import LogroListView, MisLogrosView, ProgresoLogrosView, VerificarLogrosView

urlpatterns = [
    path("logros/", LogroListView.as_view(), name="logros-lista"),
    path("mis-logros/", MisLogrosView.as_view(), name="mis-logros"),
    path("progreso-logros/", ProgresoLogrosView.as_view(), name="progreso-logros"),
    path("verificar/", VerificarLogrosView.as_view(), name="verificar-logros"),
]
