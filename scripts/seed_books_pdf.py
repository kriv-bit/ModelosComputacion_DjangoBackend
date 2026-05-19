"""
Script de seed para poblar la base de datos con libros de dominio público
y sus PDFs desde planetebook.com.

Uso:
    python manage.py shell < scripts/seed_books_pdf.py
O:
    python manage.py runscript seed_books_pdf  (requiere django-extensions)

Alternativa directa:
    ./venv/bin/python scripts/seed_books_pdf.py
"""

import os
import sys
import django

# Configurar Django si se ejecuta directamente
if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mi_proyecto.settings")
    django.setup()

from libros.models import Autor, Libro

# ─── Datos de libros de dominio público ────────────────────────────────────
BOOKS_DATA = [
    {
        "autor": {
            "nombre": "Jane Austen",
            "pais": "Reino Unido",
            "fecha_nacimiento": "1775-12-16",
        },
        "libro": {
            "titulo": "Pride and Prejudice",
            "genero": "Classic Fiction",
            "idioma": "English",
            "numero_paginas": 432,
            "editorial": "T. Egerton (1813)",
            "descripcion": (
                "Pride and Prejudice follows the turbulent relationship between Elizabeth Bennet, "
                "the daughter of a country gentleman, and Fitzwilliam Darcy, a rich aristocratic landowner. "
                "They must overcome the titular sins of pride and prejudice in order to fall in love and marry."
            ),
            "portada_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/17/PrideAndPrejudiceTitlePage.jpg/800px-PrideAndPrejudiceTitlePage.jpg",
            "pdf_source_url": "https://www.planetebook.com/free-ebooks/pride-and-prejudice.pdf",
        },
    },
    {
        "autor": {
            "nombre": "Mary Shelley",
            "pais": "Reino Unido",
            "fecha_nacimiento": "1797-08-30",
        },
        "libro": {
            "titulo": "Frankenstein",
            "genero": "Gothic Horror",
            "idioma": "English",
            "numero_paginas": 280,
            "editorial": "Lackington, Hughes, Harding, Mavor & Jones (1818)",
            "descripcion": (
                "Frankenstein tells the story of Victor Frankenstein, a scientist who creates a sapient "
                "creature in an unorthodox scientific experiment. The novel raises questions about the "
                "nature of humanity and the ethical limits of scientific ambition."
            ),
            "portada_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/35/Frankenstein_1818_edition_title_page.jpg/800px-Frankenstein_1818_edition_title_page.jpg",
            "pdf_source_url": "https://www.planetebook.com/free-ebooks/frankenstein.pdf",
        },
    },
    {
        "autor": {
            "nombre": "Herman Melville",
            "pais": "Estados Unidos",
            "fecha_nacimiento": "1819-08-01",
        },
        "libro": {
            "titulo": "Moby-Dick",
            "genero": "Adventure",
            "idioma": "English",
            "numero_paginas": 635,
            "editorial": "Harper & Brothers (1851)",
            "descripcion": (
                "Moby Dick follows the voyage of the whaling ship Pequod, commanded by Captain Ahab, "
                "who seeks revenge on the white sperm whale Moby Dick. The novel is an epic exploration "
                "of obsession, fate, and humanity's relationship with nature."
            ),
            "portada_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/36/Moby-Dick_FE_title_page.jpg/800px-Moby-Dick_FE_title_page.jpg",
            "pdf_source_url": "https://www.planetebook.com/free-ebooks/moby-dick.pdf",
        },
    },
    {
        "autor": {
            "nombre": "Oscar Wilde",
            "pais": "Irlanda",
            "fecha_nacimiento": "1854-10-16",
        },
        "libro": {
            "titulo": "The Picture of Dorian Gray",
            "genero": "Philosophical Fiction",
            "idioma": "English",
            "numero_paginas": 254,
            "editorial": "Ward, Lock and Company (1890)",
            "descripcion": (
                "The Picture of Dorian Gray follows a young man named Dorian Gray, the subject of a "
                "painting by artist Basil Hallward. Dorian makes a Faustian wish that the portrait "
                "will age instead of him, while he remains eternally young."
            ),
            "portada_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7a/The_Picture_of_Dorian_Gray_%281891%29_by_Oscar_Wilde.jpg/800px-The_Picture_of_Dorian_Gray_%281891%29_by_Oscar_Wilde.jpg",
            "pdf_source_url": "https://www.planetebook.com/free-ebooks/the-picture-of-dorian-gray.pdf",
        },
    },
    {
        "autor": {
            "nombre": "Lewis Carroll",
            "pais": "Reino Unido",
            "fecha_nacimiento": "1832-01-27",
        },
        "libro": {
            "titulo": "Alice's Adventures in Wonderland",
            "genero": "Fantasy",
            "idioma": "English",
            "numero_paginas": 166,
            "editorial": "Macmillan (1865)",
            "descripcion": (
                "Alice's Adventures in Wonderland follows a young girl named Alice who falls through a "
                "rabbit hole into a fantasy world populated by peculiar, anthropomorphic creatures. "
                "The tale plays with logic, giving it strong nonsense and satirical elements."
            ),
            "portada_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a6/Alice_in_Wonderland_%281865%29.jpg/800px-Alice_in_Wonderland_%281865%29.jpg",
            "pdf_source_url": "https://www.planetebook.com/free-ebooks/alices-adventures-in-wonderland.pdf",
        },
    },
]


def run():
    created_count = 0
    skipped_count = 0

    for data in BOOKS_DATA:
        autor_data = data["autor"]
        libro_data = data["libro"]

        # Crear o recuperar el autor
        autor, _ = Autor.objects.get_or_create(
            nombre=autor_data["nombre"],
            defaults={
                "pais": autor_data["pais"],
                "fecha_nacimiento": autor_data["fecha_nacimiento"],
            },
        )

        # Verificar si el libro ya existe
        if Libro.objects.filter(titulo=libro_data["titulo"]).exists():
            print(f"  [SKIP] '{libro_data['titulo']}' ya existe.")
            skipped_count += 1
            continue

        Libro.objects.create(
            autor=autor,
            titulo=libro_data["titulo"],
            genero=libro_data.get("genero", ""),
            idioma=libro_data.get("idioma", "English"),
            numero_paginas=libro_data.get("numero_paginas"),
            editorial=libro_data.get("editorial", ""),
            descripcion=libro_data.get("descripcion", ""),
            portada_url=libro_data.get("portada_url", ""),
            pdf_source_url=libro_data.get("pdf_source_url", ""),
            disponible=True,
        )
        print(f"  [OK]   '{libro_data['titulo']}' creado. PDF pendiente de descargar.")
        created_count += 1

    print(f"\n✅ Seed completo: {created_count} creados, {skipped_count} omitidos.")
    print(
        "\n💡 Para descargar los PDFs, usa el endpoint admin:")
    print("   POST /api/libros/<id>/download-pdf/  { 'url': '<pdf_source_url>' }")


if __name__ == "__main__":
    run()
