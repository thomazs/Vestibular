from django.contrib.auth import get_user_model
from django.db import models

from instituicao.models import Curso, Pessoa

UserModel = get_user_model()


class Edicao(models.Model):
    class Meta:
        db_table = 'edicao'

    nome = models.CharField('Edição', max_length=80)
    info = models.TextField('Informações', null=True, blank=True)
    dt_ini_insc = models.DateTimeField(null=True, blank=True)
    dt_fim_insc = models.DateTimeField()
    dt_venc_boleto = models.DateField()
    ano = models.IntegerField('Ano')
    edital = models.FileField('Edital', upload_to='editais')


class EdicaoCurso(models.Model):
    class Meta:
        db_table = 'edicaocurso'

    def __str__(self):
        return f'({self.edicao.nome}) {self.curso.nome} - Vagas: {self.qtd_vagas}'

    edicao = models.ForeignKey(Edicao, on_delete=models.RESTRICT)
    curso = models.ForeignKey(Curso, on_delete=models.RESTRICT)
    qtd_vagas = models.IntegerField('Qtd.Vagas')


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


def comprovante_enem_upload_to(instance, filename):
    ext = filename.split('.')[-1]
    return f'/E{instance.edicao.pk}/comprovate_enem/P{instance.pessoa.pk}.{ext}'


def comprovante_esc_upload_to(instance, filename):
    ext = filename.split('.')[-1]
    return f'/E{instance.edicao.pk}/comprovate_escolaridade/P{instance.pessoa.pk}.{ext}'


class Inscricao(models.Model):
    class Meta:
        db_table = 'inscricao'

    def __str__(self):
        return self.pessoa.nome

    edicao = models.ForeignKey(Edicao, on_delete=models.RESTRICT)
    pessoa = models.ForeignKey(Pessoa, on_delete=models.RESTRICT)
    tipo_selecao = models.IntegerField('Tipo de Ingresso', default=1, choices=TIPO_SELECAO)

    nota_enem = models.DecimalField('Nota do Enem', max_digits=15, decimal_places=3, null=True, blank=True)
    ano_enem = models.IntegerField('Ano do Enem', null=True, blank=True)
    comprovante_enem = models.FileField(null=True, blank=True, max_length=250, upload_to=comprovante_enem_upload_to)

    # todo Validar se TIPO_SELECAO=3. Se for, não permitir.
    treineiro = models.BooleanField(default=False)

    # todo Utilizar o campo de comprovante_escolaridade apenas se TIPO_SELECAO=2
    comprovante_escolaridade = models.FileField(null=True, blank=True, max_length=250,
                                                upload_to=comprovante_esc_upload_to)

    nec_intlibras = models.BooleanField(default=False)
    nec_ledor = models.BooleanField(default=False)
    nec_transcritor = models.BooleanField(default=False)
    nec_localfacilacesso = models.BooleanField(default=False)
    nec_outros = models.BooleanField(default=False)
    nec_outros_desc = models.TextField('Outras Nec. Especiais', null=True, blank=True)

    nec_prova_presencial = models.BooleanField(default=False)
    dt_agendamento = models.DateTimeField(null=True, blank=True)
    conf_agendamento = models.BooleanField(default=False)

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

    def __str__(self):
        return self.texto

    edicao = models.ForeignKey(Edicao, on_delete=models.RESTRICT)
    disciplina = models.ForeignKey(Disciplina, on_delete=models.RESTRICT)
    texto = models.TextField('Texto Questão')
    tipoquestao = models.IntegerField(default=1, choices=TIPO_QUESTAO)
    pontos = models.DecimalField(default='1', max_digits=10, decimal_places=1)


class RespostaQuestao(models.Model):
    class Meta:
        db_table = 'respostaquestao'

    def __str__(self):
        return self.texto

    questao = models.ForeignKey(QuestaoProva, on_delete=models.RESTRICT)
    texto = models.TextField('Texto Resposta')
    correta = models.BooleanField(default=False)


class RespostaInscricao(models.Model):
    class Meta:
        db_table = 'respostainscricao'

    inscricao = models.ForeignKey(Inscricao, on_delete=models.RESTRICT)
    questao = models.ForeignKey(QuestaoProva, on_delete=models.RESTRICT)
    resposta = models.ForeignKey(RespostaQuestao, on_delete=models.RESTRICT)
