# Generated by Django 3.1.2 on 2021-06-08 14:59

from django.db import migrations
import tinymce.models


class Migration(migrations.Migration):

    dependencies = [
        ('processo_seletivo', '0008_auto_20210608_1449'),
    ]

    operations = [
        migrations.AlterField(
            model_name='edicao',
            name='instrucoes_redacao',
            field=tinymce.models.HTMLField(verbose_name='Instruções para redação'),
        ),
    ]
