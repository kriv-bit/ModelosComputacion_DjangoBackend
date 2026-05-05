from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from lectura.models import SesionLectura
from libros.models import Autor, Libro

from .models import MetaLectura
from .services import (
    calcular_progreso_meta,
    calcular_progreso_usuario,
    obtener_inicio_periodo,
)


class BaseTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="lector_test",
            password="Pass1234!",
        )
        cls.autor = Autor.objects.create(
            nombre="Autor",
            pais="México",
            fecha_nacimiento="1970-01-01",
        )
        cls.libro = Libro.objects.create(titulo="Test", autor=cls.autor)

    def setUp(self):
        self.client = APIClient()
        self.client.force_login(self.user)


class MetaLecturaAPITests(BaseTest):
    """Tests de los endpoints de metas."""

    def test_crear_meta_diaria(self):
        url = reverse("metas-list-create")
        response = self.client.post(
            url,
            {
                "nombre": "Leer 20 páginas al día",
                "tipo": "diaria",
                "tipo_objetivo": "paginas",
                "objetivo_valor": 20,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["nombre"], "Leer 20 páginas al día")
        self.assertTrue(response.data["activa"])

    def test_listar_metas(self):
        MetaLectura.objects.create(
            usuario=self.user,
            nombre="Meta 1",
            tipo="diaria",
            tipo_objetivo="paginas",
            objetivo_valor=10,
        )
        MetaLectura.objects.create(
            usuario=self.user,
            nombre="Meta 2",
            tipo="semanal",
            tipo_objetivo="minutos",
            objetivo_valor=60,
        )
        url = reverse("metas-list-create")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_actualizar_meta(self):
        meta = MetaLectura.objects.create(
            usuario=self.user,
            nombre="Meta original",
            tipo="diaria",
            tipo_objetivo="paginas",
            objetivo_valor=10,
        )
        url = reverse("metas-detail", args=[meta.id])
        response = self.client.patch(url, {"objetivo_valor": 30}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["objetivo_valor"], 30)

    def test_eliminar_meta(self):
        meta = MetaLectura.objects.create(
            usuario=self.user,
            nombre="Meta a eliminar",
            tipo="diaria",
            tipo_objetivo="paginas",
            objetivo_valor=10,
        )
        url = reverse("metas-detail", args=[meta.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class ProgresoMetasTests(BaseTest):
    """Tests del progreso de metas."""

    def _crear_sesion(self, minutos_atras, paginas):
        sesion = SesionLectura.objects.create(
            usuario=self.user,
            libro=self.libro,
        )
        sesion.fecha_inicio = timezone.now() - timedelta(minutes=minutos_atras)
        sesion.save()
        sesion.finalizar(paginas_leidas=paginas)
        return sesion

    def test_progreso_meta_paginas(self):
        self._crear_sesion(minutos_atras=30, paginas=10)
        self._crear_sesion(minutos_atras=60, paginas=15)

        meta = MetaLectura.objects.create(
            usuario=self.user,
            nombre="25 páginas hoy",
            tipo="diaria",
            tipo_objetivo="paginas",
            objetivo_valor=25,
        )
        progreso = calcular_progreso_meta(meta)
        self.assertEqual(progreso["valor_actual"], 25)
        self.assertEqual(progreso["progreso_porcentaje"], 100)
        self.assertTrue(progreso["cumplido"])

    def test_progreso_meta_minutos(self):
        self._crear_sesion(minutos_atras=20, paginas=5)
        self._crear_sesion(minutos_atras=25, paginas=8)

        meta = MetaLectura.objects.create(
            usuario=self.user,
            nombre="30 minutos",
            tipo="diaria",
            tipo_objetivo="minutos",
            objetivo_valor=30,
        )
        progreso = calcular_progreso_meta(meta)
        self.assertGreaterEqual(progreso["valor_actual"], 30)
        self.assertTrue(progreso["cumplido"])

    def test_progreso_meta_no_cumplida(self):
        meta = MetaLectura.objects.create(
            usuario=self.user,
            nombre="100 páginas",
            tipo="diaria",
            tipo_objetivo="paginas",
            objetivo_valor=100,
        )
        progreso = calcular_progreso_meta(meta)
        self.assertEqual(progreso["valor_actual"], 0)
        self.assertEqual(progreso["progreso_porcentaje"], 0)
        self.assertFalse(progreso["cumplido"])

    def test_progreso_meta_sesiones(self):
        self._crear_sesion(minutos_atras=10, paginas=5)
        self._crear_sesion(minutos_atras=20, paginas=3)
        self._crear_sesion(minutos_atras=30, paginas=4)

        meta = MetaLectura.objects.create(
            usuario=self.user,
            nombre="3 sesiones hoy",
            tipo="diaria",
            tipo_objetivo="sesiones",
            objetivo_valor=3,
        )
        progreso = calcular_progreso_meta(meta)
        self.assertEqual(progreso["valor_actual"], 3)
        self.assertTrue(progreso["cumplido"])

    def test_endpoint_progreso(self):
        self._crear_sesion(minutos_atras=15, paginas=5)
        MetaLectura.objects.create(
            usuario=self.user,
            nombre="10 páginas",
            tipo="diaria",
            tipo_objetivo="paginas",
            objetivo_valor=10,
        )
        url = reverse("metas-progreso")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertIn("cumplido", response.data[0])
        self.assertIn("progreso_porcentaje", response.data[0])

    def test_progreso_solo_metas_activas(self):
        self._crear_sesion(minutos_atras=10, paginas=5)
        MetaLectura.objects.create(
            usuario=self.user,
            nombre="Activa",
            tipo="diaria",
            tipo_objetivo="paginas",
            objetivo_valor=5,
            activa=True,
        )
        MetaLectura.objects.create(
            usuario=self.user,
            nombre="Inactiva",
            tipo="diaria",
            tipo_objetivo="paginas",
            objetivo_valor=5,
            activa=False,
        )
        progreso = calcular_progreso_usuario(self.user)
        self.assertEqual(len(progreso), 1)


class MetaLecturaModelTests(TestCase):
    """Tests del modelo MetaLectura."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="test", password="Pass1234!")

    def test_str_representation(self):
        meta = MetaLectura.objects.create(
            usuario=self.user,
            nombre="Mi meta",
            tipo="diaria",
            tipo_objetivo="paginas",
            objetivo_valor=20,
        )
        self.assertIn("Mi meta", str(meta))
        self.assertIn("Diaria", str(meta))

    def test_obtener_inicio_periodo(self):
        from django.utils import timezone

        inicio_diario = obtener_inicio_periodo("diaria")
        self.assertEqual(inicio_diario, timezone.now().date())

    def test_meta_activa_por_defecto(self):
        meta = MetaLectura.objects.create(
            usuario=self.user,
            nombre="Defecto",
            tipo="diaria",
            tipo_objetivo="paginas",
            objetivo_valor=10,
        )
        self.assertTrue(meta.activa)
