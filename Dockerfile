# Usa Python 3.12 sobre Alpine (imagen ligera)
FROM python:3.12-alpine

# Variables de entorno de Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Directorio de trabajo
WORKDIR /app

# Copia e instala dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el proyecto
COPY . .

# Expone el puerto 8000 (interno para Gunicorn, Nginx se conectará aquí)
EXPOSE 8000

# Dar permisos de ejecución al entrypoint
RUN chmod +x /app/entrypoint.sh

# Punto de entrada para ejecutar migraciones/seeds y luego el CMD
ENTRYPOINT ["/app/entrypoint.sh"]

# Arranque del servidor WSGI
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "mi_proyecto.wsgi:application"]
