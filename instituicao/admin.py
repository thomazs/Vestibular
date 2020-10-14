from django.contrib import admin

from instituicao.models import Curso
from .models import Pessoa


class CursoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'ativo_selecao', 'ativo_matricula')


admin.site.register(Curso, CursoAdmin)


class PessoaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'fone', 'email')
    search_fields = ('nome',)


admin.site.register(Pessoa, PessoaAdmin)
