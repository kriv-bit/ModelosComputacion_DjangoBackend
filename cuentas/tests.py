from datetime import date

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from .models import PerfilUsuario


class RegistroTests(TestCase):
    """Pruebas para el registro de usuarios."""

    def setUp(self):
        self.client = APIClient()
        self.url = reverse("registro")
        self.fecha_nac = date(2000, 1, 15)

    def test_registro_exitoso(self):
        """Verifica que un usuario pueda registrarse correctamente."""
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "Password123!",
            "password2": "Password123!",
            "fecha_nacimiento": self.fecha_nac,
            "genero": "M",
            "pais": "México",
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["username"], "testuser")
        self.assertEqual(response.data["email"], "test@example.com")
        self.assertTrue(User.objects.filter(username="testuser").exists())
        self.assertTrue(
            PerfilUsuario.objects.filter(user__username="testuser").exists()
        )

    def test_registro_passwords_no_coinciden(self):
        """Verifica que falle si las contraseñas no coinciden."""
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "Password123!",
            "password2": "Password456!",
            "fecha_nacimiento": self.fecha_nac,
            "genero": "M",
            "pais": "México",
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password2", response.data)

    def test_registro_campos_faltantes(self):
        """Verifica que falle si faltan campos obligatorios."""
        data = {"username": "testuser"}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registro_username_duplicado(self):
        """Verifica que no se permitan usernames duplicados."""
        User.objects.create_user(username="testuser", password="Pass123!")
        data = {
            "username": "testuser",
            "email": "otro@example.com",
            "password": "Password123!",
            "password2": "Password123!",
            "fecha_nacimiento": self.fecha_nac,
            "genero": "F",
            "pais": "Argentina",
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registro_password_debil(self):
        """Verifica que una contraseña débil sea rechazada."""
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "123",
            "password2": "123",
            "fecha_nacimiento": date(2000, 1, 15),
            "genero": "M",
            "pais": "México",
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LoginTests(TestCase):
    """Pruebas para el inicio de sesión."""

    def setUp(self):
        self.client = APIClient()
        self.url = reverse("login")
        self.password = "Password123!"
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password=self.password,
        )

    def test_login_exitoso(self):
        """Verifica que un usuario pueda iniciar sesión."""
        data = {
            "username": "testuser",
            "password": self.password,
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "testuser")

    def test_login_credenciales_invalidas(self):
        """Verifica que falle con credenciales incorrectas."""
        data = {
            "username": "testuser",
            "password": "WrongPassword!",
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_usuario_no_existe(self):
        """Verifica que falle si el usuario no existe."""
        data = {
            "username": "noexiste",
            "password": "Password123!",
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PerfilTests(TestCase):
    """Pruebas para el perfil de usuario."""

    def setUp(self):
        self.client = APIClient()
        self.url = reverse("perfil")
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="Password123!",
        )
        PerfilUsuario.objects.create(
            user=self.user,
            fecha_nacimiento=date(2000, 1, 15),
            genero="M",
            pais="México",
        )

    def test_perfil_requiere_autenticacion(self):
        """Verifica que se requiera autenticación para ver el perfil."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_obtener_perfil(self):
        """Verifica que un usuario autenticado pueda ver su perfil."""
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "testuser")
        self.assertEqual(response.data["email"], "test@example.com")
        self.assertEqual(response.data["genero"], "M")
        self.assertEqual(response.data["pais"], "México")
        self.assertIn("edad", response.data)

    def test_actualizar_perfil(self):
        """Verifica que un usuario pueda actualizar su perfil."""
        self.client.force_login(self.user)
        data = {
            "fecha_nacimiento": "1995-06-20",
            "genero": "F",
            "pais": "Colombia",
        }
        response = self.client.patch(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["genero"], "F")
        self.assertEqual(response.data["pais"], "Colombia")

    def test_edad_calculada(self):
        """Verifica que la edad se calcule correctamente."""
        from datetime import date

        hace_25_anios = date(
            date.today().year - 25, date.today().month, date.today().day
        )
        perfil = self.user.perfil
        perfil.fecha_nacimiento = hace_25_anios
        perfil.save()
        self.assertEqual(perfil.edad, 25)


class CambioPasswordTests(TestCase):
    """Pruebas para el cambio de contraseña."""

    def setUp(self):
        self.client = APIClient()
        self.url = reverse("cambiar-password")
        self.password = "Password123!"
        self.user = User.objects.create_user(
            username="testuser",
            password=self.password,
        )

    def test_cambio_password_exitoso(self):
        """Verifica que un usuario pueda cambiar su contraseña."""
        self.client.force_login(self.user)
        data = {
            "password_actual": self.password,
            "password_nueva": "NuevaPass123!",
            "password_nueva2": "NuevaPass123!",
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verificar que la nueva contraseña funciona
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("NuevaPass123!"))

    def test_cambio_password_actual_incorrecta(self):
        """Verifica que falle si la contraseña actual es incorrecta."""
        self.client.force_login(self.user)
        data = {
            "password_actual": "WrongPassword!",
            "password_nueva": "NuevaPass123!",
            "password_nueva2": "NuevaPass123!",
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cambio_password_no_coinciden(self):
        """Verifica que falle si las nuevas contraseñas no coinciden."""
        self.client.force_login(self.user)
        data = {
            "password_actual": self.password,
            "password_nueva": "NuevaPass123!",
            "password_nueva2": "OtraPass123!",
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cambio_password_requiere_autenticacion(self):
        """Verifica que se requiera autenticación para cambiar contraseña."""
        data = {
            "password_actual": "test",
            "password_nueva": "NuevaPass123!",
            "password_nueva2": "NuevaPass123!",
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class LogoutTests(TestCase):
    """Pruebas para el cierre de sesión."""

    def setUp(self):
        self.client = APIClient()
        self.url = reverse("logout")
        self.user = User.objects.create_user(
            username="testuser",
            password="Password123!",
        )

    def test_logout_exitoso(self):
        """Verifica que un usuario pueda cerrar sesión."""
        self.client.force_login(self.user)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class PerfilUsuarioModelTests(TestCase):
    """Pruebas del modelo PerfilUsuario."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="Password123!",
        )
        self.perfil = PerfilUsuario.objects.create(
            user=self.user,
            fecha_nacimiento=date(2000, 1, 15),
            genero="M",
            pais="México",
        )

    def test_str_representation(self):
        """Verifica la representación en string del perfil."""
        self.assertEqual(str(self.perfil), "Perfil de testuser")

    def test_edad_property(self):
        """Verifica que la propiedad edad funcione."""
        self.assertIsInstance(self.perfil.edad, int)
        self.assertGreater(self.perfil.edad, 0)

    def test_perfil_se_crea_con_valores_correctos(self):
        """Verifica que el perfil se haya creado con los valores correctos."""
        self.assertEqual(self.perfil.user, self.user)
        self.assertEqual(self.perfil.genero, "M")
        self.assertEqual(self.perfil.pais, "México")
        self.assertIsNotNone(self.perfil.fecha_registro)
