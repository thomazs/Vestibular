# Generated by Django 3.1.2 on 2020-10-15 17:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('processo_seletivo', '0003_auto_20201015_1710'),
    ]

    operations = [
        migrations.AddField(
            model_name='respostainscricao',
            name='ordem',
            field=models.IntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='respostainscricao',
            name='resposta',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, to='processo_seletivo.respostaquestao'),
        ),
    ]
