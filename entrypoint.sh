#!/bin/sh

# Esperar a que la base de datos esté lista (opcional si usamos depends_on en docker-compose, pero buena práctica)
echo "Esperando a la base de datos..."
# Puedes usar un script para esperar a la base de datos, o confiar en depends_on.
# Por simplicidad, confiamos en docker-compose condition: service_healthy

echo "Aplicando migraciones..."
python manage.py migrate --noinput

echo "Corriendo seed de datos inicial (si no existen)..."
python manage.py seed_data

echo "Corriendo seed de libros PDF (si no existen)..."
python scripts/seed_books_pdf.py

# Descargar PDFs si hay libros sin PDF que tengan pdf_source_url
# echo "Descargando PDFs..."
# python manage.py download_book_pdfs

echo "Iniciando servidor..."
exec "$@"
