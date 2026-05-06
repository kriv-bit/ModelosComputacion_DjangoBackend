from datetime import date, timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from .models import Autor, Favorito, Libro, Prestamo, Resena

# ─── Helpers ────────────────────────────────────────────────────────────────

def make_autor(**kwargs):
    """Crea un Autor con todos los campos NOT NULL completos."""
    defaults = {
        "nombre": "Autor Test",
        "pais": "Colombia",
        "fecha_nacimiento": date(1970, 1, 1),
    }
    defaults.update(kwargs)
    return Autor.objects.create(**defaults)


def make_libro(autor, **kwargs):
    """Crea un Libro con valores mínimos válidos."""
    defaults = {
        "titulo": "Libro Test",
        "autor": autor,
        "isbn": "1234567890123",
        "disponible": True,
    }
    defaults.update(kwargs)
    return Libro.objects.create(**defaults)


# ─── Model Tests ────────────────────────────────────────────────────────────

class LibrosModelTests(TestCase):
    """Pruebas para los modelos de la app libros."""

    def setUp(self):
        self.autor = make_autor(nombre="Gabriel García Márquez")
        self.libro = make_libro(self.autor, titulo="Cien Años de Soledad")
        self.user = User.objects.create_user(username="testuser", password="Pass123!")

    def test_libro_str(self):
        self.assertEqual(str(self.libro), "Cien Años de Soledad")

    def test_autor_str(self):
        self.assertEqual(str(self.autor), "Gabriel García Márquez")

    def test_rating_inicial_sin_resenas(self):
        """Un libro sin reseñas debe tener rating 0 y review_count 0."""
        self.assertEqual(self.libro.rating, 0)
        self.assertEqual(self.libro.review_count, 0)

    def test_rating_se_calcula_con_resenas(self):
        """El rating debe ser el promedio de las calificaciones."""
        Resena.objects.create(
            libro=self.libro, usuario=self.user, calificacion=5, comentario="Excelente"
        )
        user2 = User.objects.create_user(username="user2", password="Pass123!")
        Resena.objects.create(
            libro=self.libro, usuario=user2, calificacion=3, comentario="Bueno"
        )
        self.libro.refresh_from_db()
        self.assertEqual(self.libro.rating, 4.0)
        self.assertEqual(self.libro.review_count, 2)

    def test_disponible_por_defecto(self):
        self.assertTrue(self.libro.disponible)


# ─── API Tests: Libros ───────────────────────────────────────────────────────

class LibrosAPITests(TestCase):
    """Pruebas de endpoints de la API de libros."""

    def setUp(self):
        self.client = APIClient()
        self.autor = make_autor()
        self.libro = make_libro(self.autor)
        self.user = User.objects.create_user(username="testuser", password="Pass123!")

    def test_listar_libros_publico(self):
        """El listado de libros debe ser público (sin autenticación)."""
        url = reverse("libro-list-create")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "Libro Test")

    def test_listar_libros_campos_correctos(self):
        """Verifica que el serializer mapee los campos al formato del frontend."""
        url = reverse("libro-list-create")
        response = self.client.get(url)
        libro_data = response.data[0]
        self.assertIn("id", libro_data)
        self.assertIn("title", libro_data)
        self.assertIn("author", libro_data)
        self.assertIn("available", libro_data)
        self.assertIn("rating", libro_data)

    def test_crear_resena_autenticado(self):
        """Un usuario autenticado puede crear una reseña."""
        self.client.force_authenticate(user=self.user)
        url = reverse("resena-list-create")
        data = {
            "bookId": self.libro.id,
            "rating": 5,
            "comment": "Increíble libro",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Resena.objects.count(), 1)

    def test_crear_resena_sin_autenticacion_falla(self):
        """Sin autenticación no se puede crear una reseña."""
        url = reverse("resena-list-create")
        data = {"bookId": self.libro.id, "rating": 4, "comment": "Bueno"}
        response = self.client.post(url, data, format="json")
        # Con TokenAuthentication, DRF devuelve 401
        self.assertIn(response.status_code, [
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
        ])

    def test_toggle_favorito_agrega(self):
        """Un usuario autenticado puede añadir un favorito."""
        self.client.force_authenticate(user=self.user)
        url = reverse("favorito-list-create")
        data = {"bookId": self.libro.id}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Favorito.objects.filter(usuario=self.user, libro=self.libro).exists()
        )

    def test_toggle_favorito_elimina(self):
        """Un usuario puede eliminar un favorito."""
        Favorito.objects.create(usuario=self.user, libro=self.libro)
        self.client.force_authenticate(user=self.user)
        url = reverse("favorito-delete", args=[self.libro.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            Favorito.objects.filter(usuario=self.user, libro=self.libro).exists()
        )


# ─── Préstamos Tests ─────────────────────────────────────────────────────────

class PrestamosTests(TestCase):
    """Pruebas para el sistema de préstamos."""

    def setUp(self):
        self.client = APIClient()
        self.autor = make_autor()
        self.libro = make_libro(self.autor, titulo="Libro Prestable", disponible=True)
        # El usuario necesita ser staff (admin/librarian) para crear préstamos
        self.user = User.objects.create_user(
            username="librarian", password="Pass123!", is_staff=True
        )

    def test_crear_prestamo(self):
        """Se puede crear un préstamo y el libro pasa a no disponible."""
        self.client.force_authenticate(user=self.user)
        url = reverse("prestamo-list-create")
        vencimiento = date.today() + timedelta(days=7)
        data = {
            "bookId": self.libro.id,
            "dueDate": vencimiento.isoformat(),
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # El libro ya no debe estar disponible
        self.libro.refresh_from_db()
        self.assertFalse(self.libro.disponible)

    def test_devolver_prestamo(self):
        """Al devolver un préstamo, el libro vuelve a estar disponible."""
        self.libro.disponible = False
        self.libro.save()
        prestamo = Prestamo.objects.create(
            libro=self.libro,
            usuario=self.user,
            fecha_vencimiento=date.today() + timedelta(days=7),
            estado="active",
        )

        self.client.force_authenticate(user=self.user)
        url = reverse("prestamo-return", args=[prestamo.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        prestamo.refresh_from_db()
        self.assertEqual(prestamo.estado, "returned")
        self.libro.refresh_from_db()
        self.assertTrue(self.libro.disponible)

    def test_no_prestar_libro_no_disponible(self):
        """No se puede prestar un libro que ya no está disponible."""
        self.libro.disponible = False
        self.libro.save()

        self.client.force_authenticate(user=self.user)
        url = reverse("prestamo-list-create")
        data = {
            "bookId": self.libro.id,
            "dueDate": (date.today() + timedelta(days=7)).isoformat(),
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
