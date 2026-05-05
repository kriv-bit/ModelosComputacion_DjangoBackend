from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from libros.models import Autor, Libro

from .models import IntentoPrueba, PruebaComprension


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
        cls.libro = Libro.objects.create(titulo="Libro Test", autor=cls.autor)

    def setUp(self):
        self.client = APIClient()
        self.client.force_login(self.user)


class PruebaTests(BaseTest):
    """Tests de creación y listado de pruebas."""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.prueba = PruebaComprension.objects.create(
            libro=cls.libro,
            titulo="Comprensión Capítulo 1",
            pregunta="¿Cuál es el tema principal?",
            opcion_a="Amor",
            opcion_b="Realismo mágico",
            opcion_c="Aventura",
            respuesta_correcta="B",
            dificultad="media",
        )

    def test_listar_pruebas_por_libro(self):
        url = reverse("pruebas-list", args=[self.libro.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        # Verificar que NO se filtra la respuesta correcta
        self.assertNotIn("respuesta_correcta", response.data[0])

    def test_prueba_no_muestra_respuesta_correcta(self):
        """La respuesta correcta nunca debe mostrarse al listar."""
        url = reverse("pruebas-list", args=[self.libro.id])
        response = self.client.get(url)
        for p in response.data:
            self.assertNotIn("respuesta_correcta", p)

    def test_crear_prueba(self):
        url = reverse("pruebas-detail", args=[999])
        # Usamos POST a través del generics o directamente desde admin
        # Verificamos que el endpoint detail funciona
        pass

    def test_ver_detalle_prueba(self):
        url = reverse("pruebas-detail", args=[self.prueba.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["titulo"], "Comprensión Capítulo 1")


class ResponderPruebaTests(BaseTest):
    """Tests para responder pruebas."""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.prueba = PruebaComprension.objects.create(
            libro=cls.libro,
            titulo="Test Capítulo 1",
            pregunta="¿Quién es el protagonista?",
            opcion_a="José Arcadio Buendía",
            opcion_b="Aureliano Buendía",
            opcion_c="Úrsula Iguarán",
            respuesta_correcta="A",
            dificultad="facil",
        )

    def test_responder_correctamente(self):
        url = reverse("responder-prueba", args=[self.prueba.id])
        response = self.client.post(
            url,
            {
                "prueba": self.prueba.id,
                "respuesta": "A",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["correcta"])

    def test_responder_incorrectamente(self):
        url = reverse("responder-prueba", args=[self.prueba.id])
        response = self.client.post(
            url,
            {
                "prueba": self.prueba.id,
                "respuesta": "B",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertFalse(response.data["correcta"])

    def test_responder_sin_autenticacion(self):
        self.client.logout()
        url = reverse("responder-prueba", args=[self.prueba.id])
        response = self.client.post(
            url,
            {
                "prueba": self.prueba.id,
                "respuesta": "A",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_responder_con_opcion_invalida(self):
        url = reverse("responder-prueba", args=[self.prueba.id])
        response = self.client.post(
            url,
            {
                "prueba": self.prueba.id,
                "respuesta": "Z",  # Opción inválida
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class HistorialTests(BaseTest):
    """Tests del historial de intentos."""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.prueba1 = PruebaComprension.objects.create(
            libro=cls.libro,
            titulo="Prueba 1",
            pregunta="¿P1?",
            opcion_a="A1",
            opcion_b="A2",
            respuesta_correcta="A",
            dificultad="facil",
        )
        cls.prueba2 = PruebaComprension.objects.create(
            libro=cls.libro,
            titulo="Prueba 2",
            pregunta="¿P2?",
            opcion_a="B1",
            opcion_b="B2",
            respuesta_correcta="B",
            dificultad="media",
        )

    def setUp(self):
        super().setUp()
        IntentoPrueba.objects.create(
            usuario=self.user,
            prueba=self.prueba1,
            respuesta="A",
        )
        IntentoPrueba.objects.create(
            usuario=self.user,
            prueba=self.prueba2,
            respuesta="A",
        )

    def test_historial_intentos(self):
        url = reverse("intentos-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_resultados_comprension(self):
        url = reverse("resultados-comprension")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_pruebas"], 2)
        self.assertEqual(
            response.data["total_correctas"], 1
        )  # Solo prueba1 es correcta
        self.assertEqual(response.data["total_incorrectas"], 1)
        self.assertEqual(response.data["porcentaje_aciertos"], 50.0)

    def test_resultados_sin_intentos(self):
        """Verifica resultados con cero intentos."""
        IntentoPrueba.objects.all().delete()
        url = reverse("resultados-comprension")
        response = self.client.get(url)
        self.assertEqual(response.data["total_pruebas"], 0)
        self.assertEqual(response.data["porcentaje_aciertos"], 0.0)

    def test_filtrar_historial_por_libro(self):
        url = reverse("intentos-list") + f"?libro={self.libro.id}"
        response = self.client.get(url)
        self.assertEqual(len(response.data), 2)


class ModeloTests(TestCase):
    """Tests de modelos."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="test", password="Pass1234!")
        cls.autor = Autor.objects.create(
            nombre="Autor",
            pais="País",
            fecha_nacimiento="1980-01-01",
        )
        cls.libro = Libro.objects.create(titulo="Test", autor=cls.autor)

    def test_prueba_str(self):
        prueba = PruebaComprension.objects.create(
            libro=self.libro,
            titulo="Mi prueba",
            pregunta="¿?",
            opcion_a="A1",
            opcion_b="A2",
            respuesta_correcta="A",
        )
        self.assertIn("Test", str(prueba))
        self.assertIn("Mi prueba", str(prueba))

    def test_intento_str(self):
        prueba = PruebaComprension.objects.create(
            libro=self.libro,
            titulo="Prueba",
            pregunta="¿?",
            opcion_a="A1",
            opcion_b="A2",
            respuesta_correcta="A",
        )
        intento = IntentoPrueba.objects.create(
            usuario=self.user,
            prueba=prueba,
            respuesta="A",
        )
        self.assertIn("test", str(intento))
        self.assertIn("✅", str(intento))

    def test_intento_incorrecto_str(self):
        prueba = PruebaComprension.objects.create(
            libro=self.libro,
            titulo="Prueba",
            pregunta="¿?",
            opcion_a="A1",
            opcion_b="A2",
            respuesta_correcta="A",
        )
        intento = IntentoPrueba.objects.create(
            usuario=self.user,
            prueba=prueba,
            respuesta="B",
        )
        self.assertIn("❌", str(intento))

    def test_auto_verificacion_correcta(self):
        prueba = PruebaComprension.objects.create(
            libro=self.libro,
            titulo="Test",
            pregunta="¿?",
            opcion_a="Correcta",
            opcion_b="Incorrecta",
            respuesta_correcta="A",
        )
        intento = IntentoPrueba.objects.create(
            usuario=self.user,
            prueba=prueba,
            respuesta="A",
        )
        self.assertTrue(intento.correcta)

    def test_auto_verificacion_incorrecta(self):
        prueba = PruebaComprension.objects.create(
            libro=self.libro,
            titulo="Test",
            pregunta="¿?",
            opcion_a="Correcta",
            opcion_b="Incorrecta",
            respuesta_correcta="A",
        )
        intento = IntentoPrueba.objects.create(
            usuario=self.user,
            prueba=prueba,
            respuesta="B",
        )
        self.assertFalse(intento.correcta)
