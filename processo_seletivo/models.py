from datetime import datetime
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.html import strip_tags
from instituicao.models import Curso, Pessoa
UserModel = get_user_model()

from tinymce.models import HTMLField




class Edicao(models.Model):
    class Meta:
        db_table = 'edicao'
        verbose_name = 'edição'
        verbose_name_plural = 'edições'

    def __str__(self):
        return self.nome

    nome = models.CharField('Edição', max_length=80)
    info = models.TextField('Informações', null=True, blank=True)
    dt_ini_insc = models.DateTimeField(null=True, blank=True)
    dt_fim_insc = models.DateTimeField()
    dt_venc_boleto = models.DateField()
    ano = models.IntegerField('Ano')
    edital = models.FileField('Edital', upload_to='editais')
    prova_liberada = models.BooleanField(default=False)
    pagamento_liberado = models.BooleanField(default=False)

    # instrucoes_redacao = HTMLField('Instruções para redação')
    instrucoes_redacao = HTMLField('Instruções para redação')


    @property
    def ativo(self):
        return self.dt_ini_insc <= datetime.now() <= self.dt_fim_insc


class EdicaoCurso(models.Model):
    class Meta:
        db_table = 'edicaocurso'
        verbose_name = 'curso/edição'
        verbose_name_plural = 'cursos/Edição'

    def __str__(self):
        return f'({self.edicao.nome}) {self.curso.nome} - Vagas: {self.qtd_vagas}'

    edicao = models.ForeignKey(Edicao, on_delete=models.RESTRICT)
    curso = models.ForeignKey(Curso, on_delete=models.RESTRICT)
    qtd_vagas = models.IntegerField('Qtd.Vagas')
    valor_curso = models.DecimalField('Valor do curso', null=True, blank=True, max_digits=7, decimal_places=2)

    @property
    def nome(self):
        return self.curso.nome

    def percentual_inscricoes(self):
        qtd_inscricoes = Inscricao.objects.filter(edicao=self.edicao, curso=self.curso).count()
        qtd_vagas = self.qtd_vagas
        return int(round(qtd_inscricoes * 100 // qtd_vagas, 0))


    def qtd_inscricoes(self):
        qtd_inscricoes = Inscricao.objects.filter(edicao=self.edicao, curso=self.curso).count()
        return qtd_inscricoes

    @property
    def matriculados(self):
        qtd_matriculados = Inscricao.objects.filter(situacao=31, curso=self.curso, edicao=self.edicao).count()
        return qtd_matriculados


TIPO_SELECAO = (
    (1, 'Processo Seletivo Comum (Prova)'),
    (2, 'Portador de Diploma (já possui outro curso de nível superior)'),
    (3, 'Utilizando nota do ENEM'),
)

SITUACAO_INSCRICAO = (
    (1, 'Inscrito'),
    (11, 'Reprovado (nota abaixo do mínimo)'),
    (12, 'Reprovado (zerou em alguma nota)'),
    (13, 'Reprovado (não comprovou enem ou doc. conclusão)'),
    (21, 'Aprovado'),
    (31, 'Matriculado'),
)

FICOUSABENDO_INSCRICAO = (
    (1, 'Google'),
    (2, 'Rede Amazônica'),
    (3, 'TV Gazeta'),
    (4, 'Facebook'),
    (5, 'Instagram'),
    (6, 'Via Verde Shopping'),
    (7, 'Outros'),
)

def comprovante_enem_upload_to(instance, filename):
    ext = filename.split('.')[-1]
    retorno = f'E{instance.edicao.pk}/comprovate_enem/P{instance.pessoa.pk}.{ext}'
    print('UPLOAD PARA: ', retorno)
    return ext


def comprovante_esc_upload_to(instance, filename):
    ext = filename.split('.')[-1]
    return f'E{instance.edicao.pk}/comprovate_escolaridade/P{instance.pessoa.pk}.{ext}'


class Inscricao(models.Model):
    class Meta:
        db_table = 'inscricao'
        verbose_name = 'inscrição'
        verbose_name_plural = 'inscrições'

    def __str__(self):
        return self.pessoa.nome

    edicao = models.ForeignKey(Edicao, on_delete=models.RESTRICT)
    pessoa = models.ForeignKey(Pessoa, on_delete=models.RESTRICT)
    tipo_selecao = models.IntegerField('Tipo de Ingresso', default=1, choices=TIPO_SELECAO)

    nota_enem = models.DecimalField('Nota do Enem', max_digits=15, decimal_places=3, null=True, blank=True)
    ano_enem = models.IntegerField('Ano do Enem', null=True, blank=True)
    comprovante_enem = models.FileField(null=True, blank=True, max_length=250, upload_to=comprovante_enem_upload_to)

    treineiro = models.BooleanField(default=False)

    comprovante_escolaridade = models.FileField(null=True, blank=True, max_length=250, upload_to=comprovante_esc_upload_to)

    nec_intlibras = models.BooleanField(default=False)
    nec_ledor = models.BooleanField(default=False)
    nec_transcritor = models.BooleanField(default=False)
    nec_localfacilacesso = models.BooleanField(default=False)
    nec_outros = models.BooleanField(default=False)
    nec_outros_desc = models.TextField('Outras Nec. Especiais', null=True, blank=True)

    nec_prova_presencial = models.BooleanField(default=False)
    dt_agendamento = models.DateTimeField(null=True, blank=True)
    conf_agendamento = models.BooleanField(default=False)
    dt_conf_agendamento = models.DateField(null=True, blank=True)
    quem_confirmou = models.ForeignKey(UserModel, on_delete=models.RESTRICT, null=True, blank=True,
                                       related_name='confagendamento_user_set')

    fez_prova = models.BooleanField(default=False)
    dt_ini_prova = models.DateTimeField(null=True, blank=True)
    dt_fim_prova = models.DateTimeField(null=True, blank=True)

    fez_redacao = models.BooleanField(default=False)
    dt_ini_redacao = models.DateTimeField(null=True, blank=True)
    dt_fim_redacao = models.DateTimeField(null=True, blank=True)

    nota_geral = models.DecimalField('Nota Geral', null=True, blank=True, max_digits=13, decimal_places=3)
    nota_redacao = models.DecimalField('Nota Redação', null=True, blank=True, max_digits=13, decimal_places=3)
    nota_redacao_p1 = models.DecimalField('Nota Redação', null=True, blank=True, max_digits=13, decimal_places=3)
    nota_redacao_p2 = models.DecimalField('Nota Redação', null=True, blank=True, max_digits=13, decimal_places=3)
    nota_redacao_p3 = models.DecimalField('Nota Redação', null=True, blank=True, max_digits=13, decimal_places=3)
    nota_redacao_p4 = models.DecimalField('Nota Redação', null=True, blank=True, max_digits=13, decimal_places=3)
    nota_redacao_p5 = models.DecimalField('Nota Redação', null=True, blank=True, max_digits=13, decimal_places=3)
    nota_prova = models.DecimalField('Nota Prova', null=True, blank=True, max_digits=13, decimal_places=3)
    redacao = models.TextField('Redação', null=True, blank=True)
    corretor_redacao = models.ForeignKey(UserModel, null=True, blank=True, on_delete=models.RESTRICT)

    curso = models.ForeignKey(Curso, related_name='cursoopcao_set', on_delete=models.RESTRICT)
    curso_final = models.ForeignKey(Curso, related_name='cursoselecionado_set', on_delete=models.RESTRICT)

    data_inclusao = models.DateTimeField(auto_now_add=True)
    data_alteracao = models.DateTimeField(auto_now=True)
    situacao = models.IntegerField(default=1, choices=SITUACAO_INSCRICAO)
    # afiliado = models.CharField('Afiliado', null=True, blank=True, max_length=100)
    publicidade = models.IntegerField('Como ficou sabendo do Vestibular', default=7, choices=FICOUSABENDO_INSCRICAO)

    def id_protegido(self):
        from processo_seletivo.services import cria_tag_segura
        return cria_tag_segura(str(self.id))
    # todo Adicionar opção de controle de pagamento


class Disciplina(models.Model):
    class Meta:
        db_table = 'disciplina'

    def __str__(self):
        return self.nome

    nome = models.CharField('Nome', max_length=100)


TIPO_QUESTAO = (
    (1, 'Objetiva'),
)


class QuestaoProva(models.Model):
    class Meta:
        db_table = 'questaoprova'
        verbose_name = 'questão da prova'
        verbose_name_plural = 'questões da prova'

    def __str__(self):
        return strip_tags(self.texto_curto)

    edicao = models.ForeignKey(Edicao, on_delete=models.RESTRICT)
    disciplina = models.ForeignKey(Disciplina, on_delete=models.RESTRICT)
    # texto = models.TextField('Texto Questão')
    texto = HTMLField('Textos Questãos')

    tipoquestao = models.IntegerField(default=1, choices=TIPO_QUESTAO)
    pontos = models.DecimalField(default='1', max_digits=10, decimal_places=1)

    @property
    def texto_curto(self):
        return strip_tags(self.texto)[:50]


class RespostaQuestao(models.Model):
    class Meta:
        db_table = 'respostaquestao'

    def __str__(self):
        return self.texto_curto

    questao = models.ForeignKey(QuestaoProva, on_delete=models.RESTRICT)
    texto = models.TextField('Texto Resposta')
    correta = models.BooleanField(default=False)

    @property
    def texto_curto(self):
        return strip_tags(self.texto)[:50]


class RespostaInscricao(models.Model):
    class Meta:
        db_table = 'respostainscricao'

    inscricao = models.ForeignKey(Inscricao, on_delete=models.RESTRICT)
    questao = models.ForeignKey(QuestaoProva, on_delete=models.RESTRICT)
    resposta = models.ForeignKey(RespostaQuestao, on_delete=models.RESTRICT, null=True, blank=True)
    ordem = models.IntegerField(default=1)
    dt_respondeu = models.DateTimeField(null=True, blank=True)

    @property
    def correta(self):
        return self.resposta.correta

    @property
    def tag(self):
        from processo_seletivo.services import cria_tag_segura
        return cria_tag_segura(self.id)

# class Afiliado(models.Model):
#     class Meta:
#         db_table = 'afiliados'
#         verbose_name = 'afiliado'
#         verbose_name_plural = 'afiliados'
#
#     def __str__(self):
#         return self.pessoa.nome
#
#     pessoa = models.ForeignKey(Pessoa, on_delete=models.RESTRICT)
#     codigo = models.CharField('Código de indicação', blank=True, null=True, unique=True, max_length=50)
#     visitas = models.IntegerField('Visitas', blank=True, null=True)
#
#     @property
#     def qtd_inscritos(self):
#         qtd_pessoas = Inscricao.objects.filter(afiliado=self.codigo).count()
#         return qtd_pessoas