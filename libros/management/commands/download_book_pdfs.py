"""
Management command para descargar los PDFs de todos los libros
que tienen `pdf_source_url` configurada pero no tienen `pdf_file` aún.

Uso:
    ./venv/bin/python manage.py download_book_pdfs
    ./venv/bin/python manage.py download_book_pdfs --book-id 1
    ./venv/bin/python manage.py download_book_pdfs --force   # re-descarga aunque ya tenga PDF
"""

import os
import re
import uuid

import requests
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError

from libros.models import Libro


class Command(BaseCommand):
    help = "Descarga PDFs de libros desde sus pdf_source_url configuradas."

    def add_arguments(self, parser):
        parser.add_argument(
            "--book-id",
            type=int,
            default=None,
            help="ID del libro específico a descargar (por defecto: todos).",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            default=False,
            help="Forzar re-descarga aunque el libro ya tenga PDF.",
        )

    def handle(self, *args, **options):
        book_id = options["book_id"]
        force = options["force"]

        qs = Libro.objects.all()
        if book_id:
            qs = qs.filter(pk=book_id)

        if not force:
            qs = qs.filter(pdf_file="")  # solo los que no tienen PDF

        libros = qs.filter(pdf_source_url__isnull=False).exclude(pdf_source_url="")

        if not libros.exists():
            self.stdout.write(self.style.WARNING("No hay libros para descargar."))
            return

        self.stdout.write(f"📚 Descargando PDFs para {libros.count()} libro(s)...\n")

        for libro in libros:
            url = libro.pdf_source_url
            self.stdout.write(f"  → [{libro.id}] {libro.titulo}")
            self.stdout.write(f"       URL: {url}")

            try:
                response = requests.get(url, timeout=120, stream=True)
                response.raise_for_status()

                content_type = response.headers.get("Content-Type", "")
                if "pdf" not in content_type.lower() and not url.lower().endswith(".pdf"):
                    self.stdout.write(
                        self.style.ERROR(
                            f"       ✘ Content-Type inesperado: {content_type}"
                        )
                    )
                    continue

                safe_title = re.sub(r"[^a-zA-Z0-9_-]", "_", libro.titulo[:40])
                filename = f"{safe_title}_{uuid.uuid4().hex[:8]}.pdf"

                content = b"".join(response.iter_content(chunk_size=8192))

                if libro.pdf_file:
                    libro.pdf_file.delete(save=False)

                libro.pdf_file.save(filename, ContentFile(content), save=True)
                size_kb = len(content) // 1024
                self.stdout.write(
                    self.style.SUCCESS(
                        f"       ✔ Guardado: {filename} ({size_kb} KB)"
                    )
                )

            except requests.exceptions.Timeout:
                self.stdout.write(self.style.ERROR("       ✘ Timeout al descargar."))
            except requests.exceptions.RequestException as e:
                self.stdout.write(self.style.ERROR(f"       ✘ Error: {e}"))

        self.stdout.write(self.style.SUCCESS("\n✅ Descarga completada."))
