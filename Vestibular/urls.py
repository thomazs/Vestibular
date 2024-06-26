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
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth import views as auth_views
from processo_seletivo.views import index, cadastro, painel, sair, emailenviado, validar_email, concluir_cadastro, \
    mensagem, faz_inscricao, prova_online, revisao_prova_online, \
    prova_redacao, revisao_prova_redacao, prova_completa, \
    acompanhamento, acompanhamento_ti, corrige_redacao, redacao_pendente, inscricao_enem, portador_diploma, ajuste_nota, \
    csv_redacao_pendente, ativa_enem, aprovados_provapadrao, cursosJson, afiliados, ativa_portador_diploma, \
    cursosIndividualJson, inscricao_pendente, marcar_matriculado, inscritos_por_processo

admin.site.site_header = 'Vestibular U:Verse'
admin.site.site_title = 'VestU:Verse'
admin.site.index_title = 'Sistema de Vestibular'
admin.sites.AdminSite.site_url = 'http://uverse.in/uvest/'

urlpatterns = [
    path('admin/', admin.site.urls),

    path('cadastro/<id>', cadastro, name="cadastro"),
    path('cadastro/', cadastro, name="cadastro"),


    path('painel/', painel, name="painel"),
    path('faz_inscricao/', faz_inscricao, name="faz_inscricao"),
    path('sair/', sair, name="sair"),
    path('mensagem/', mensagem, name="mensagem"),
    path('emailenviado/<token>/', emailenviado, name="emailenviado"),
    path('validar_email/<token>/', validar_email, name="validar_email"),
    path('concluir_cadastro/<token>/', concluir_cadastro, name="concluir_cadastro"),
    path('prova_online/', prova_online, name="prova_online"),
    path('prova_redacao/', prova_redacao, name="prova_redacao"),
    path('revisao_prova_online/', revisao_prova_online, name="revisao_prova_online"),
    path('revisao_prova_redacao/', revisao_prova_redacao, name="revisao_prova_redacao"),
    path('prova_completa/', prova_completa, name="prova_completa"),
    path('acompanhamento/', acompanhamento, name="acompanhamento"),
    path('acompanhamento_ti/', acompanhamento_ti, name="acompanhamento_ti"),
    path('correcao/', corrige_redacao, name="correcao"),
    path('redacao_pendente/', redacao_pendente, name="redacao_pendente"),
    path('inscricao_enem/', inscricao_enem, name="inscricao_enem"),
    path('ativa_enem/<codigo>/<status>', ativa_enem, name="ativa_enem"),
    path('ativa_portador_diploma/<codigo>/<status>', ativa_portador_diploma, name="ativa_portador_diploma"),
    path('portador-diploma/', portador_diploma, name="portador_diploma"),
    path('ajuste_nota/', ajuste_nota, name="ajuste_nota"),
    path('csv_redacao_pendente/', csv_redacao_pendente, name="csv_redacao_pendente"),
    path('aprovados/', aprovados_provapadrao, name="aprovados"),
    path('afiliados/', afiliados, name="afiliados"),
    path('cursosJson/<cod>', cursosJson, name="cursosJson"),
    path('cursosIndividualJson/<cod_curso>/<cod>', cursosIndividualJson, name="cursosIndividualJson"),
    # path('consultaStatusAPI/<cod>/<email>', consultaStatusAPI, name="consultaStatusAPI"),
    path('inscricao_pendente', inscricao_pendente, name="inscricao_pendente"),
    path('marcar_matriculado/<id>', marcar_matriculado, name="marcar_matriculado"),
    path('inscritos_por_processo/', inscritos_por_processo, name="inscritos_por_processo"),

    path('reset_password/', auth_views.PasswordResetView.as_view(), name="reset_password"),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(), name="password_reset_done"),
    path('reset/<uidb64>/<token>', auth_views.PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(), name="password_reset_complete"),

    path('', index, name="index"),

    path('tinymce/', include('tinymce.urls')),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static('media/', document_root=settings.MEDIA_ROOT)

