# 📚 API REST de Libros - Django + Docker

![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white)
![Django REST](https://img.shields.io/badge/Django_REST-ff1709?style=for-the-badge&logo=django&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2CA5E0?style=for-the-badge&logo=docker&logoColor=white)
![Python](https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue)

**Una API REST moderna y escalable para gestión de libros, desarrollada con Django REST Framework y contenerizada con Docker.** Proyecto académico para la Universidad de Nariño.

---

## ✨ Características Principales

- 🚀 **API REST completa** con endpoints para CRUD de libros
- 🐳 **Contenerización completa** con Docker y Docker Compose
- 🗄️ **Base de datos PostgreSQL** optimizada para producción
- 📊 **Panel de administración Django** intuitivo y personalizable
- 🔧 **Configuración dual** SQLite (desarrollo local) / PostgreSQL (producción)
- 📦 **Migraciones automáticas** al iniciar el contenedor
- 🔐 **Variables de entorno** para configuración segura
- 📝 **Documentación API** integrada y detallada

---

## 🏫 Contexto Académico

| | |
|:---|:---|
| **Universidad** | Universidad de Nariño |
| **Facultad** | Facultad de Ingeniería |
| **Materia** | Modelos de Computación |
| **Semestre** | 2026-1 |
| **Profesor** | Por definir |

### 👥 Integrantes del Proyecto

| Nombre | Rol | Contacto |
|:---|:---|:---|
| **Kevin Orlando Rivera Lasso** | Backend Developer | [GitHub](https://github.com/tu-usuario) |
| **Daniel Alejandro Lasso Molina** | DevOps & Database | [GitHub](https://github.com/tu-usuario) |

---

## 🏗️ Arquitectura del Proyecto

```
📦 django-backend-libros
├── 📁 libros/                    # Aplicación Django principal
│   ├── 📁 migrations/           # Migraciones de base de datos
│   ├── 📄 models.py            # Modelo Libro (titulo, autor, ISBN, fecha)
│   ├── 📄 serializers.py       # Serializadores DRF
│   ├── 📄 views.py             # Vistas API (GET, POST)
│   ├── 📄 urls.py              # Rutas de la aplicación
│   ├── 📄 admin.py             # Configuración del panel admin
│   └── 📄 tests.py             # Pruebas unitarias
├── 📁 mi_proyecto/             # Configuración principal del proyecto
│   ├── 📄 settings.py          # Configuración Django (BD, apps, etc.)
│   ├── 📄 urls.py              # Rutas principales (admin, api)
│   └── 📄 wsgi.py              # Configuración WSGI para producción
├── 📄 Dockerfile               # Contenerización de la aplicación
├── 📄 docker-compose.yml       # Orquestación de servicios (Django + PostgreSQL)
├── 📄 requirements.txt         # Dependencias de Python
├── 📄 .env                     # Variables de entorno (seguras)
└── 📄 README.md               # Esta documentación
```

---

## 🚀 Inicio Rápido

### Opción 1: Docker Compose (Recomendada)

```bash
# 1. Clonar el repositorio
git clone https://github.com/tu-usuario/django-backend-libros.git
cd django-backend-libros

# 2. Construir y levantar los contenedores
docker-compose up --build

# 3. Acceder a la aplicación
# API:      http://localhost:8000/api/libros/
# Admin:    http://localhost:8000/admin/
```

### Opción 2: Desarrollo Local (sin Docker)

```bash
# 1. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar variables de entorno
cp .env.example .env  # Editar con tus valores

# 4. Aplicar migraciones
python manage.py migrate

# 5. Crear superusuario
python manage.py createsuperuser

# 6. Ejecutar servidor
python manage.py runserver
```

---

## 📡 Endpoints de la API

### 📖 Listar Libros
```http
GET /api/libros/
```
**Respuesta Exitosa (200 OK):**
```json
[
  {
    "id": 1,
    "titulo": "Cien años de soledad",
    "autor": "Gabriel García Márquez",
    "isbn": "9788437604947",
    "fecha_publicacion": "2026-04-14"
  }
]
```

### ➕ Crear Nuevo Libro
```http
POST /api/libros/
Content-Type: application/json
```
**Cuerpo de la Solicitud:**
```json
{
  "titulo": "El amor en los tiempos del cólera",
  "autor": "Gabriel García Márquez",
  "isbn": "9780307389732"
}
```
**Nota:** El campo `fecha_publicacion` se establece automáticamente a la fecha actual.

---

## ⚙️ Configuración de Base de Datos

El proyecto soporta dos motores de base de datos:

### 🐘 PostgreSQL (Producción/Docker)
```yaml
# Configuración automática en Docker
DB_ENGINE=postgresql
DB_NAME=mi_proyecto
DB_USER=django_app_user
DB_PASSWORD=passwordseguradjango
DB_HOST=db
DB_PORT=5432
```

### 🗃️ SQLite (Desarrollo Local)
```python
# Configuración por defecto
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

---

## 🛠️ Comandos Útiles

### 🔨 Desarrollo
```bash
# Aplicar migraciones
python manage.py migrate

# Crear migraciones después de cambios en modelos
python manage.py makemigrations libros

# Ejecutar pruebas
python manage.py test libros

# Crear superusuario para el admin
python manage.py createsuperuser
```

### 🐳 Docker
```bash
# Construir imágenes
docker-compose build

# Levantar servicios en segundo plano
docker-compose up -d

# Ver logs
docker-compose logs -f web

# Detener servicios
docker-compose down

# Eliminar volúmenes (cuidado: borra datos)
docker-compose down -v
```

---

## 🎨 Panel de Administración

Accede al panel de administración en:
```
http://localhost:8000/admin/
```

**Características del panel:**
- 👥 Gestión de usuarios y permisos
- 📚 CRUD completo de libros
- 🔍 Búsqueda y filtrado avanzado
- 📊 Interfaz responsive y moderna
- 🔐 Autenticación segura con Django

---

## 🌐 Despliegue en Producción

### Recomendaciones para Producción:
1. **Cambiar `DEBUG=False`** en `.env`
2. **Configurar `ALLOWED_HOSTS`** con tu dominio
3. **Usar PostgreSQL** en lugar de SQLite
4. **Configurar SSL/TLS** para tráfico seguro
5. **Implementar backup automático** de la base de datos
6. **Configurar logging** adecuado
7. **Usar Gunicorn/Uvicorn** como servidor ASGI/WSGI

### Ejemplo con Gunicorn:
```bash
gunicorn --workers 4 --bind 0.0.0.0:8000 mi_proyecto.wsgi:application
```

---

## 🤝 Contribuciones

Este proyecto es académico, pero si deseas contribuir:

1. 🍴 Haz un fork del proyecto
2. 🌿 Crea una rama para tu feature (`git checkout -b feature/awesome-feature`)
3. 💾 Realiza tus cambios y commitea (`git commit -m 'Add awesome feature'`)
4. 🚀 Push a la rama (`git push origin feature/awesome-feature`)
5. 🔄 Abre un Pull Request

---

## 📄 Licencia

Este proyecto fue desarrollado con fines académicos para la **Universidad de Nariño** en el marco de la asignatura **Modelos de Computación**.

**© 2026 - Kevin Orlando Rivera Lasso & Daniel Alejandro Lasso Molina**

---

## 🙏 Agradecimientos

- **Universidad de Nariño** por la formación académica
- **Docentes de Modelos de Computación** por la guía y conocimientos
- **Comunidad Django** por el excelente framework
- **Docker** por las herramientas de contenerización

---

<div align="center">

### 🚀 **¡Listo para empezar!**

[![Open in Docker](https://img.shields.io/badge/Desplegar_con_Docker-2CA5E0?style=for-the-badge&logo=docker&logoColor=white)](https://docs.docker.com/compose/)
[![Django Docs](https://img.shields.io/badge/Ver_Documentación_Django-092E20?style=for-the-badge&logo=django&logoColor=white)](https://docs.djangoproject.com/)

</div>