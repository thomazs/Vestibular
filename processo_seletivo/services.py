import base64
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
    valor = str(valor)[::-1]
    chave = '%f%f' % (valor, settings.SECRET_KEY)
    base = 100
    mod = sum([ord(i) for i in chave]) % base
    return base64.urlsafe_b64encode(f'{chave}{mod}')


def tag_segura_valida(chave):
    valores = base64.urlsafe_b64decode(chave)
    valores = valores.replace(settings.SECRET_KEY, settings.SECRET_KEY + '|||').split('|||')
    if len(valores) != 2:
        return False, None
    chave = valores[0]
    base = 100
    mod = sum([ord(i) for i in chave]) % base

    if mod != int(valores[1]):
        return False, None

    return chave.replace(settings.SECRET_KEY, '')[::-1]


def gera_cod_validacao():
    p1 = ''.join([str(random.randint(0, 9)) for i in range(5)])
    return p1


def envia_email_cadastro(pessoa):
    assunto = 'Vestibular U:verse - Cadastro Realizado'
    destinatarios = [pessoa.email]
    template = 'email.html'
    contexto = {'pessoa': pessoa, 'token': cria_tag_segura(pessoa.id)}
    enviar_email(assunto, destinatarios, template, contexto=contexto)


def envia_email_emailvalido(pessoa):
    assunto = 'Vestibular U:verse - Email validado'
    destinatarios = [pessoa.email]
    template = 'email.html'
    contexto = {'pessoa': pessoa, 'token': cria_tag_segura(pessoa.id)}
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
    contexto = {'pessoa': pessoa, 'senha': senha}
    enviar_email(assunto, destinatarios, template, contexto=contexto)


def loga_pessoa(request, pessoa, senha):
    user = authenticate(username=pessoa.email, password=senha)
    if user and user.is_active:
        login(request, user=user)
        return True
    return False
