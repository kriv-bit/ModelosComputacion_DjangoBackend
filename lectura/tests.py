from datetime import date, timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from libros.models import Autor, Libro

from .models import ProgresoLibro, SesionLectura


class BaseTest(TestCase):
    """Configuración base para todos los tests."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="lector_test",
            password="Pass1234!",
        )
        cls.autor = Autor.objects.create(
            nombre="Autor Test",
            pais="México",
            fecha_nacimiento="1970-01-01",
        )
        cls.libro = Libro.objects.create(
            titulo="Libro de prueba",
            autor=cls.autor,
            genero="Ficción",
            numero_paginas=300,
        )
        cls.libro2 = Libro.objects.create(
            titulo="Segundo libro",
            autor=cls.autor,
            genero="Ficción",
            numero_paginas=200,
        )

    def setUp(self):
        self.client = APIClient()
        self.client.force_login(self.user)


class SesionLecturaTests(BaseTest):
    """Tests para SesionLectura."""

    def test_iniciar_sesion(self):
        """Verifica que se pueda iniciar una sesión de lectura."""
        url = reverse("sesion-list-create")
        response = self.client.post(url, {"libro": self.libro.id}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["activa"])
        self.assertEqual(
            response.data["palabras_por_pagina"],
            SesionLectura.PALABRAS_POR_PAGINA_DEFAULT,
        )

    def test_iniciar_sesion_sin_libro(self):
        """Verifica que se pueda iniciar sesión sin asociar un libro."""
        url = reverse("sesion-list-create")
        response = self.client.post(url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNone(response.data["libro"])

    def test_listar_sesiones(self):
        """Verifica que se listen las sesiones del usuario."""
        SesionLectura.objects.create(usuario=self.user, libro=self.libro)
        SesionLectura.objects.create(usuario=self.user, libro=self.libro2)

        url = reverse("sesion-list-create")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_filtrar_sesiones_por_libro(self):
        """Verifica el filtrado de sesiones por libro."""
        SesionLectura.objects.create(usuario=self.user, libro=self.libro)
        SesionLectura.objects.create(usuario=self.user, libro=self.libro2)

        url = reverse("sesion-list-create") + f"?libro={self.libro.id}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["libro"], self.libro.id)

    def test_finalizar_sesion(self):
        """Verifica que al finalizar se calculen las métricas correctamente."""
        sesion = SesionLectura.objects.create(
            usuario=self.user,
            libro=self.libro,
        )
        # Simular que pasaron 30 minutos
        sesion.fecha_inicio = timezone.now() - timedelta(minutes=30)
        sesion.save()

        url = reverse("sesion-finalizar", args=[sesion.id])
        response = self.client.post(url, {"paginas_leidas": 15}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        sesion.refresh_from_db()
        self.assertFalse(sesion.activa)
        self.assertIsNotNone(sesion.fecha_fin)
        self.assertEqual(sesion.paginas_leidas, 15)
        # 15 páginas * 250 palabras / 30 min = 125 ppm
        self.assertEqual(sesion.palabras_por_minuto, 125)

    def test_finalizar_sesion_ya_finalizada(self):
        """Verifica que no se pueda finalizar una sesión ya finalizada."""
        sesion = SesionLectura.objects.create(
            usuario=self.user,
            libro=self.libro,
            activa=False,
        )
        url = reverse("sesion-finalizar", args=[sesion.id])
        response = self.client.post(url, {"paginas_leidas": 5}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_finalizar_sesion_actualiza_progreso(self):
        """Verifica que al finalizar se actualice el progreso del libro."""
        sesion = SesionLectura.objects.create(usuario=self.user, libro=self.libro)
        sesion.fecha_inicio = timezone.now() - timedelta(minutes=10)
        sesion.save()

        url = reverse("sesion-finalizar", args=[sesion.id])
        self.client.post(url, {"paginas_leidas": 20}, format="json")

        progreso = ProgresoLibro.objects.get(usuario=self.user, libro=self.libro)
        self.assertEqual(progreso.pagina_actual, 20)

    def test_ver_detalle_sesion(self):
        """Verifica que se pueda ver el detalle de una sesión."""
        sesion = SesionLectura.objects.create(
            usuario=self.user,
            libro=self.libro,
            notas="Prueba",
        )
        url = reverse("sesion-detail", args=[sesion.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["notas"], "Prueba")

    def test_eliminar_sesion(self):
        """Verifica que se pueda eliminar una sesión."""
        sesion = SesionLectura.objects.create(usuario=self.user, libro=self.libro)
        url = reverse("sesion-detail", args=[sesion.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(SesionLectura.objects.filter(id=sesion.id).exists())

    def test_sesion_requiere_autenticacion(self):
        """Verifica que se requiera autenticación."""
        self.client.logout()
        url = reverse("sesion-list-create")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class ProgresoLibroTests(BaseTest):
    """Tests para ProgresoLibro."""

    def test_crear_progreso(self):
        """Verifica que se pueda crear un progreso."""
        url = reverse("progreso-list-create")
        response = self.client.post(
            url,
            {"libro": self.libro.id, "pagina_actual": 50, "paginas_totales": 300},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["pagina_actual"], 50)
        self.assertIsNotNone(response.data["progreso_porcentaje"])

    def test_listar_progresos(self):
        """Verifica que se listen los progresos."""
        ProgresoLibro.objects.create(usuario=self.user, libro=self.libro)
        ProgresoLibro.objects.create(usuario=self.user, libro=self.libro2)

        url = reverse("progreso-list-create")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_progreso_unico_por_usuario_libro(self):
        """Verifica que no se duplique progreso para mismo usuario+libro."""
        ProgresoLibro.objects.create(
            usuario=self.user,
            libro=self.libro,
            pagina_actual=50,
        )
        url = reverse("progreso-list-create")
        response = self.client.post(
            url,
            {"libro": self.libro.id, "pagina_actual": 100},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_actualizar_progreso(self):
        """Verifica que se pueda actualizar el progreso."""
        progreso = ProgresoLibro.objects.create(
            usuario=self.user,
            libro=self.libro,
            pagina_actual=30,
        )
        url = reverse("progreso-detail", args=[progreso.id])
        response = self.client.patch(
            url,
            {"pagina_actual": 75},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["pagina_actual"], 75)

    def test_marcar_completado(self):
        """Verifica que se pueda marcar un libro como completado."""
        progreso = ProgresoLibro.objects.create(
            usuario=self.user,
            libro=self.libro,
            pagina_actual=300,
        )
        url = reverse("progreso-completar", args=[progreso.id])
        response = self.client.post(
            url,
            {"calificacion": 5},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["completado"])
        self.assertEqual(response.data["calificacion"], 5)

    def test_marcar_completado_sin_calificacion(self):
        """Verifica que se pueda marcar completado sin calificación."""
        progreso = ProgresoLibro.objects.create(
            usuario=self.user,
            libro=self.libro,
        )
        url = reverse("progreso-completar", args=[progreso.id])
        response = self.client.post(url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["completado"])
        self.assertIsNone(response.data["calificacion"])

    def test_marcar_completado_ya_completado(self):
        """Verifica que no se pueda marcar como completado si ya lo está."""
        progreso = ProgresoLibro.objects.create(
            usuario=self.user,
            libro=self.libro,
            completado=True,
        )
        url = reverse("progreso-completar", args=[progreso.id])
        response = self.client.post(url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_progreso_porcentaje(self):
        """Verifica el cálculo del porcentaje de progreso."""
        progreso = ProgresoLibro.objects.create(
            usuario=self.user,
            libro=self.libro,
            pagina_actual=75,
            paginas_totales=300,
        )
        self.assertEqual(progreso.progreso_porcentaje, 25.0)

    def test_progreso_porcentaje_sin_total(self):
        """Verifica que el porcentaje sea None si no hay total."""
        progreso = ProgresoLibro.objects.create(
            usuario=self.user,
            libro=self.libro,
            pagina_actual=50,
        )
        self.assertIsNone(progreso.progreso_porcentaje)


class EstadisticasTests(BaseTest):
    """Tests para las estadísticas de lectura."""

    def _crear_sesion(self, minutos_atras, paginas, libro=None):
        """Crea una sesión finalizada en el pasado."""
        sesion = SesionLectura.objects.create(
            usuario=self.user,
            libro=libro or self.libro,
        )
        sesion.fecha_inicio = timezone.now() - timedelta(minutes=minutos_atras)
        sesion.save()
        sesion.finalizar(paginas_leidas=paginas)
        return sesion

    def test_estadisticas_basicas(self):
        """Verifica que las estadísticas básicas sean correctas."""
        self._crear_sesion(minutos_atras=30, paginas=10)
        self._crear_sesion(minutos_atras=60, paginas=20)

        url = reverse("estadisticas")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_sesiones"], 2)
        self.assertEqual(response.data["total_paginas"], 30)
        self.assertGreater(response.data["total_tiempo_minutos"], 0)
        self.assertGreater(response.data["ppm_promedio"], 0)
        self.assertIn("racha_actual_dias", response.data)
        self.assertIn("racha_maxima_dias", response.data)

    def test_estadisticas_sin_sesiones(self):
        """Verifica estadísticas con cero sesiones."""
        url = reverse("estadisticas")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_sesiones"], 0)
        self.assertEqual(response.data["total_paginas"], 0)
        self.assertEqual(response.data["ppm_promedio"], 0)
        self.assertEqual(response.data["racha_actual_dias"], 0)
        self.assertEqual(response.data["libros_completados"], 0)

    def test_estadisticas_libros_completados(self):
        """Verifica el conteo de libros completados."""
        ProgresoLibro.objects.create(
            usuario=self.user,
            libro=self.libro,
            completado=True,
        )
        url = reverse("estadisticas")
        response = self.client.get(url)
        self.assertEqual(response.data["libros_completados"], 1)
        self.assertEqual(response.data["libros_en_lectura"], 0)


class ModeloTests(TestCase):
    """Tests de los modelos."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="test", password="Pass1234!")
        cls.autor = Autor.objects.create(
            nombre="Autor",
            pais="México",
            fecha_nacimiento="1980-01-01",
        )
        cls.libro = Libro.objects.create(titulo="Test", autor=cls.autor)

    def test_sesion_str(self):
        """Verifica el string representation de SesionLectura."""
        sesion = SesionLectura.objects.create(usuario=self.user, libro=self.libro)
        self.assertIn("test", str(sesion))
        self.assertIn("Test", str(sesion))

    def test_sesion_str_sin_libro(self):
        """Verifica el string sin libro."""
        sesion = SesionLectura.objects.create(usuario=self.user)
        self.assertIn("test", str(sesion))
        self.assertNotIn("None", str(sesion))

    def test_progreso_str(self):
        """Verifica el string representation de ProgresoLibro."""
        progreso = ProgresoLibro.objects.create(
            usuario=self.user,
            libro=self.libro,
            pagina_actual=42,
        )
        self.assertIn("test", str(progreso))
        self.assertIn("42", str(progreso))

    def test_sesion_orden(self):
        """Verifica que las sesiones se ordenen por fecha descendente."""
        s1 = SesionLectura.objects.create(usuario=self.user)
        s2 = SesionLectura.objects.create(usuario=self.user)
        self.assertEqual(
            list(SesionLectura.objects.all()),
            [s2, s1],
        )

    def test_progreso_unico(self):
        """Verifica la restricción unique_together."""
        ProgresoLibro.objects.create(usuario=self.user, libro=self.libro)
        with self.assertRaises(Exception):
            ProgresoLibro.objects.create(usuario=self.user, libro=self.libro)

    def test_finalizar_con_metodo(self):
        """Verifica el método finalizar() del modelo."""
        sesion = SesionLectura.objects.create(usuario=self.user)
        sesion.fecha_inicio = timezone.now() - timedelta(minutes=10)
        sesion.save()
        sesion.finalizar(paginas_leidas=5)

        self.assertFalse(sesion.activa)
        self.assertIsNotNone(sesion.fecha_fin)
        self.assertEqual(sesion.duracion_segundos, 600)  # 10 min = 600 seg
        self.assertEqual(sesion.paginas_leidas, 5)

    def test_marcar_completado_metodo(self):
        """Verifica el método marcar_completado() del modelo."""
        progreso = ProgresoLibro.objects.create(usuario=self.user, libro=self.libro)
        progreso.marcar_completado(calificacion=4)

        self.assertTrue(progreso.completado)
        self.assertIsNotNone(progreso.fecha_completado)
        self.assertEqual(progreso.calificacion, 4)
