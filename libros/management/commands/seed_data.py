"""
Comando de Django para poblar la base de datos con datos de prueba.
Replica exactamente los datos de mock-data.ts del frontend Angular.

Uso: python manage.py seed_data
"""

from datetime import date

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from cuentas.models import PerfilUsuario
from libros.models import Autor, Favorito, Libro, Prestamo, Resena


class Command(BaseCommand):
    help = "Pobla la base de datos con datos de prueba (replica mock-data.ts)"

    def handle(self, *args, **options):
        self.stdout.write("🌱 Iniciando seed de datos...")

        # ─── Usuarios ─────────────────────────────────────────
        users_data = [
            {
                "username": "daniel.lasso",
                "email": "daniel.lasso@lassriver.com",
                "first_name": "Daniel",
                "last_name": "Lasso",
                "password": "LassRiver2026!",
                "perfil": {
                    "fecha_nacimiento": date(2000, 1, 15),
                    "genero": "M",
                    "pais": "Colombia",
                    "rol": "user",
                },
            },
            {
                "username": "ana.rivera",
                "email": "ana.rivera@lassriver.com",
                "first_name": "Ana",
                "last_name": "Rivera",
                "password": "LassRiver2026!",
                "perfil": {
                    "fecha_nacimiento": date(1995, 6, 20),
                    "genero": "F",
                    "pais": "Colombia",
                    "rol": "librarian",
                },
            },
            {
                "username": "admin",
                "email": "admin@lassriver.com",
                "first_name": "Admin",
                "last_name": "LassRiver",
                "password": "LassRiver2026!",
                "perfil": {
                    "fecha_nacimiento": date(1990, 3, 10),
                    "genero": "M",
                    "pais": "Colombia",
                    "rol": "admin",
                },
            },
        ]

        created_users = {}
        for ud in users_data:
            perfil_data = ud.pop("perfil")
            password = ud.pop("password")
            user, created = User.objects.get_or_create(
                username=ud["username"],
                defaults=ud,
            )
            if created:
                user.set_password(password)
                user.save()
                PerfilUsuario.objects.create(user=user, **perfil_data)
                self.stdout.write(f"  ✅ Usuario creado: {user.username} ({perfil_data['rol']})")
            else:
                self.stdout.write(f"  ⏭️  Usuario ya existe: {user.username}")
            created_users[user.username] = user

        daniel = created_users["daniel.lasso"]
        ana = created_users["ana.rivera"]

        # ─── Autores ──────────────────────────────────────────
        autores_data = [
            {"nombre": "Gabriel García Márquez", "pais": "Colombia", "fecha_nacimiento": date(1927, 3, 6)},
            {"nombre": "Miguel de Cervantes", "pais": "España", "fecha_nacimiento": date(1547, 9, 29)},
            {"nombre": "Carlos Ruiz Zafón", "pais": "España", "fecha_nacimiento": date(1964, 9, 25)},
            {"nombre": "Julio Cortázar", "pais": "Argentina", "fecha_nacimiento": date(1914, 8, 26)},
            {"nombre": "Isabel Allende", "pais": "Chile", "fecha_nacimiento": date(1942, 8, 2)},
            {"nombre": "Jorge Luis Borges", "pais": "Argentina", "fecha_nacimiento": date(1899, 8, 24)},
            {"nombre": "Juan Rulfo", "pais": "México", "fecha_nacimiento": date(1917, 5, 16)},
            {"nombre": "Ernesto Sabato", "pais": "Argentina", "fecha_nacimiento": date(1911, 6, 24)},
            {"nombre": "Roberto Bolaño", "pais": "Chile", "fecha_nacimiento": date(1953, 4, 28)},
            {"nombre": "Mario Vargas Llosa", "pais": "Perú", "fecha_nacimiento": date(1936, 3, 28)},
        ]

        autores = {}
        for ad in autores_data:
            autor, _ = Autor.objects.get_or_create(nombre=ad["nombre"], defaults=ad)
            autores[autor.nombre] = autor

        self.stdout.write(f"  ✅ {len(autores)} autores listos")

        # ─── Libros ───────────────────────────────────────────
        libros_data = [
            {"titulo": "Cien Años de Soledad", "autor": "Gabriel García Márquez", "isbn": "978-0307474728", "genero": "Ficción", "idioma": "Español", "editorial": "Editorial Sudamericana", "numero_paginas": 417, "descripcion": "Una obra maestra del realismo mágico que narra la historia de la familia Buendía a lo largo de siete generaciones en el pueblo ficticio de Macondo.", "portada_url": "https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=300&h=450&fit=crop", "disponible": True},
            {"titulo": "El Amor en los Tiempos del Cólera", "autor": "Gabriel García Márquez", "isbn": "978-0307389732", "genero": "Romance", "idioma": "Español", "editorial": "Oveja Negra", "numero_paginas": 368, "descripcion": "Una historia de amor que trasciende el tiempo.", "portada_url": "https://images.unsplash.com/photo-1543002588-bfa74002ed7e?w=300&h=450&fit=crop", "disponible": True},
            {"titulo": "Don Quijote de la Mancha", "autor": "Miguel de Cervantes", "isbn": "978-8420412146", "genero": "Clásicos", "idioma": "Español", "editorial": "Real Academia Española", "numero_paginas": 863, "descripcion": "La obra cumbre de la literatura española.", "portada_url": "https://images.unsplash.com/photo-1512820790803-83ca734da794?w=300&h=450&fit=crop", "disponible": False},
            {"titulo": "La Sombra del Viento", "autor": "Carlos Ruiz Zafón", "isbn": "978-0143126393", "genero": "Misterio", "idioma": "Español", "editorial": "Planeta", "numero_paginas": 487, "descripcion": "Un joven descubre un libro maldito en la Barcelona de posguerra.", "portada_url": "https://images.unsplash.com/photo-1541963463532-d68292c34b19?w=300&h=450&fit=crop", "disponible": True},
            {"titulo": "Rayuela", "autor": "Julio Cortázar", "isbn": "978-8420471778", "genero": "Ficción", "idioma": "Español", "editorial": "Alfaguara", "numero_paginas": 600, "descripcion": "Una novela experimental que puede leerse de múltiples formas.", "portada_url": "https://images.unsplash.com/photo-1495446815901-a7297e633e8d?w=300&h=450&fit=crop", "disponible": True},
            {"titulo": "La Casa de los Espíritus", "autor": "Isabel Allende", "isbn": "978-1501117015", "genero": "Ficción", "idioma": "Español", "editorial": "Plaza & Janés", "numero_paginas": 433, "descripcion": "La saga de la familia Trueba.", "portada_url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=300&h=450&fit=crop", "disponible": True},
            {"titulo": "Ficciones", "autor": "Jorge Luis Borges", "isbn": "978-0802130303", "genero": "Cuentos", "idioma": "Español", "editorial": "Emecé", "numero_paginas": 174, "descripcion": "Colección de cuentos que exploran temas como el tiempo y el infinito.", "portada_url": "https://images.unsplash.com/photo-1519682337058-a94d519337bc?w=300&h=450&fit=crop", "disponible": False},
            {"titulo": "Pedro Páramo", "autor": "Juan Rulfo", "isbn": "978-0802133908", "genero": "Ficción", "idioma": "Español", "editorial": "Fondo de Cultura Económica", "numero_paginas": 124, "descripcion": "Juan Preciado regresa al pueblo fantasmal de Comala.", "portada_url": "https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=300&h=450&fit=crop", "disponible": True},
            {"titulo": "El Túnel", "autor": "Ernesto Sabato", "isbn": "978-8432217036", "genero": "Ficción Psicológica", "idioma": "Español", "editorial": "Seix Barral", "numero_paginas": 158, "descripcion": "La confesión de un pintor sobre el asesinato.", "portada_url": "https://images.unsplash.com/photo-1497633762265-9d179a990aa6?w=300&h=450&fit=crop", "disponible": True},
            {"titulo": "Los Detectives Salvajes", "autor": "Roberto Bolaño", "isbn": "978-0374191481", "genero": "Ficción", "idioma": "Español", "editorial": "Anagrama", "numero_paginas": 609, "descripcion": "Un grupo de poetas busca a una poetisa perdida.", "portada_url": "https://images.unsplash.com/photo-1506880018603-83d5b814b5a6?w=300&h=450&fit=crop", "disponible": True},
            {"titulo": "Crónica de una Muerte Anunciada", "autor": "Gabriel García Márquez", "isbn": "978-0307475084", "genero": "Ficción", "idioma": "Español", "editorial": "Editorial Sudamericana", "numero_paginas": 122, "descripcion": "La reconstrucción de un asesinato anunciado.", "portada_url": "https://images.unsplash.com/photo-1532012197267-da84d127e765?w=300&h=450&fit=crop", "disponible": True},
            {"titulo": "La Ciudad y los Perros", "autor": "Mario Vargas Llosa", "isbn": "978-8420412580", "genero": "Ficción", "idioma": "Español", "editorial": "Alfaguara", "numero_paginas": 408, "descripcion": "Violencia y corrupción en un colegio militar de Lima.", "portada_url": "https://images.unsplash.com/photo-1524995997946-a1c2e315a42f?w=300&h=450&fit=crop", "disponible": False},
        ]

        libros = {}
        for ld in libros_data:
            autor_nombre = ld.pop("autor")
            libro, _ = Libro.objects.get_or_create(
                titulo=ld["titulo"],
                defaults={"autor": autores[autor_nombre], **ld},
            )
            libros[libro.titulo] = libro

        self.stdout.write(f"  ✅ {len(libros)} libros listos")

        # ─── Reseñas ──────────────────────────────────────────
        resenas_data = [
            {"libro": "Cien Años de Soledad", "usuario": daniel, "calificacion": 5, "comentario": "Una obra maestra absoluta.", "marcada": False},
            {"libro": "Cien Años de Soledad", "usuario": ana, "calificacion": 5, "comentario": "El realismo mágico en su máxima expresión.", "marcada": False},
            {"libro": "El Amor en los Tiempos del Cólera", "usuario": daniel, "calificacion": 4, "comentario": "Una historia de amor épica.", "marcada": False},
            {"libro": "La Sombra del Viento", "usuario": created_users["admin"], "calificacion": 5, "comentario": "Zafón crea un universo literario fascinante.", "marcada": False},
            {"libro": "Don Quijote de la Mancha", "usuario": daniel, "calificacion": 5, "comentario": "El clásico por excelencia.", "marcada": False},
            {"libro": "Ficciones", "usuario": created_users["admin"], "calificacion": 3, "comentario": "Contenido inapropiado.", "marcada": True, "razon_marca": "Comentario ofensivo"},
        ]

        count = 0
        for rd in resenas_data:
            libro_titulo = rd.pop("libro")
            razon = rd.pop("razon_marca", "")
            _, created = Resena.objects.get_or_create(
                libro=libros[libro_titulo],
                usuario=rd["usuario"],
                defaults={**rd, "razon_marca": razon},
            )
            if created:
                count += 1

        self.stdout.write(f"  ✅ {count} reseñas creadas")

        # ─── Préstamos ────────────────────────────────────────
        prestamos_data = [
            {"libro": "Don Quijote de la Mancha", "usuario": daniel, "fecha_vencimiento": date(2026, 5, 15), "estado": "active"},
            {"libro": "Ficciones", "usuario": daniel, "fecha_vencimiento": date(2026, 4, 25), "estado": "overdue"},
            {"libro": "La Ciudad y los Perros", "usuario": ana, "fecha_vencimiento": date(2026, 5, 20), "estado": "active"},
            {"libro": "Cien Años de Soledad", "usuario": daniel, "fecha_vencimiento": date(2026, 4, 15), "fecha_devolucion": date(2026, 4, 14), "estado": "returned"},
        ]

        count = 0
        for pd in prestamos_data:
            libro_titulo = pd.pop("libro")
            _, created = Prestamo.objects.get_or_create(
                libro=libros[libro_titulo],
                usuario=pd["usuario"],
                estado=pd["estado"],
                defaults=pd,
            )
            if created:
                count += 1

        self.stdout.write(f"  ✅ {count} préstamos creados")

        self.stdout.write(self.style.SUCCESS("\n🎉 Seed completado exitosamente!"))
        self.stdout.write(
            "\n  Credenciales de prueba:\n"
            "  ──────────────────────\n"
            "  daniel.lasso / LassRiver2026!  (user)\n"
            "  ana.rivera   / LassRiver2026!  (librarian)\n"
            "  admin        / LassRiver2026!  (admin)\n"
        )
