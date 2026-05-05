# 📚 Documentación de la API - Lectura Rápida con Gamificación

## 📋 Índice
1. [Introducción](#1-introducción)
2. [Requisitos e Instalación](#2-requisitos-e-instalación)
3. [Estructura del Proyecto](#3-estructura-del-proyecto)
4. [Módulo: Cuentas (Autenticación y Perfil)](#4-módulo-cuentas)
5. [Módulo: Libros (Autores y Libros)](#5-módulo-libros)
6. [Módulo: Lectura (Sesiones y Progreso)](#6-módulo-lectura)
7. [Módulo: Gamificación (Logros)](#7-módulo-gamificación)
8. [Módulo: Metas (Objetivos de Lectura)](#8-módulo-metas)
9. [Módulo: Comprensión (Pruebas)](#9-módulo-comprensión)
10. [Tests](#10-tests)
11. [Base de Datos y Seed](#11-base-de-datos-y-seed)
12. [Manejo de Errores](#12-manejo-de-errores)

---

## 1. Introducción

API REST para una aplicación de **lectura rápida con gamificación**. Los usuarios pueden:
- Registrar sesiones de lectura y medir su velocidad (PPM)
- Seguir su progreso en cada libro
- Desbloquear logros e insignias
- Establecer metas diarias/semanales/mensuales
- Responder pruebas de comprensión lectora

**Stack técnico:**
- Django 6.0.4
- Django REST Framework 3.15.2
- SQLite (desarrollo) / PostgreSQL (Docker/producción)
- Autenticación por Token + Sesión

---

## 2. Requisitos e Instalación

### 2.1 Local (SQLite)
```bash
# Clonar
git clone https://github.com/LassRiver-NS-A2026EDW/ModelosComputacion_DjangoBackend.git
cd ModelosComputacion_DjangoBackend

# Entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Dependencias
pip install -r requirements.txt

# Migraciones y seed
python manage.py migrate
python manage.py dbshell < scripts/seed.sql

# Iniciar servidor
python manage.py runserver
```

### 2.2 Docker (PostgreSQL + pgvector)
```bash
docker-compose up --build
```

### 2.3 Usuarios de prueba (del seed)
| Usuario | Contraseña | Rol |
|---|---|---|
| `admin` | `Pass1234!` | Superusuario |
| `lector1` | `Pass1234!` | Usuario normal |
| `lector2` | `Pass1234!` | Usuario normal |

**Tokens de prueba:**
- admin: `aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa`
- lector1: `bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb`
- lector2: `cccccccccccccccccccccccccccccccccccccccc`

---

## 3. Estructura del Proyecto

```
ModelosComputacion_DjangoBackend/
├── mi_proyecto/           # Configuración del proyecto Django
│   ├── settings.py        # Configuración global (apps, DB, DRF)
│   ├── urls.py            # Rutas raíz del proyecto
│   └── wsgi.py            # WSGI para producción
├── cuentas/               # Módulo de autenticación y perfiles
├── libros/                # Módulo de autores y libros
├── lectura/               # Módulo de sesiones y progreso
├── gamificacion/          # Módulo de logros e insignias
├── metas/                 # Módulo de objetivos de lectura
├── comprension/           # Módulo de pruebas de comprensión
├── scripts/
│   └── seed.sql           # Datos de prueba para todos los modelos
├── docs/
│   └── README.md          # Este archivo
├── pyrightconfig.json     # Configuración de BasePyRight
├── requirements.txt       # Dependencias Python
└── docker-compose.yml     # Configuración Docker
```

### 3.1 Arquitectura de cada app

Cada app sigue la misma estructura:

```
app/
├── models.py          # Modelos de base de datos
├── serializers.py     # Serializers (validación y transformación de datos)
├── views.py           # Vistas (lógica de los endpoints)
├── urls.py            # Rutas específicas de la app
├── tests.py           # Tests unitarios y de integración
├── admin.py           # Configuración del panel admin
├── services.py        # Lógica de negocio (opcional)
└── migrations/        # Migraciones de base de datos
```

---

## 4. Módulo: Cuentas

### 4.1 Modelo: `PerfilUsuario`

```python
class PerfilUsuario(models.Model):
    user          = OneToOneField(User, related_name='perfil')
    fecha_nacimiento = DateField()
    genero        = CharField(choices=['M', 'F', 'O', 'N'])
    pais          = CharField(max_length=100)
    fecha_registro = DateTimeField(auto_now_add=True)
    # Propiedad calculada:
    edad          = int  # Se calcula automáticamente desde fecha_nacimiento
```

### 4.2 Endpoints

| Método | URL | Autenticación | Descripción |
|---|---|---|---|
| POST | `/api/auth/registro/` | ❌ No | Registrar nuevo usuario |
| POST | `/api/auth/login/` | ❌ No | Iniciar sesión |
| POST | `/api/auth/logout/` | ✅ Sí | Cerrar sesión |
| GET | `/api/auth/perfil/` | ✅ Sí | Ver mi perfil |
| PATCH | `/api/auth/perfil/` | ✅ Sí | Actualizar mi perfil |
| POST | `/api/auth/cambiar-password/` | ✅ Sí | Cambiar mi contraseña |

### 4.3 Ejemplos de uso

**Registro:**
```bash
curl -X POST http://localhost:8080/api/auth/registro/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "nuevo_lector",
    "email": "nuevo@email.com",
    "password": "MiPass123!",
    "password2": "MiPass123!",
    "fecha_nacimiento": "1995-06-15",
    "genero": "M",
    "pais": "México"
  }'
```

**Login (retorna token):**
```bash
curl -X POST http://localhost:8080/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "lector1", "password": "Pass1234!"}'
```

**Usar token en peticiones:**
```bash
curl http://localhost:8080/api/auth/perfil/ \
  -H "Authorization: Token bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
```

---

## 5. Módulo: Libros

### 5.1 Modelos

```python
class Autor(models.Model):
    nombre           = CharField(max_length=200)
    pais             = CharField(max_length=100)
    fecha_nacimiento = DateField()

class Libro(models.Model):
    titulo            = CharField(max_length=200)
    autor             = ForeignKey(Autor, related_name='libros')
    isbn              = CharField(blank=True, null=True)
    fecha_publicacion = DateField(auto_now_add=True)
    genero            = CharField(blank=True, null=True)
    numero_paginas    = PositiveIntegerField(blank=True, null=True)
    editorial         = CharField(blank=True, null=True)
    descripcion       = TextField(blank=True, null=True)
```

### 5.2 Endpoints

| Método | URL | Descripción |
|---|---|---|
| GET | `/api/autores/` | Listar autores |
| POST | `/api/autores/` | Crear autor |
| GET/PUT/DELETE | `/api/autores/<id>/` | CRUD de autor |
| GET | `/api/libros/` | Listar libros |
| POST | `/api/libros/` | Crear libro |
| GET/PUT/DELETE | `/api/libros/<id>/` | CRUD de libro |

---

## 6. Módulo: Lectura

### 6.1 Modelos

```python
class SesionLectura(models.Model):
    usuario            = ForeignKey(User, related_name='sesiones_lectura')
    libro              = ForeignKey(Libro, null=True, blank=True)
    fecha_inicio       = DateTimeField(auto_now_add=True)
    fecha_fin          = DateTimeField(null=True, blank=True)
    duracion_segundos  = PositiveIntegerField(null=True, blank=True)
    paginas_leidas     = PositiveIntegerField(null=True, blank=True)
    palabras_por_pagina = PositiveIntegerField(default=250)
    palabras_por_minuto = PositiveIntegerField(null=True, blank=True)
    activa             = BooleanField(default=True)
    notas              = TextField(blank=True)

    def finalizar(paginas_leidas):
        """Finaliza la sesión y calcula:
        - Duración en segundos
        - PPM (palabras por minuto)
        - Actualiza el progreso del libro asociado
        """

class ProgresoLibro(models.Model):
    usuario           = ForeignKey(User)
    libro             = ForeignKey(Libro)
    pagina_actual     = PositiveIntegerField(default=0)
    paginas_totales   = PositiveIntegerField(null=True, blank=True)
    completado        = BooleanField(default=False)
    fecha_inicio      = DateTimeField(auto_now_add=True)
    fecha_completado  = DateTimeField(null=True, blank=True)
    calificacion      = PositiveSmallIntegerField(null=True, blank=True)
    # Propiedad:
    progreso_porcentaje = float  # pagina_actual / paginas_totales * 100
```

### 6.2 Endpoints

| Método | URL | Descripción |
|---|---|---|
| POST | `/api/lectura/sesiones/` | Iniciar sesión de lectura |
| GET | `/api/lectura/sesiones/` | Listar sesiones (con filtros) |
| GET | `/api/lectura/sesiones/<id>/` | Detalle de sesión |
| PATCH | `/api/lectura/sesiones/<id>/` | Actualizar sesión |
| DELETE | `/api/lectura/sesiones/<id>/` | Eliminar sesión |
| POST | `/api/lectura/sesiones/<id>/finalizar/` | Finalizar sesión (calcula PPM) |
| POST | `/api/lectura/progreso/` | Crear progreso de libro |
| GET | `/api/lectura/progreso/` | Listar progresos |
| PATCH | `/api/lectura/progreso/<id>/` | Actualizar progreso |
| POST | `/api/lectura/progreso/<id>/completar/` | Marcar libro como completado |
| GET | `/api/lectura/estadisticas/` | Estadísticas de lectura |

### 6.3 Filtros disponibles

**Para sesiones:**
```
GET /api/lectura/sesiones/?libro=1&activa=false&desde=2026-05-01&hasta=2026-05-05
```

**Para progreso:**
```
GET /api/lectura/progreso/?libro=1&completado=false
```

### 6.4 Ejemplos

**Iniciar sesión:**
```bash
curl -X POST http://localhost:8080/api/lectura/sesiones/ \
  -H "Authorization: Token bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb" \
  -H "Content-Type: application/json" \
  -d '{"libro": 1}'
```

**Finalizar sesión (calcular PPM):**
```bash
curl -X POST http://localhost:8080/api/lectura/sesiones/1/finalizar/ \
  -H "Authorization: Token ..." \
  -H "Content-Type: application/json" \
  -d '{"paginas_leidas": 15}'
```

**Estadísticas:**
```json
GET /api/lectura/estadisticas/
{
  "total_sesiones": 8,
  "sesiones_activas": 0,
  "total_tiempo_minutos": 245.0,
  "total_paginas": 130,
  "ppm_promedio": 132,
  "ppm_maximo": 167,
  "racha_actual_dias": 4,
  "racha_maxima_dias": 4,
  "libros_completados": 0,
  "libros_en_lectura": 5,
  "sesiones_ultimos_7_dias": [...]
}
```

### 6.5 Cálculo de PPM

```
PPM = (paginas_leidas × palabras_por_pagina) / minutos
```

- `palabras_por_pagina` default: **250**
- El usuario puede personalizarlo al crear la sesión

---

## 7. Módulo: Gamificación

### 7.1 Modelos

```python
class Logro(models.Model):
    nombre           = CharField(max_length=200)
    descripcion      = TextField()
    icono            = CharField(default='🏆')
    categoria        = CharField(choices=['sesiones', 'paginas', 'tiempo', 'velocidad', 'racha', 'libros', 'especial'])
    tipo_requisito   = CharField(choices=['sesiones', 'paginas', 'tiempo_minutos', 'ppm', 'racha_dias', 'libros_completados', 'calificaciones'])
    requisito_valor  = PositiveIntegerField()
    orden            = PositiveIntegerField(default=0)
    activo           = BooleanField(default=True)

class LogroUsuario(models.Model):
    usuario          = ForeignKey(User)
    logro            = ForeignKey(Logro)
    fecha_desbloqueo = DateTimeField(auto_now_add=True)
    # Unique: (usuario, logro)
```

### 7.2 Endpoints

| Método | URL | Descripción |
|---|---|---|
| GET | `/api/gamificacion/logros/` | Catálogo completo de logros |
| GET | `/api/gamificacion/mis-logros/` | Mis logros desbloqueados |
| GET | `/api/gamificacion/progreso-logros/` | Progreso hacia cada logro |
| POST | `/api/gamificacion/verificar/` | Verificar y desbloquear nuevos logros |

### 7.3 Los 20 logros disponibles

| # | Icono | Nombre | Requisito |
|---|---|---|---|
| 1 | 🏁 | Primeros Pasos | 1 sesión |
| 2 | 📖 | Aprendiz | 10 sesiones |
| 3 | 📚 | Lector | 50 sesiones |
| 4 | 📃 | Curioso | 100 páginas |
| 5 | 📕 | Devora Libros | 500 páginas |
| 6 | 📚 | Ratón de Biblioteca | 1000 páginas |
| 7 | ⏱️ | Diez Minutos | 10 minutos |
| 8 | ⏰ | Una Hora | 60 minutos |
| 9 | 🎯 | Maratón | 600 minutos |
| 10 | 🏃 | Velocista | 300 PPM |
| 11 | ⚡ | Flash | 500 PPM |
| 12 | 🚀 | Rayo | 800 PPM |
| 13 | 📅 | Constante | 3 días racha |
| 14 | 🔥 | Racha de 7 Días | 7 días racha |
| 15 | 🔥 | Racha de 15 Días | 15 días racha |
| 16 | 💪 | Racha de 30 Días | 30 días racha |
| 17 | 🎯 | Primer Libro | 1 libro completado |
| 18 | 🏆 | Coleccionista | 3 libros completados |
| 19 | 📚 | Bibliófilo | 10 libros completados |
| 20 | ⭐ | Crítico | 3 libros calificados |

### 7.4 Progreso de logros

El endpoint `GET /api/gamificacion/progreso-logros/` retorna para cada logro:

```json
[
  {
    "logro_id": 1,
    "logro_nombre": "Primeros Pasos",
    "logro_icono": "🏁",
    "logro_descripcion": "Completa tu primera sesión de lectura",
    "logro_categoria": "sesiones",
    "valor_actual": 3,
    "requisito_valor": 1,
    "progreso_porcentaje": 100,
    "desbloqueado": true
  },
  ...
]
```

### 7.5 Verificación automática

El servicio `verificar_logros(usuario)` se encarga de:
1. Obtener las estadísticas actuales del usuario
2. Comparar cada logro contra las estadísticas
3. Desbloquear los que cumpla (creando `LogroUsuario`)
4. Retornar los nuevos logros desbloqueados

Se recomienda llamar a `POST /api/gamificacion/verificar/` después de:
- Finalizar una sesión de lectura
- Completar un libro
- Marcar una meta como cumplida

---

## 8. Módulo: Metas

### 8.1 Modelo

```python
class MetaLectura(models.Model):
    usuario          = ForeignKey(User)
    nombre           = CharField(max_length=200)
    tipo             = CharField(choices=['diaria', 'semanal', 'mensual'])
    tipo_objetivo    = CharField(choices=['paginas', 'minutos', 'sesiones'])
    objetivo_valor   = PositiveIntegerField()
    activa           = BooleanField(default=True)
```

### 8.2 Endpoints

| Método | URL | Descripción |
|---|---|---|
| POST | `/api/metas/` | Crear meta |
| GET | `/api/metas/` | Listar metas |
| GET | `/api/metas/<id>/` | Detalle de meta |
| PATCH | `/api/metas/<id>/` | Actualizar meta |
| DELETE | `/api/metas/<id>/` | Eliminar meta |
| GET | `/api/metas/progreso/` | Progreso de metas activas |

### 8.3 Cálculo de progreso

El progreso se calcula automáticamente según el período:

- **Diaria**: desde hoy a las 00:00 hasta ahora
- **Semanal**: desde el lunes a las 00:00 hasta ahora
- **Mensual**: desde el 1 del mes a las 00:00 hasta ahora

```json
GET /api/metas/progreso/
[
  {
    "meta_id": 1,
    "meta_nombre": "Leer 30 páginas al día",
    "meta_tipo": "diaria",
    "meta_tipo_objetivo": "paginas",
    "valor_actual": 25,
    "objetivo": 30,
    "progreso_porcentaje": 83,
    "cumplido": false
  }
]
```

---

## 9. Módulo: Comprensión

### 9.1 Modelos

```python
class PruebaComprension(models.Model):
    libro              = ForeignKey(Libro)
    titulo             = CharField(max_length=200)
    pregunta           = TextField()
    opcion_a           = CharField(max_length=500)
    opcion_b           = CharField(max_length=500)
    opcion_c           = CharField(blank=True)
    opcion_d           = CharField(blank=True)
    respuesta_correcta = CharField(choices=['A','B','C','D'])
    dificultad         = CharField(choices=['facil','media','dificil'])
    activa             = BooleanField(default=True)

class IntentoPrueba(models.Model):
    usuario          = ForeignKey(User)
    prueba           = ForeignKey(PruebaComprension)
    respuesta        = CharField(choices=['A','B','C','D'])
    correcta         = BooleanField(auto_verificada)
    fecha_intento    = DateTimeField(auto_now_add=True)
```

### 9.2 Endpoints

| Método | URL | Descripción |
|---|---|---|
| GET | `/api/comprension/libros/<id>/pruebas/` | Pruebas de un libro |
| GET | `/api/comprension/pruebas/<id>/` | Detalle de prueba |
| POST | `/api/comprension/pruebas/<id>/responder/` | Responder prueba |
| GET | `/api/comprension/intentos/` | Historial de intentos |
| GET | `/api/comprension/resultados/` | Resultados generales |

### 9.3 Importante: Seguridad

La **respuesta correcta NUNCA se expone** en el API. Al listar pruebas, el campo `respuesta_correcta` es excluido del serializador. La verificación ocurre internamente en el servidor:

```python
# En IntentoPrueba.save():
self.correcta = (self.respuesta == self.prueba.respuesta_correcta)
```

### 9.4 Ejemplo

**Responder una prueba:**
```bash
curl -X POST http://localhost:8080/api/comprension/pruebas/1/responder/ \
  -H "Authorization: Token ..." \
  -H "Content-Type: application/json" \
  -d '{"prueba": 1, "respuesta": "A"}'
```
Respuesta:
```json
{
  "id": 9,
  "prueba": 1,
  "respuesta": "A",
  "correcta": false,
  "prueba_pregunta": "¿Cómo se llamaba el fundador de Macondo?"
}
```

---

## 10. Tests

### 10.1 Ejecutar tests

```bash
# Todos los tests
python manage.py test

# Tests de un módulo específico
python manage.py test cuentas
python manage.py test lectura
python manage.py test gamificacion
python manage.py test metas
python manage.py test comprension

# Tests con verbosidad
python manage.py test --verbosity=2
```

### 10.2 Cobertura de tests

| Módulo | Tests | Cobertura |
|---|---|---|
| `cuentas` | 20 | Registro, login, perfil, cambio password, logout, modelo |
| `lectura` | 29 | Sesiones, progreso, estadísticas, rachas, finalizar, filtros |
| `gamificacion` | 13 | Logros, verificación, progreso, servicios, modelo |
| `metas` | 13 | CRUD, progreso páginas/minutos/sesiones, período, endpoint |
| `comprension` | 17 | Pruebas, responder, historial, resultados, auto-verificación, modelo |
| **Total** | **92** | Todos los módulos |

### 10.3 Estructura de tests

Cada archivo `tests.py` sigue esta estructura:

```python
class APITests(TestCase):
    """Tests de los endpoints."""
    def setUp(self):
        self.client = APIClient()
        self.client.force_login(self.user)

    def test_algo_funciona(self):
        url = reverse('nombre-url')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class ServiceTests(TestCase):
    """Tests de servicios/lógica de negocio."""

class ModelTests(TestCase):
    """Tests de modelos (str, métodos, validaciones)."""
```

### 10.4 Buenas prácticas en los tests

- Cada test verifica **una sola cosa** (atomicidad)
- Usar `setUpTestData` para datos compartidos (más rápido)
- Usar `setUp` para datos que cambian por test
- Probar casos: ✅ éxito, ❌ error, 🔒 autenticación
- Usar `reverse('nombre-url')` en vez de URLs hardcodeadas
- No usar datos externos (todo se genera en el test)

---

## 11. Base de Datos y Seed

### 11.1 Cargar datos de prueba

```bash
python manage.py migrate
python manage.py dbshell < scripts/seed.sql
```

### 11.2 Datos incluidos

| Tabla | Registros |
|---|---|
| `auth_user` | 3 usuarios (admin, lector1, lector2) |
| `authtoken_token` | 3 tokens |
| `cuentas_perfilusuario` | 3 perfiles |
| `libros_autor` | 5 autores |
| `libros_libro` | 5 libros |
| `lectura_sesionlectura` | 8 sesiones |
| `lectura_progresolibro` | 5 progresos |
| `metas_metalectura` | 5 metas |
| `comprension_pruebacomprension` | 8 pruebas |
| `comprension_intentoprueba` | 8 intentos |
| `gamificacion_logrousuario` | 3 logros |
| `gamificacion_logro` | 20 (creados por migración) |

### 11.3 Diagrama de relaciones

```
User (Django auth)
├── PerfilUsuario (1:1)
├── SesionLectura (1:N)
│   └── Libro (N:1)
├── ProgresoLibro (1:N)
│   └── Libro (N:1)
├── LogroUsuario (N:N)
│   └── Logro
├── MetaLectura (1:N)
└── IntentoPrueba (1:N)
    └── PruebaComprension (N:1)
        └── Libro (N:1)

Libro ─── Autor (N:1)
```

---

## 12. Manejo de Errores

### 12.1 Códigos de error comunes

| Código | Significado |
|---|---|
| `400 Bad Request` | Datos inválidos (validación falló) |
| `401 Unauthorized` | Token inválido o no provisto |
| `403 Forbidden` | No autenticado |
| `404 Not Found` | Recurso no existe |
| `500 Internal Server Error` | Error del servidor |

### 12.2 Formato de errores

**Error de validación:**
```json
{
  "campo": ["Este campo es requerido."],
  "password2": ["Las contraseñas no coinciden."]
}
```

**Error de autenticación:**
```json
{
  "error": "Credenciales inválidas."
}
```

**Error de recurso no encontrado:**
```json
{
  "error": "Sesión no encontrada."
}
```

---

## Apéndice A: Configuración de BasePyRight

El archivo `pyrightconfig.json` silencia falsos positivos del ORM de Django. Si agregas tipos personalizados y quieres más rigor, puedes eliminar estas líneas:

```json
{
  "reportAttributeAccessIssue": false,
  "reportUnknownMemberType": false,
  "reportGeneralTypeIssues": false
}
```

---

## Apéndice B: Docker

Para entornos productivos, el proyecto incluye:

```bash
docker-compose up --build
```

Esto levanta:
- **PostgreSQL 15** con `pgvector` (para búsquedas semánticas futuras)
- **Nginx** sirviendo archivos estáticos y media
- **Gunicorn** con la app Django

Variables de entorno requeridas (`.env`):
```
SECRET_KEY=...
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1
POSTGRES_DB=lecturapp
POSTGRES_USER=postgres
POSTGRES_PASSWORD=...
APP_DB_USER=app_user
APP_DB_PASSWORD=...
```

---

*Documentación generada para el proyecto ModelosComputacion_DjangoBackend*
