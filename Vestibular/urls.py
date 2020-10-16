"""Vestibular URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from processo_seletivo.views import index, cadastro, painel, sair, emailenviado, validar_email, concluir_cadastro, \
    mensagem, faz_inscricao, prova_online

admin.site.site_header = 'Vestibular U:Verse'
admin.site.site_title = 'VestU:Verse'
admin.site.index_title = 'Sistema de Vestibular'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('cadastro/', cadastro, name="cadastro"),
    path('painel/', painel, name="painel"),
    path('faz_inscricao/', faz_inscricao, name="faz_inscricao"),
    path('sair/', sair, name="sair"),
    path('mensagem/', mensagem, name="mensagem"),
    path('emailenviado/<token>/', emailenviado, name="emailenviado"),
    path('validar_email/<token>/', validar_email, name="validar_email"),
    path('concluir_cadastro/<token>/', concluir_cadastro, name="concluir_cadastro"),
    path('prova_online/', prova_online, name="prova_online"),

    path('', index, name="index"),
]
