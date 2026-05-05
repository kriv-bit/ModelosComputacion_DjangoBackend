from django.urls import path

from .views import (
    HistorialIntentosView,
    PruebaDetail,
    PruebaList,
    ResponderPruebaView,
    ResultadosView,
)

urlpatterns = [
    path("libros/<int:libro_id>/pruebas/", PruebaList.as_view(), name="pruebas-list"),
    path("pruebas/<int:pk>/", PruebaDetail.as_view(), name="pruebas-detail"),
    path(
        "pruebas/<int:pk>/responder/",
        ResponderPruebaView.as_view(),
        name="responder-prueba",
    ),
    path("intentos/", HistorialIntentosView.as_view(), name="intentos-list"),
    path("resultados/", ResultadosView.as_view(), name="resultados-comprension"),
]
