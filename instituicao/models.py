from django.contrib.auth import get_user_model
from django.db import models

UserModel = get_user_model()


class Curso(models.Model):
    class Meta:
        db_table = 'curso'

    nome = models.CharField('Nome', max_length=80)
    ativo_selecao = models.BooleanField('Ativo para Seleção', default=True)
    ativo_matricula = models.BooleanField('Ativo para Matrícula', default=True)

    def __str__(self):
        return self.nome

    def __unicode__(self):
        return self.nome


class Pessoa(models.Model):
    class Meta:
        db_table = 'pessoa'

    nome = models.CharField('Nome', max_length=80)
    fone = models.CharField('Telefone', max_length=20)
    email = models.EmailField('Email', max_length=200)
    rg = models.CharField('RG', max_length=20, null=True, blank=True)
    cpf = models.CharField('CPF', max_length=20, null=True, blank=True)
    ativo = models.BooleanField('Ativo', default=True)
    usuario = models.ForeignKey(UserModel, null=True, blank=True, on_delete=models.RESTRICT)
    email_valido = models.BooleanField(default=False)
    fone_valido = models.BooleanField(default=True)
    ativo = models.BooleanField(default=False)
    codvalidacao = models.CharField(max_length=80, null=True, blank=True)
    data_cadastro = models.DateTimeField(auto_now_add=True)
    data_alteracao = models.DateTimeField(auto_now=True)
    data_ativacao = models.DateTimeField(editable=False, null=True, blank=True)

    def __str__(self):
        return self.nome

    def __unicode__(self):
        return self.nome

    def primeiro_nome(self):
        return self.nome.split(' ')[0]
