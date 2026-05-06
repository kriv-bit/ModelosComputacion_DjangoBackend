from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('libros', '0002_libro_disponible_libro_idioma_libro_portada_url_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='libro',
            name='isbn',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
