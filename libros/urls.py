from django.urls import path

from .views import (
    AutorListCreate,
    AutorRetrieveUpdateDestroy,
    ChatView,
    EstadisticasAdminView,
    FavoritoDestroy,
    FavoritoListCreate,
    LibroListCreate,
    LibroPDFDownloadView,
    LibroPDFServeView,
    LibroRetrieveUpdateDestroy,
    PrestamoListCreate,
    PrestamoReturnView,
    ResenaDestroy,
    ResenaFlagView,
    ResenaListCreate,
    ResenaUnflagView,
    health_check,
)

urlpatterns = [
    # Health
    path("health/", health_check, name="health-check"),
    # Autores
    path("autores/", AutorListCreate.as_view(), name="autor-list-create"),
    path(
        "autores/<int:pk>/",
        AutorRetrieveUpdateDestroy.as_view(),
        name="autor-detail",
    ),
    # Libros
    path("libros/", LibroListCreate.as_view(), name="libro-list-create"),
    path(
        "libros/<int:pk>/",
        LibroRetrieveUpdateDestroy.as_view(),
        name="libro-detail",
    ),
    # PDF: descargar desde URL (admin/librarian)
    path(
        "libros/<int:pk>/download-pdf/",
        LibroPDFDownloadView.as_view(),
        name="libro-pdf-download",
    ),
    # PDF: servir al frontend (auth + préstamo activo)
    path(
        "libros/<int:pk>/pdf/",
        LibroPDFServeView.as_view(),
        name="libro-pdf-serve",
    ),
    # Reseñas
    path("resenas/", ResenaListCreate.as_view(), name="resena-list-create"),
    path("resenas/<int:pk>/", ResenaDestroy.as_view(), name="resena-delete"),
    path(
        "resenas/<int:pk>/flag/",
        ResenaFlagView.as_view(),
        name="resena-flag",
    ),
    path(
        "resenas/<int:pk>/unflag/",
        ResenaUnflagView.as_view(),
        name="resena-unflag",
    ),
    # Favoritos
    path("favoritos/", FavoritoListCreate.as_view(), name="favorito-list-create"),
    path(
        "favoritos/<int:book_id>/",
        FavoritoDestroy.as_view(),
        name="favorito-delete",
    ),
    # Préstamos
    path("prestamos/", PrestamoListCreate.as_view(), name="prestamo-list-create"),
    path(
        "prestamos/<int:pk>/devolver/",
        PrestamoReturnView.as_view(),
        name="prestamo-return",
    ),
    # Estadísticas
    path(
        "estadisticas/",
        EstadisticasAdminView.as_view(),
        name="estadisticas-admin",
    ),
    # Chat IA con DeepSeek
    path("chat/", ChatView.as_view(), name="chat-ia"),
]
