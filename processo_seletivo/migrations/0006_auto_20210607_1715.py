# Generated by Django 3.1.2 on 2021-06-07 17:15

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import tinymce.models


class Migration(migrations.Migration):

    dependencies = [
        ('instituicao', '0004_auto_20210607_1715'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('processo_seletivo', '0005_respostainscricao_dt_respondeu'),
    ]

    operations = [
        migrations.AlterField(
            model_name='afiliado',
            name='pessoa',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='instituicao.pessoa'),
        ),
        migrations.AlterField(
            model_name='edicaocurso',
            name='curso',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='instituicao.curso'),
        ),
        migrations.AlterField(
            model_name='edicaocurso',
            name='edicao',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='processo_seletivo.edicao'),
        ),
        migrations.AlterField(
            model_name='inscricao',
            name='corretor_redacao',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='inscricao',
            name='curso',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='cursoopcao_set', to='instituicao.curso'),
        ),
        migrations.AlterField(
            model_name='inscricao',
            name='curso_final',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='cursoselecionado_set', to='instituicao.curso'),
        ),
        migrations.AlterField(
            model_name='inscricao',
            name='edicao',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='processo_seletivo.edicao'),
        ),
        migrations.AlterField(
            model_name='inscricao',
            name='pessoa',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='instituicao.pessoa'),
        ),
        migrations.AlterField(
            model_name='inscricao',
            name='quem_confirmou',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='confagendamento_user_set', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='questaoprova',
            name='disciplina',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='processo_seletivo.disciplina'),
        ),
        migrations.AlterField(
            model_name='questaoprova',
            name='edicao',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='processo_seletivo.edicao'),
        ),
        migrations.AlterField(
            model_name='questaoprova',
            name='texto',
            field=tinymce.models.HTMLField(verbose_name='Texto Questão'),
        ),
        migrations.AlterField(
            model_name='respostainscricao',
            name='inscricao',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='processo_seletivo.inscricao'),
        ),
        migrations.AlterField(
            model_name='respostainscricao',
            name='questao',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='processo_seletivo.questaoprova'),
        ),
        migrations.AlterField(
            model_name='respostainscricao',
            name='resposta',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='processo_seletivo.respostaquestao'),
        ),
        migrations.AlterField(
            model_name='respostaquestao',
            name='questao',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='processo_seletivo.questaoprova'),
        ),
    ]
