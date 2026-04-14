from django.urls import path
from .views import LibroListCreate

urlpatterns = [
    path('libros/', LibroListCreate.as_view(), name='libro-list-create'),
]
