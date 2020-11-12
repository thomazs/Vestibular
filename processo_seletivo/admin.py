from django.contrib import admin
from .models import Edicao
from .models import EdicaoCurso
from .models import Inscricao
from .models import Disciplina
from .models import QuestaoProva
from .models import RespostaQuestao
from .models import RespostaInscricao


class EdicaoCursoAdminTabular(admin.TabularInline):
    model = EdicaoCurso


class EdicaoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'dt_venc_boleto')
    inlines = [EdicaoCursoAdminTabular, ]


admin.site.register(Edicao, EdicaoAdmin)


class EdicaoCursoAdmin(admin.ModelAdmin):
    list_display = ('edicao', 'curso', 'qtd_vagas')


admin.site.register(EdicaoCurso, EdicaoCursoAdmin)


class RespostaInscricaoTabular(admin.TabularInline):
    model = RespostaInscricao
    min_num = 0
    extra = 0


class InscricaoAdmin(admin.ModelAdmin):
    list_display = ('pessoa', 'edicao', 'curso', 'situacao')
    search_fields = ('pessoa__nome',)
    list_filter = ('curso', 'situacao', 'tipo_selecao')
    inlines = (RespostaInscricaoTabular,)


admin.site.register(Inscricao, InscricaoAdmin)


class DisciplinaAdmin(admin.ModelAdmin):
    list_display = ('nome',)


admin.site.register(Disciplina, DisciplinaAdmin)


class RespostaQuestaoTabular(admin.TabularInline):
    model = RespostaQuestao


class QuestaoProvaAdmin(admin.ModelAdmin):
    list_display = ('edicao', 'disciplina', 'texto_curto')
    inlines = (RespostaQuestaoTabular,)


admin.site.register(QuestaoProva, QuestaoProvaAdmin)


class RespostaQuestaoAdmin(admin.ModelAdmin):
    list_display = ('questao', 'texto_curto', 'correta')


admin.site.register(RespostaQuestao, RespostaQuestaoAdmin)


class RespostaInscricaoAdmin(admin.ModelAdmin):
    list_display = ('inscricao', 'questao',)


admin.site.register(RespostaInscricao, RespostaInscricaoAdmin)
