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

# Da permisos de ejecución al entrypoint y fuerza saltos de linea Unix (LF)
# (Soluciona el error 'no such file or directory' en contenedores Linux
#  cuando los archivos se editan en Windows con CRLF)
RUN chmod +x /app/scripts/entrypoint.sh && \
    sed -i 's/\r$//' /app/scripts/entrypoint.sh /app/scripts/init.sh

# Entrypoint: migraciones automáticas + collectstatic
ENTRYPOINT ["/app/scripts/entrypoint.sh"]

# Comando por defecto
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "mi_proyecto.wsgi:application"]
