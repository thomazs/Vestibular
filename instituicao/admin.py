from django.contrib import admin

from instituicao.models import Curso


class CursoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'ativo_selecao', 'ativo_matricula')


admin.site.register(CursoAdmin, Curso)
