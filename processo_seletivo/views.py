from django.contrib.auth import logout
from django.shortcuts import render, redirect

from processo_seletivo.forms import LoginForm, FormCadastro


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
            pessoa = form.save()

            # todo Redirecionar a uma outra view
            return render(request, 'mensagem_email.html', locals())

    return render(request, 'cadastro.html', locals())


def sair(request):
    logout(request)
    return redirect('index')
