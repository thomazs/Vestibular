# Generated by Django 3.1.2 on 2020-10-15 11:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('instituicao', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='pessoa',
            name='dt_nasc',
            field=models.DateField(blank=True, null=True, verbose_name='Data Nascimento'),
        ),
    ]