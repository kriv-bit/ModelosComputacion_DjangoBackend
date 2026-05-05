from django.db import migrations

LOGROS = [
    # Sesiones
    {
        "nombre": "Primeros Pasos",
        "descripcion": "Completa tu primera sesión de lectura",
        "icono": "🏁",
        "categoria": "sesiones",
        "tipo_requisito": "sesiones",
        "requisito_valor": 1,
        "orden": 1,
    },
    {
        "nombre": "Aprendiz",
        "descripcion": "Completa 10 sesiones de lectura",
        "icono": "📖",
        "categoria": "sesiones",
        "tipo_requisito": "sesiones",
        "requisito_valor": 10,
        "orden": 2,
    },
    {
        "nombre": "Lector",
        "descripcion": "Completa 50 sesiones de lectura",
        "icono": "📚",
        "categoria": "sesiones",
        "tipo_requisito": "sesiones",
        "requisito_valor": 50,
        "orden": 3,
    },
    # Páginas
    {
        "nombre": "Curioso",
        "descripcion": "Lee 100 páginas en total",
        "icono": "📃",
        "categoria": "paginas",
        "tipo_requisito": "paginas",
        "requisito_valor": 100,
        "orden": 4,
    },
    {
        "nombre": "Devora Libros",
        "descripcion": "Lee 500 páginas en total",
        "icono": "📕",
        "categoria": "paginas",
        "tipo_requisito": "paginas",
        "requisito_valor": 500,
        "orden": 5,
    },
    {
        "nombre": "Ratón de Biblioteca",
        "descripcion": "Lee 1,000 páginas en total",
        "icono": "📚",
        "categoria": "paginas",
        "tipo_requisito": "paginas",
        "requisito_valor": 1000,
        "orden": 6,
    },
    # Tiempo
    {
        "nombre": "Diez Minutos",
        "descripcion": "Acumula 10 minutos de lectura",
        "icono": "⏱️",
        "categoria": "tiempo",
        "tipo_requisito": "tiempo_minutos",
        "requisito_valor": 10,
        "orden": 7,
    },
    {
        "nombre": "Una Hora",
        "descripcion": "Acumula 1 hora de lectura",
        "icono": "⏰",
        "categoria": "tiempo",
        "tipo_requisito": "tiempo_minutos",
        "requisito_valor": 60,
        "orden": 8,
    },
    {
        "nombre": "Maratón",
        "descripcion": "Acumula 10 horas de lectura",
        "icono": "🎯",
        "categoria": "tiempo",
        "tipo_requisito": "tiempo_minutos",
        "requisito_valor": 600,
        "orden": 9,
    },
    # Velocidad
    {
        "nombre": "Velocista",
        "descripcion": "Alcanza 300 PPM en una sesión",
        "icono": "🏃",
        "categoria": "velocidad",
        "tipo_requisito": "ppm",
        "requisito_valor": 300,
        "orden": 10,
    },
    {
        "nombre": "Flash",
        "descripcion": "Alcanza 500 PPM en una sesión",
        "icono": "⚡",
        "categoria": "velocidad",
        "tipo_requisito": "ppm",
        "requisito_valor": 500,
        "orden": 11,
    },
    {
        "nombre": "Rayo",
        "descripcion": "Alcanza 800 PPM en una sesión",
        "icono": "🚀",
        "categoria": "velocidad",
        "tipo_requisito": "ppm",
        "requisito_valor": 800,
        "orden": 12,
    },
    # Rachas
    {
        "nombre": "Constante",
        "descripcion": "Lee 3 días consecutivos",
        "icono": "📅",
        "categoria": "racha",
        "tipo_requisito": "racha_dias",
        "requisito_valor": 3,
        "orden": 13,
    },
    {
        "nombre": "Racha de 7 Días",
        "descripcion": "Lee 7 días consecutivos",
        "icono": "🔥",
        "categoria": "racha",
        "tipo_requisito": "racha_dias",
        "requisito_valor": 7,
        "orden": 14,
    },
    {
        "nombre": "Racha de 15 Días",
        "descripcion": "Lee 15 días consecutivos",
        "icono": "🔥",
        "categoria": "racha",
        "tipo_requisito": "racha_dias",
        "requisito_valor": 15,
        "orden": 15,
    },
    {
        "nombre": "Racha de 30 Días",
        "descripcion": "Lee 30 días consecutivos",
        "icono": "💪",
        "categoria": "racha",
        "tipo_requisito": "racha_dias",
        "requisito_valor": 30,
        "orden": 16,
    },
    # Libros completados
    {
        "nombre": "Primer Libro",
        "descripcion": "Completa tu primer libro",
        "icono": "🎯",
        "categoria": "libros",
        "tipo_requisito": "libros_completados",
        "requisito_valor": 1,
        "orden": 17,
    },
    {
        "nombre": "Coleccionista",
        "descripcion": "Completa 3 libros",
        "icono": "🏆",
        "categoria": "libros",
        "tipo_requisito": "libros_completados",
        "requisito_valor": 3,
        "orden": 18,
    },
    {
        "nombre": "Bibliófilo",
        "descripcion": "Completa 10 libros",
        "icono": "📚",
        "categoria": "libros",
        "tipo_requisito": "libros_completados",
        "requisito_valor": 10,
        "orden": 19,
    },
    # Calificaciones
    {
        "nombre": "Crítico",
        "descripcion": "Califica 3 libros",
        "icono": "⭐",
        "categoria": "especial",
        "tipo_requisito": "calificaciones",
        "requisito_valor": 3,
        "orden": 20,
    },
]


def seed_logros(apps, schema_editor):
    Logro = apps.get_model("gamificacion", "Logro")
    for data in LOGROS:
        Logro.objects.get_or_create(
            nombre=data["nombre"],
            defaults=data,
        )


def reverse_seed(apps, schema_editor):
    Logro = apps.get_model("gamificacion", "Logro")
    Logro.objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ("gamificacion", "0001_initial"),
    ]
    operations = [
        migrations.RunPython(seed_logros, reverse_seed),
    ]
