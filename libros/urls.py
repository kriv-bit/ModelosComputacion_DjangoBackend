from django.urls import path
from .views import (
    AutorListCreate,
    AutorRetrieveUpdateDestroy,
    LibroListCreate,
    LibroRetrieveUpdateDestroy,
)

urlpatterns = [
    path('autores/', AutorListCreate.as_view(), name='autor-list-create'),
    path('autores/<int:pk>/', AutorRetrieveUpdateDestroy.as_view(), name='autor-retrieve-update-destroy'),
    path('libros/', LibroListCreate.as_view(), name='libro-list-create'),
    path('libros/<int:pk>/', LibroRetrieveUpdateDestroy.as_view(), name='libro-retrieve-update-destroy'),
]
