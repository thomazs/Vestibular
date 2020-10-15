from django.contrib import messages
from django.contrib.auth import logout
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy

from instituicao.models import Pessoa
from processo_seletivo.forms import LoginForm, FormCadastro, FormCompletaCadastro
from processo_seletivo.services import tag_segura_valida, cria_tag_segura, gera_cod_validacao, \
    envia_email_cadastro, valida_email, ativa_pessoa, loga_pessoa, envia_email_cadastroconcluido


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
    return render(request, 'painel.html', locals())


def cadastro(request):
    form = FormCadastro()
    if request.method == 'POST':
        print(request.POST)
        form = FormCadastro(request.POST)
        if form.is_valid():
            pessoa = form.save(commit=False)
            pessoa.codvalidacao = gera_cod_validacao()
            pessoa.save()
            envia_email_cadastro(pessoa)
            return redirect('emailenviado', token=cria_tag_segura(pessoa.id))

    return render(request, 'cadastro.html', locals())


def emailenviado(request, token=None):
    segura, valor = tag_segura_valida(request.GET.get('token', ''))
    if not segura:
        return redirect('index')

    pessoa = get_object_or_404(Pessoa, pk=valor)
    return render(request, 'mensagem_email.html', {'pessoa': pessoa})


def sair(request):
    logout(request)
    return redirect('index')


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
            return redirect(reverse_lazy('mensagem') + '?_next=' + reverse_lazy('concluir_cadastro', args=[token]))

    return redirect('mensagem')


def mensagem(request, time_to_redirect=0):
    next = request.GET.get('_next', '')
    return render(request, 'mensagem.html', {'next': next, 'time_to_redirect': time_to_redirect})


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

    form = FormCompletaCadastro(instance=Pessoa)
    if request.method == 'POST':
        form = FormCompletaCadastro(request.POST, instance=Pessoa)
        if form.is_valid():
            pessoa = form.save(commit=False)
            ativa_pessoa(pessoa, form.cleaned_data['senha'])
            loga_pessoa(pessoa, form.cleaned_data['senha'])
            envia_email_cadastroconcluido(pessoa, form.cleaned_data['senha'])
            return redirect('index')
    return render(request, 'completa_cadastro.html', locals())
