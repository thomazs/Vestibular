import string
import random
from datetime import date, datetime
from django.contrib.auth import get_user_model, authenticate, login
from django.core import mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

UserModel = get_user_model()


class EMensagemNaoIndicada(Exception):
    def __init__(self):
        self.message = 'Mensagem não indicada'


class EDestinatariosNaoIndicados(Exception):
    def __init__(self):
        self.message = 'Mensagem não indicada'


def enviar_email(assunto, destinatarios=[], template=None, mensagem='', contexto={}):
    if template:
        html_message = render_to_string(template, contexto)
    else:
        html_message = mensagem
    plain_message = strip_tags(html_message)

    if plain_message == '' and html_message == '':
        raise EMensagemNaoIndicada()

    if len(destinatarios) == 0:
        raise EDestinatariosNaoIndicados()

    from_email = 'Uverse <%s>' % settings.EMAIL_HOST_USER
    mail.send_mail(assunto, plain_message, from_email, destinatarios, html_message=html_message)


def cria_tag_segura(valor):
    valor = str(valor).rjust(10, '0')[::-1]
    for i in range(10):
        valor += random.choice(string.ascii_uppercase[:10])
    base = 10
    mod = str(sum([ord(i) for i in valor]) % base).rjust(2, '0')
    chave = f'{valor}{mod}'
    cadeia = chave[::-1]
    trans01 = string.ascii_uppercase[:10] + '0123456789'
    trans02 = '1234567890' + string.ascii_lowercase[:10]
    t = cadeia.maketrans(trans01, trans02)
    cadeia = cadeia.translate(t)
    return cadeia


def tag_segura_valida(chave):
    if len(chave) != 22:
        return False, None

    trans01 = string.ascii_uppercase[:10] + '0123456789'
    trans02 = '1234567890' + string.ascii_lowercase[:10]
    t = chave.maketrans(trans02, trans01)
    cadeia = chave.translate(t)[::-1]
    base = 10
    p1 = cadeia[:-2]
    p2 = cadeia[-2:]
    mod = str(sum([ord(i) for i in p1]) % base).rjust(2, '0')

    if p2 != mod:
        return False, None

    return True, p1[:10][::-1]


def gera_cod_validacao():
    p1 = ''.join([str(random.randint(0, 9)) for i in range(5)])
    return p1


def envia_email_cadastro(pessoa, token):
    assunto = 'Vestibular U:verse - Cadastro Realizado'
    destinatarios = [pessoa.email]
    template = 'email.html'
    contexto = {'pessoa': pessoa, 'token': token, 'host': settings.HOST_CURRENT}
    enviar_email(assunto, destinatarios, template, contexto=contexto)


def envia_email_emailvalido(pessoa):
    assunto = 'Vestibular U:verse - Email validado'
    destinatarios = [pessoa.email]
    template = 'email.html'
    contexto = {'pessoa': pessoa, 'token': cria_tag_segura(pessoa.id), 'host': settings.HOST_CURRENT}
    enviar_email(assunto, destinatarios, template, contexto=contexto)


def valida_email(pessoa):
    pessoa.email_valido = True
    pessoa.save()


def ativa_pessoa(pessoa, senha):
    user = UserModel(username=pessoa.email, is_active=True)
    user.set_password(senha)
    user.save()

    pessoa.ativo = True
    pessoa.data_ativacao = datetime.now()
    pessoa.usuario = user
    pessoa.save()

    return pessoa


def envia_email_cadastroconcluido(pessoa, senha):
    assunto = 'Vestibular U:verse - Email validado'
    destinatarios = [pessoa.email]
    template = 'email_cadastrocompleto.html'
    contexto = {'pessoa': pessoa, 'senha': senha, 'host': settings.HOST_CURRENT}
    enviar_email(assunto, destinatarios, template, contexto=contexto)


def loga_pessoa(request, pessoa, senha):
    user = authenticate(username=pessoa.email, password=senha)
    if user and user.is_active:
        login(request, user=user)
        return True
    return False
