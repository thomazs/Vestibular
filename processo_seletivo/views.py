from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy

from instituicao.models import Pessoa
from processo_seletivo.forms import LoginForm, FormCadastro, FormCompletaCadastro, FormInscricao
from processo_seletivo.models import Inscricao
from processo_seletivo.services import tag_segura_valida, cria_tag_segura, gera_cod_validacao, \
    envia_email_cadastro, valida_email, ativa_pessoa, loga_pessoa, envia_email_cadastroconcluido, pega_edicao_ativa, \
    envia_email_inscricaofeita, cria_perguntas_inscricao


def index(request):
    if request.user.is_authenticated:
        return redirect('painel')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        form.request = request

        # todo Verificar se o email informado é de algum cadastro iniciado e pedir pra verificar email
        if form.is_valid():
            return redirect('painel')

    else:
        form = LoginForm()

    return render(request, 'index.html', locals())


def painel(request):
    if not request.user.is_authenticated:
        return redirect('index')
    edicao = pega_edicao_ativa()
    return render(request, 'painel.html', locals())


@transaction.atomic
def cadastro(request):
    form = FormCadastro()
    if request.method == 'POST':
        print(request.POST)
        form = FormCadastro(request.POST)
        if form.is_valid():
            pessoa = form.save(commit=False)
            pessoa.codvalidacao = gera_cod_validacao()
            pessoa.save()
            token = cria_tag_segura(pessoa.id)
            envia_email_cadastro(pessoa, token)
            return redirect('emailenviado', token=token)

    return render(request, 'cadastro.html', locals())


def emailenviado(request, token=None):
    segura, valor = tag_segura_valida(token)
    if not segura:
        return redirect('index')

    pessoa = get_object_or_404(Pessoa, pk=valor)
    return render(request, 'mensagem_email.html', {'pessoa': pessoa})


def sair(request):
    logout(request)
    return redirect('index')


@transaction.atomic
def validar_email(request, token=''):
    if token == '':
        return redirect('index')

    segura, valor = tag_segura_valida(token)
    if not segura:
        return redirect('index')

    pessoa = Pessoa.objects.filter(id=valor)
    if not pessoa.exists():
        messages.warning(request, 'Cadastro não localizado')

    else:
        pessoa = pessoa.first()
        if pessoa.email_valido:
            messages.warning(request, 'Email já foi validado! Tente fazer o login!')

        else:
            messages.success(request, 'Ativação do email realizada com sucesso!')
            valida_email(pessoa)
            return redirect(
                str(reverse_lazy('mensagem')) + '?_next=' + str(reverse_lazy('concluir_cadastro', args=[token])))

    return redirect('mensagem')


def mensagem(request, time_to_redirect=0):
    next = request.GET.get('_next', '')
    return render(request, 'mensagem.html', {'next': next, 'time_to_redirect': time_to_redirect})


@transaction.atomic
def concluir_cadastro(request, token):
    segura, valor = tag_segura_valida(token)
    if not segura:
        return redirect('index')

    pessoa = Pessoa.objects.filter(id=valor)
    if not pessoa.exists():
        messages.warning(request, 'Cadastro não localizado')
        return redirect('mensagem')

    pessoa = pessoa.first()
    if not pessoa.email_valido:
        messages.warning(request, 'Email ainda não foi validado! Tente fazer o login!')
        return redirect('mensagem')

    form = FormCompletaCadastro(instance=pessoa)
    if request.method == 'POST':
        form = FormCompletaCadastro(request.POST, instance=pessoa)
        if form.is_valid():
            pessoa = form.save()
            ativa_pessoa(pessoa, form.cleaned_data['senha'])
            loga_pessoa(request, pessoa, form.cleaned_data['senha'])
            envia_email_cadastroconcluido(pessoa, form.cleaned_data['senha'])
            return redirect('faz_inscricao')
    return render(request, 'completa_cadastro.html', locals())


@login_required(login_url=reverse_lazy('index'))
@transaction.atomic()
def faz_inscricao(request, id=None):
    pessoa = request.user.get_pessoa()
    inscricao = get_object_or_404(Inscricao, id=id) if id else None
    if inscricao and inscricao.pessoa_id != pessoa:
        messages.error(request, 'Inscrição não pertence a este candidato!')
        return redirect('painel')
    edicao = pega_edicao_ativa()
    form = FormInscricao(instance=inscricao, edicao=edicao)
    if request.method == 'POST':
        form = FormInscricao(request.POST, instance=inscricao, edicao=edicao)
        if form.is_valid():
            pinscricao = form.save(commit=False)
            pinscricao.curso_final = pinscricao.curso
            pinscricao.edicao = edicao
            pinscricao.pessoa = pessoa
            pinscricao.save()
            cria_perguntas_inscricao(pinscricao)
            envia_email_inscricaofeita(pessoa, pinscricao)
            messages.success(request, 'Inscrição efetuada com sucesso!')
            return redirect('painel')

    return render(request, 'inscricao.html', locals())


def prova_online(request):
    return render(request, 'prova_online.html', locals())
