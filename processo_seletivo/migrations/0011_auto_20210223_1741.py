# Generated by Django 3.1.1 on 2021-02-23 17:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('processo_seletivo', '0010_afiliado_visitas'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inscricao',
            name='afiliado',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Afiliado'),
        ),
    ]
