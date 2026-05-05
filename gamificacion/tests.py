from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from lectura.models import ProgresoLibro

from .models import Logro, LogroUsuario
from .services import progreso_logros, verificar_logros


class LogroTests(TestCase):
    """Tests para el módulo de gamificación."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="lector_test",
            password="Pass1234!",
        )

    def setUp(self):
        self.client = APIClient()
        self.client.force_login(self.user)

    # --- Tests de endpoints ---

    def test_listar_logros(self):
        """Verifica que se listen los logros del catálogo."""
        url = reverse("logros-lista")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Deberían venir los 20 logros de la seed
        self.assertGreaterEqual(len(response.data), 20)

    def test_mis_logros_vacio(self):
        """Verifica que un usuario nuevo no tenga logros."""
        url = reverse("mis-logros")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_verificar_sin_logros(self):
        """Verificar sin actividad no desbloquea nada."""
        url = reverse("verificar-logros")
        response = self.client.post(url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_nuevos"], 0)

    def test_progreso_logros(self):
        """Verifica que el progreso de logros funcione."""
        url = reverse("progreso-logros")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 20)
        # Todos deberían estar en 0% y no desbloqueados
        for item in response.data:
            self.assertFalse(item["desbloqueado"])

    def test_autenticacion_requerida(self):
        """Verifica que se requiera autenticación."""
        self.client.logout()
        urls = [
            reverse("logros-lista"),
            reverse("mis-logros"),
            reverse("progreso-logros"),
            reverse("verificar-logros"),
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class LogroServiceTests(TestCase):
    """Tests para el servicio de verificación de logros."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="test_user",
            password="Pass1234!",
        )

    def test_verificar_primeros_pasos(self):
        """Verifica que al tener 1 sesión se desbloquee 'Primeros Pasos'."""
        from datetime import timedelta

        from django.utils import timezone

        from lectura.models import SesionLectura

        sesion = SesionLectura.objects.create(usuario=self.user)
        sesion.fecha_inicio = timezone.now() - timedelta(minutes=5)
        sesion.save()
        sesion.finalizar(paginas_leidas=5)

        nuevos = verificar_logros(self.user)
        nombres = [l.nombre for l in nuevos]

        self.assertIn("Primeros Pasos", nombres)
        self.assertTrue(
            LogroUsuario.objects.filter(
                usuario=self.user, logro__nombre="Primeros Pasos"
            ).exists()
        )

    def test_no_duplicar_logros(self):
        """Verifica que no se dupliquen logros al verificar dos veces."""
        from datetime import timedelta

        from django.utils import timezone

        from lectura.models import SesionLectura

        sesion = SesionLectura.objects.create(usuario=self.user)
        sesion.fecha_inicio = timezone.now() - timedelta(minutes=5)
        sesion.save()
        sesion.finalizar(paginas_leidas=5)

        verificar_logros(self.user)
        nuevos = verificar_logros(self.user)  # Segunda vez

        self.assertEqual(len(nuevos), 0)  # No debería desbloquear nada nuevo
        self.assertEqual(LogroUsuario.objects.filter(usuario=self.user).count(), 1)

    def test_verificar_libro_completado(self):
        """Verifica que al completar un libro se desbloquee el logro."""
        from django.utils import timezone

        from libros.models import Autor, Libro

        autor = Autor.objects.create(
            nombre="Autor",
            pais="País",
            fecha_nacimiento="1980-01-01",
        )
        libro = Libro.objects.create(titulo="Test", autor=autor)

        ProgresoLibro.objects.create(
            usuario=self.user,
            libro=libro,
            completado=True,
            fecha_completado=timezone.now(),
        )

        nuevos = verificar_logros(self.user)
        nombres = [l.nombre for l in nuevos]
        self.assertIn("Primer Libro", nombres)

    def test_progreso_logros_estructura(self):
        """Verifica la estructura del progreso de logros."""
        resultado = progreso_logros(self.user)

        self.assertGreater(len(resultado), 0)
        item = resultado[0]
        self.assertIn("logro_id", item)
        self.assertIn("logro_nombre", item)
        self.assertIn("logro_icono", item)
        self.assertIn("progreso_porcentaje", item)
        self.assertIn("desbloqueado", item)
        self.assertIn("valor_actual", item)
        self.assertIn("requisito_valor", item)


class LogroModelTests(TestCase):
    """Tests de los modelos de gamificación."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="test", password="Pass1234!")
        cls.logro = Logro.objects.create(
            nombre="Logro Test",
            descripcion="Descripción test",
            icono="🎯",
            categoria="sesiones",
            tipo_requisito="sesiones",
            requisito_valor=5,
        )

    def test_logro_str(self):
        """Verifica el string representation de Logro."""
        self.assertIn("🎯", str(self.logro))
        self.assertIn("Logro Test", str(self.logro))

    def test_logro_usuario_str(self):
        """Verifica el string representation de LogroUsuario."""
        lu = LogroUsuario.objects.create(usuario=self.user, logro=self.logro)
        self.assertIn("test", str(lu))
        self.assertIn("Logro Test", str(lu))

    def test_logro_activo_por_defecto(self):
        """Verifica que los logros sean activos por defecto."""
        self.assertTrue(self.logro.activo)

    def test_unique_together(self):
        """Verifica la restricción unique_together."""
        LogroUsuario.objects.create(usuario=self.user, logro=self.logro)
        with self.assertRaises(Exception):
            LogroUsuario.objects.create(usuario=self.user, logro=self.logro)
