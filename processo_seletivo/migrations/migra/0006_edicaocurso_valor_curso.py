# Generated by Django 3.1.1 on 2020-11-17 16:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('processo_seletivo', '0005_respostainscricao_dt_respondeu'),
    ]

    operations = [
        migrations.AddField(
            model_name='edicaocurso',
            name='valor_curso',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=7, null=True, verbose_name='Valor do curso'),
        ),
    ]
