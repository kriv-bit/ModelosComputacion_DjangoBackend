from django.urls import path

from .views import (
    EstadisticasView,
    FinalizarSesionView,
    MarcarCompletadoView,
    ProgresoLibroDetail,
    ProgresoLibroListCreate,
    SesionLecturaDetail,
    SesionLecturaListCreate,
)

urlpatterns = [
    path("sesiones/", SesionLecturaListCreate.as_view(), name="sesion-list-create"),
    path("sesiones/<int:pk>/", SesionLecturaDetail.as_view(), name="sesion-detail"),
    path(
        "sesiones/<int:pk>/finalizar/",
        FinalizarSesionView.as_view(),
        name="sesion-finalizar",
    ),
    # Progreso de libros
    path("progreso/", ProgresoLibroListCreate.as_view(), name="progreso-list-create"),
    path("progreso/<int:pk>/", ProgresoLibroDetail.as_view(), name="progreso-detail"),
    path(
        "progreso/<int:pk>/completar/",
        MarcarCompletadoView.as_view(),
        name="progreso-completar",
    ),
    # Estadísticas
    path("estadisticas/", EstadisticasView.as_view(), name="estadisticas"),
]
