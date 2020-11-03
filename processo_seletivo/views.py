from datetime import datetime

from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Count
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy

from instituicao.models import Pessoa
from processo_seletivo.forms import LoginForm, FormCadastro, FormCompletaCadastro, FormInscricao, FormCorrigeRedacao
from processo_seletivo.models import Inscricao, Curso, EdicaoCurso
from processo_seletivo.services import tag_segura_valida, cria_tag_segura, gera_cod_validacao, \
    envia_email_cadastro, valida_email, ativa_pessoa, loga_pessoa, envia_email_cadastroconcluido, pega_edicao_ativa, \
    envia_email_inscricaofeita, cria_perguntas_inscricao, pega_questao_responder, resposta_valida, responder_questao, \
    prova_redirecionar_para, gravar_redacao


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
        if pessoa.email_valido and pessoa.usuario:
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
        return redirect('index')

    edicao = pega_edicao_ativa()
    form = FormInscricao(instance=inscricao, edicao=edicao)
    if request.method == 'POST':
        form = FormInscricao(request.POST, instance=inscricao, edicao=edicao)
        if form.is_valid():
            pinscricao = form.save(commit=False)
            pinscricao.curso_final = pinscricao.curso
            pinscricao.edicao = edicao
            # pinscricao.pessoa = pessoa
            pinscricao.pessoa = request.user.get_pessoa()
            pinscricao.save()
            cria_perguntas_inscricao(pinscricao)
            envia_email_inscricaofeita(pessoa, pinscricao)
            messages.success(request, 'Inscrição efetuada com sucesso!')
            return redirect('painel')

    return render(request, 'inscricao.html', locals())


@login_required(login_url=reverse_lazy('index'))
@transaction.atomic()
def prova_online(request):
    edicao = pega_edicao_ativa()
    if (not edicao) or (not edicao.prova_liberada):
        return redirect('painel')

    inscricao = request.user.get_inscricao_ativa()

    # Se já fez a prova objetiva, redireciona
    if inscricao.fez_prova:
        return redirect(prova_redirecionar_para(inscricao))

    # Verifica qual a primeira questão a responder
    opcoes, primeira_responder, tag_voltar, questao = pega_questao_responder(inscricao)
    total_questoes = opcoes.count()

    # Verifica se foi pedido para ver uma pergunta em especial
    questao_especifica = request.GET.get('qesp', None)
    if questao_especifica:
        is_ok, tag_questao = tag_segura_valida(questao_especifica)
        if is_ok and opcoes.filter(pk=tag_questao).exists():
            questao = opcoes.filter(pk=tag_questao).first()
            if questao.ordem > 1:
                tag_voltar = cria_tag_segura(opcoes.filter(ordem=questao.ordem - 1).first().id)
            else:
                tag_voltar = None
        else:
            messages.info(request, 'Não foi possível identificar a questão solicitada')

    # Verifica se todas as questões foram respondidas, vai para revisão
    if questao is None:
        return redirect('revisao_prova_online')

    if request.method == 'POST':
        resposta_id = request.POST.get('resposta')
        if not resposta_id:
            messages.error(request, 'Não foi repassado nenhuma resposta')
        else:
            resp_ok, resp = resposta_valida(questao.questao, resposta_id)
            if not resp_ok:
                messages.error(request, 'A resposta repassada não é válida!')

            else:
                responder_questao(questao, resp)
                return redirect('prova_online')
    return render(request, 'prova_online.html', locals())


@login_required(login_url=reverse_lazy('index'))
def revisao_prova_online(request):
    edicao = pega_edicao_ativa()
    if (not edicao) or (not edicao.prova_liberada):
        return redirect('painel')

    inscricao = request.user.get_inscricao_ativa()

    # Se já fez a prova objetiva, vai para redação
    if inscricao.fez_prova:
        return redirect(prova_redirecionar_para(inscricao))

    if request.method == 'POST':
        # todo Enviar email com as respostas das questões e suas pontuações
        inscricao.fez_prova = True
        inscricao.dt_fim_prova = datetime.now()
        inscricao.save()
        return redirect('prova_redacao')

    respostas_dadas = inscricao.respostainscricao_set.order_by('ordem')
    return render(request, 'revisao_prova_online.html', locals())


@login_required(login_url=reverse_lazy('index'))
def prova_redacao(request):
    edicao = pega_edicao_ativa()
    if (not edicao) or (not edicao.prova_liberada):
        return redirect('painel')

    inscricao = request.user.get_inscricao_ativa()

    # Se já fez a prova objetiva, vai para redação
    if inscricao.fez_redacao:
        return redirect(prova_redirecionar_para(inscricao))

    if request.method == 'POST':
        redacao = request.POST.get('redacao')
        gravar_redacao(inscricao, redacao)
        return redirect('revisao_prova_redacao')

    return render(request, 'prova_redacao.html', locals())


@login_required(login_url=reverse_lazy('index'))
def revisao_prova_redacao(request):
    edicao = pega_edicao_ativa()
    if (not edicao) or (not edicao.prova_liberada):
        return redirect('painel')

    inscricao = request.user.get_inscricao_ativa()

    # Se já fez a prova objetiva, vai para redação
    if inscricao.fez_redacao:
        return redirect(prova_redirecionar_para(inscricao))

    if request.method == 'POST':
        # todo Enviar email com as respostas das questões e suas pontuações
        inscricao.fez_redacao = True
        inscricao.save()
        return redirect('prova_completa')

    texto_redacao = '<p>' + '</p><p>'.join(inscricao.redacao.split('\n')) + '</p>'
    return render(request, 'revisao_prova_redacao.html', locals())


@login_required(login_url=reverse_lazy('index'))
def prova_completa(request):
    edicao = pega_edicao_ativa()
    if (not edicao) or (not edicao.prova_liberada):
        return redirect('painel')

    inscricao = request.user.get_inscricao_ativa()

    if not inscricao.fez_prova:
        return redirect('prova_online')

    if not inscricao.fez_redacao:
        return redirect('prova_redacao')

    respostas_dadas = inscricao.respostainscricao_set.order_by('ordem')
    texto_redacao = '<p>' + '</p><p>'.join(inscricao.redacao.split('\n')) + '</p>'
    total_pontos_prova = sum([r.questao.pontos for r in respostas_dadas if r.resposta.correta])
    # todo Adicionar pontuação da redação
    return render(request, 'prova_completa.html', locals())


# todo Criar modelo de envio de mensagens a candidatos com filtros específicos:
# inscritos, não fizeram redação, não inscreveram curso, não fizeram prova, iniciaram mas não concluíram,
# pontuaram, passaram


@login_required(login_url=reverse_lazy('index'))
def acompanhamento(request):
    return render(request, 'acompanhamento.html', locals())


@login_required
def acompanhamento_ti(request):
    total_inscricao = Inscricao.objects.all().count()
    cursos = EdicaoCurso.objects.annotate(qtd_inscricoes=Count('curso__cursoopcao_set')).order_by('-qtd_inscricoes')

    return render(request, 'acompanhamento_ti.html', locals())


@login_required
def corrige_redacao(request):
    if request.user.is_staff:
        redacao = Inscricao.objects.filter(fez_redacao='True', nota_redacao=None).first()
        sem_redacao = Inscricao.objects.filter(fez_redacao='False')

        corrigidas = Inscricao.objects.filter(corretor_redacao=request.user).count()

        if request.method == "POST":
            form = FormCorrigeRedacao(request.POST, instance=redacao)

            if form.is_valid():
                post = form.save(commit=False)
                post.corretor_redacao = request.user
                post.nota_redacao_p1 = post.nota_redacao_p1
                post.nota_redacao_p2 = post.nota_redacao_p2
                post.nota_redacao_p3 = post.nota_redacao_p3
                post.nota_redacao_p4 = post.nota_redacao_p4
                post.nota_redacao_p5 = post.nota_redacao_p5
                post.nota_redacao = post.nota_redacao_p1 + post.nota_redacao_p2 + post.nota_redacao_p3 + post.nota_redacao_p4 + post.nota_redacao_p5
                post.save()
                messages.success(request, 'Nota salva com sucesso')
                return redirect('correcao')
        else:
            form = FormCorrigeRedacao()
    else:
        return redirect('index')

    return render(request, 'redacao/correcao.html', locals())


@login_required
def redacao_pendente(request):
    if request.user.is_staff:
        sem_redacao = Inscricao.objects.filter(fez_redacao='False')
    else:
        return redirect('index')

    return render(request, 'redacao/lista-redacao-pendente.html', locals())


@login_required
def inscricao_enem(request):
    if request.user.is_staff:
       candidatos = Inscricao.objects.filter(tipo_selecao='3')
    else:
        return redirect('index')

    return render(request, 'redacao/selecao-enem.html', locals())
