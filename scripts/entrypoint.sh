#!/bin/sh
# entrypoint.sh - Script de entrada para el contenedor web de Django
# Se ejecuta cada vez que el contenedor arranca

set -e  # Si algún comando falla, se detiene el script

echo "▶️  Ejecutando migraciones de Django..."
python manage.py migrate --noinput

echo "▶️  Recolectando archivos estáticos..."
python manage.py collectstatic --noinput --clear

echo "▶️  Iniciando Gunicorn..."
exec "$@"
