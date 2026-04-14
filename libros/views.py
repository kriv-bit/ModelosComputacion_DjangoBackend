from rest_framework import generics
from .models import Libro
from .serializers import LibroSerializer

class LibroListCreate(generics.ListCreateAPIView):
    queryset = Libro.objects.all()
    serializer_class = LibroSerializer
