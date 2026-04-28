from django.db import models

class Autor(models.Model):
    nombre = models.CharField(max_length=200)
    pais = models.CharField(max_length=100)
    fecha_nacimiento = models.DateField()

    def __str__(self):
        return self.nombre


class Libro(models.Model):
    titulo = models.CharField(max_length=200)
    autor = models.ForeignKey(
        Autor,
        on_delete=models.CASCADE,
        related_name='libros'
    )
    isbn = models.CharField(max_length=13, blank=True, null=True)
    fecha_publicacion = models.DateField(auto_now_add=True)
    genero = models.CharField(max_length=100, blank=True, null=True)
    numero_paginas = models.PositiveIntegerField(blank=True, null=True)
    editorial = models.CharField(max_length=200, blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.titulo
