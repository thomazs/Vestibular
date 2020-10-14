from django.contrib.auth import logout
from django.shortcuts import render, redirect

from processo_seletivo.forms import LoginForm


def index(request):
    if request.user.is_authenticated:
        return redirect('painel')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        form.request = request
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
    return render(request, 'cadastro.html', {})


def sair(request):
    logout(request)
    return redirect('index')
