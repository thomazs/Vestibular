from datetime import datetime
from django.db.models import Avg, Count, Min, Sum
from decimal import Decimal
import json
from urllib.parse import urlencode
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Count
from django.http import Http404, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy

from instituicao.models import Pessoa
from processo_seletivo.forms import LoginForm, FormCadastro, FormCompletaCadastro, FormInscricao, FormCorrigeRedacao
from processo_seletivo.models import Inscricao, Curso, EdicaoCurso, Afiliado, Edicao
from processo_seletivo.services import tag_segura_valida, cria_tag_segura, gera_cod_validacao, \
    envia_email_cadastro, valida_email, ativa_pessoa, loga_pessoa, envia_email_cadastroconcluido, pega_edicao_ativa, \
    envia_email_inscricaofeita, cria_perguntas_inscricao, pega_questao_responder, resposta_valida, responder_questao, \
    prova_redirecionar_para, gravar_redacao, RespostaInscricao, envia_email_redacao


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

    inscricao_ativa = request.user.get_inscricao_ativa


    return render(request, 'painel.html', locals())


@transaction.atomic
def cadastro(request, id=None):
    if id is not None:
        sessao = request.session['afiliado_codigo'] = id
        parceiro = Afiliado.objects.filter(codigo=id).first()
        if not parceiro:
            return redirect('cadastro')

        if parceiro.visitas == None:
            parceiro.visitas = 0
            parceiro.save()
        else:
            parceiro.visitas = parceiro.visitas + 1
            parceiro.save()
    else:
        sessao = None

    form = FormCadastro()
    if request.method == 'POST':
        print(request.POST)
        form = FormCadastro(request.POST)
        if form.is_valid():
            pessoa = form.save(commit=False)
            pessoa.codvalidacao = gera_cod_validacao()
            pessoa.codigo_afiliado = sessao
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
    edicao_ativa = pega_edicao_ativa()
    verifica = Inscricao.objects.filter(pessoa=request.user.get_pessoa(), edicao=edicao_ativa)
    if verifica:
        messages.error(request, 'O candidato já possui inscrição ativa')
        return redirect('painel')

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
            pinscricao.pessoa = pessoa
            pinscricao.afiliado = pessoa.codigo_afiliado
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
    if request.user.is_superuser:
        edicao_atual = pega_edicao_ativa()
        total_inscricao = Inscricao.objects.filter(treineiro=False, edicao=edicao_atual).count()
        metas = EdicaoCurso.objects.all().aggregate(q=Sum('qtd_vagas'))
        # calcula a meta minima de inscrições
        meta_minima = int((total_inscricao * 100) / metas['q'])

        inscricao_afiliados = Inscricao.objects.filter(afiliado__isnull=False, edicao=edicao_atual).count()
        afiliados = Afiliado.objects.all()

        redacao_pendente = Inscricao.objects.filter(fez_redacao=False, tipo_selecao=1, edicao=edicao_atual).count()
        redacao_naocorrigida = Inscricao.objects.filter(fez_redacao=True, nota_redacao__isnull=True,
                                                        tipo_selecao=1, edicao=edicao_atual).count()
        media = int((redacao_pendente * 100) / total_inscricao)

        inscricao_enem = Inscricao.objects.filter(tipo_selecao=3, edicao=edicao_atual).count()
        inscricao_enem_aprovados = Inscricao.objects.filter(tipo_selecao=3, situacao=21, edicao=edicao_atual).count()
        inscricao_enem_reprovados = Inscricao.objects.filter(tipo_selecao=3, situacao=13, edicao=edicao_atual).count()

        inscricao_portadordiploma = Inscricao.objects.filter(tipo_selecao=2, edicao=edicao_atual).count()
        inscricao_portadordiploma_aprovados = Inscricao.objects.filter(tipo_selecao=2, situacao=21,
                                                                       edicao=edicao_atual).count()
        inscricao_portadordiploma_reprovados = Inscricao.objects.filter(tipo_selecao=2, situacao=13,
                                                                        edicao=edicao_atual).count()

        return render(request, 'redacao/home.html', locals())
    else:
        return redirect('acompanhamento_ti')


@login_required
def acompanhamento_ti(request):
    if request.user.is_staff:
        edicao_ativa = pega_edicao_ativa()

        cursos = EdicaoCurso.objects.filter(edicao=edicao_ativa)

        matriculados = Inscricao.objects.filter(situacao=31, edicao=edicao_ativa).count()
        total_inscricao = Inscricao.objects.filter(treineiro=False, edicao=edicao_ativa).count()
        # cursos = edicao_curso.objects.annotate(qtd_inscricoes=Count('curso__cursoopcao_set')).order_by('-qtd_inscricoes')
        redacao_pendente = Inscricao.objects.filter(fez_redacao=False, tipo_selecao=1, edicao=edicao_ativa).count()
        redacao_naocorrigida = Inscricao.objects.filter(fez_redacao=False, nota_redacao__isnull=True,
                                                        tipo_selecao=1, edicao=edicao_ativa).count()
        media = int((redacao_pendente * 100) / total_inscricao)
        return render(request, 'acompanhamento_ti.html', locals())


@login_required
def corrige_redacao(request):
    if request.user.is_staff:
        edicao_atual = pega_edicao_ativa()
        redacao = Inscricao.objects.filter(fez_redacao='True', nota_redacao=None, edicao=edicao_atual).first()
        sem_redacao = Inscricao.objects.filter(fez_redacao='False', tipo_selecao=1, edicao=edicao_atual)
        corrigidas = Inscricao.objects.filter(corretor_redacao=request.user, edicao=edicao_atual).count()
        nao_corrigidas = Inscricao.objects.filter(fez_redacao='True', nota_redacao=None, edicao=edicao_atual).count()

        pontos_prova = RespostaInscricao.objects.filter(inscricao=redacao, resposta__correta=True).aggregate(
            Sum('questao__pontos'))

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
                post.nota_prova = pontos_prova['questao__pontos__sum']
                post.nota_geral = post.nota_redacao + post.nota_prova
                if post.nota_geral >= 200:
                    post.situacao = 21
                else:
                    post.situacao = 11
                post.save()

                messages.success(request, 'Nota salva com sucesso')

                if post.nota_geral >= 200:
                    # teste de sms
                    # !/usr/bin/python
                    import urllib.request
                    login_sms = 'passos27'
                    token_sms = '75c0320a62b207887cb59dc27ebddded'
                    numero_sms = post.pessoa.fone
                    import re
                    numero_sms = re.sub("[^0-9]", "", numero_sms)
                    mensagem_sms = urlencode({
                        'msg': 'VESTIBULAR U:VERSE: Parabéns! Você foi aprovado no Vestibular U:verse, procure a Instituição ou acesse: https://uverse.in/info para saber mais.'})
                    with urllib.request.urlopen(
                            "http://painel.kingsms.com.br/kingsms/api.php?acao=sendsms&login=" + login_sms + "&token=" + token_sms + "&numero=" + numero_sms + "&" + mensagem_sms) as url:
                        s = url.read()
                return redirect('correcao')
        else:
            form = FormCorrigeRedacao()
    else:
        return redirect('index')

    return render(request, 'redacao/correcao.html', locals())


@login_required
def redacao_pendente(request):
    if request.user.is_staff:
        edicao_atual = pega_edicao_ativa()
        sem_redacao = Inscricao.objects.filter(fez_redacao='False', tipo_selecao=1, edicao=edicao_atual)

    else:
        return redirect('index')

    return render(request, 'redacao/lista-redacao-pendente.html', locals())


def inscritos_por_processo(request):
    if request.user.is_staff:
        if request.GET.get('ed') and request.GET.get('dt_inicio') and request.GET.get('dt_fim'):
            ed = request.GET.get('ed')
            dt_inicio = request.GET.get('dt_inicio')
            dt_fim = request.GET.get('dt_fim')

            inscritos = Inscricao.objects.filter(situacao=21, edicao=ed, data_inclusao__gte=dt_inicio, data_inclusao__lte=dt_fim)
        else:
            inscritos = Inscricao.objects.filter(situacao=21)

        edicao_atual = pega_edicao_ativa()
        edicoes = Edicao.objects.all().reverse()


    else:
        return redirect('index')

    return render(request, 'relatorios/inscritos_por_processo.html', locals())


@login_required
def csv_redacao_pendente(request):
    if request.user.is_staff:
        edicao_atual = pega_edicao_ativa()
        sem_redacao = Inscricao.objects.filter(fez_redacao='False', tipo_selecao=1, edicao=edicao_atual)
    else:
        return redirect('index')
    r = render(request, 'csv/redacao_pendente.html', locals(), content_type='text/plain')
    r['content-disposition'] = 'attachment; filename="Redacao.csv"'
    return r


@login_required
def inscricao_enem(request):
    if request.user.is_staff:
        edicao_atual = pega_edicao_ativa()
        candidatos = Inscricao.objects.filter(tipo_selecao='3', situacao=1, edicao=edicao_atual)
    else:
        return redirect('index')

    return render(request, 'redacao/selecao-enem.html', locals())


@login_required
def portador_diploma(request):
    if request.user.is_staff:
        edicao_atual = pega_edicao_ativa()
        candidatos = Inscricao.objects.filter(tipo_selecao='2', situacao=1, edicao=edicao_atual)
        aprovados = Inscricao.objects.filter(tipo_selecao='2', situacao=21, edicao=edicao_atual)
        reprovados = Inscricao.objects.filter(tipo_selecao='2', situacao=13, edicao=edicao_atual)

    else:
        return redirect('index')

    return render(request, 'redacao/portador-diploma.html', locals())


@login_required
def ativa_enem(request, codigo, status):
    if request.user.is_staff:
        is_ok, cod = tag_segura_valida(codigo)
        if not is_ok:
            raise Http404()
        inscricao = get_object_or_404(Inscricao, id=cod)

        if status == 'A':
            inscricao.situacao = 21
            inscricao.save()
            return redirect('inscricao_enem')
        elif status == 'R':
            inscricao.situacao = 13
            inscricao.save()
            return redirect('inscricao_enem')

    else:
        return redirect('index')


def ativa_portador_diploma(request, codigo, status):
    if request.user.is_staff:
        inscricao = get_object_or_404(Inscricao, id=codigo)

        if status == 'A':
            inscricao.situacao = 21
            inscricao.save()
            return redirect('portador_diploma')
        elif status == 'R':
            inscricao.situacao = 13
            inscricao.save()
            return redirect('portador-diploma')

    else:
        return redirect('index')


@login_required
def aprovados_provapadrao(request):
    if request.user.is_staff:
        edicao_atual = pega_edicao_ativa()
        inscritos = Inscricao.objects.filter(situacao=21, edicao=edicao_atual)
        n_aprovados = Inscricao.objects.filter(situacao=21, edicao=edicao_atual).count()
    else:
        return redirect('index')

    return render(request, 'redacao/aprovados.html', locals())


@login_required
def marcar_matriculado(request, id=None):
    if request.user.is_staff:
        inscritos = Inscricao.objects.get(id=id)
        print(inscritos.situacao)
        inscritos.situacao = '31'
        inscritos.save()

    return redirect('aprovados')


@login_required
def inscricao_pendente(request):
    if request.user.is_staff:

        pessoas = list()

        inscritos = Pessoa.objects.filter()

        for i in inscritos:
            nome = Inscricao.objects.filter(pessoa__email=i.email)
            if nome:
                pessoas.append('nome:' + i.nome)
                pessoas.append('email:' + i.email)
                print(pessoas)

    else:
        return redirect('index')

    return render(request, 'redacao/inscricao_pendente.html', locals())


def cursosJson(request, cod):
    codigo = '4b68f9fa5686f541bb53c1e77a78833a6536d84aeb80190e7e6d84eea376e8268df51ff87973147a4bec7f7130f25225b60c530d4e0be29259a4a42e934b8fe1'
    if cod == codigo:
        cursos = [{'id': i.id,
                   'curso': i.curso.nome,
                   'qtd_inscricoes': i.qtd_inscricoes,
                   'vagas': i.qtd_vagas,
                   } for i in EdicaoCurso.objects.annotate(qtd_inscricoes=Count('curso__cursoopcao_set')).order_by(
            '-qtd_inscricoes')]
    else:
        cursos = [{'erro': 'Código incorreto'}]

    # teste = [ {'id': i.id, 'curso': i.curso.nome} for i in Inscricao.objects.all()]

    response = HttpResponse(json.dumps(cursos), content_type='text/json')
    response["Access-Control-Allow-Origin"] = '*'
    # response["Access-Control-Allow-Methods"] = 'GET'
    # response["Access-Control-Max-Age"] = '1000'
    # response["Access-Control-Allow-Headers"] = 'X-Requested-With, Content-Type'
    return response


def cursosIndividualJson(request, cod_curso, cod):
    codigo = '4b68f9fa5686f541bb53c1e77a78833a6536d84aeb80190e7e6d84eea376e8268df51ff87973147a4bec7f7130f25225b60c530d4e0be29259a4a42e934b8fe1'

    if cod == codigo:
        nao_fezredacao = Inscricao.objects.filter(curso_id=cod_curso, fez_redacao=False).count()
        matriculados = Inscricao.objects.filter(curso_id=cod_curso, situacao=31).count()
        curso = [{'nao_redacao': nao_fezredacao, 'matriculados': matriculados}]
    else:
        curso = [{'erro': 'Código incorreto'}]

    response = HttpResponse(json.dumps(curso), content_type='text/json')
    response["Access-Control-Allow-Origin"] = '*'
    # response["Access-Control-Allow-Methods"] = 'GET'
    # response["Access-Control-Max-Age"] = '1000'
    # response["Access-Control-Allow-Headers"] = 'X-Requested-With, Content-Type'
    return response


@login_required
def afiliados(request):
    afiliado_dados = Afiliado.objects.get(pessoa__usuario=request.user)
    qtd_indicados = Inscricao.objects.filter(afiliado=afiliado_dados.codigo).count()
    indicados = Inscricao.objects.filter(afiliado=afiliado_dados.codigo)

    ganhos = Inscricao.objects.filter(afiliado=afiliado_dados.codigo, situacao=31).count()

    return render(request, 'afiliados/afiliados.html', locals())


# def consultaStatusAPI(request, cod, email):
#     codigo = '4b68f9fa5686f541bb53c1e77a78833a6536d84aeb80190e7e6d84eea376e8268df51ff87973147a4bec7f7130f25225b60c530d4e0be29259a4a42e934b8fe1'
#
#     if cod == codigo:
# 	    edicao_atual = pega_edicao_ativa()
#         dados = Inscricao.objects.filter(pessoa__email=email,edicao=edicao_atual).first()
#
#         if dados:
#
#             if dados.get_situacao_display() == 'Inscrito':
#                 curso = {
#                     'status': dados.get_situacao_display(),
#                     'curso': dados.curso.nome,
#                     'mensagem': 'Aguardando correção',
#                     'text': 'Você pode verificar o status da correção de sua prova a qualquer momento através do painel de controle do candidato, disponível em: https://uverse.in/uvest'
#                 }
#             elif dados.get_situacao_display() == 'Aprovado':
#                 curso = {
#                     'status': dados.get_situacao_display(),
#                     'curso': dados.curso.nome,
#                     'mensagem': dados.get_situacao_display(),
#                     'texto': 'Parabéns 👏👏👏... Você foi aprovado!! Já pode ir até a U:verse para efetuar sua matrícula, é importante ter em mãos todos os documentos previtos no edital, nosso atendimento funciona das 14h às 18h, de segunda a sexta.'
#                 }
#         else:
#             curso = {
#                 'status': 'Não encontrado',
#                 'curso': 'Não encontrado',
#                 'mensagem': 'Dados não encontrados',
#                 'texto': 'Verifiquei aqui e notei que você não possui nenhuma inscrição vinculada para este endereço de e-mail, caso não tenha feito o vestibular é so acessar: https://uverse.in/uvest e se inscrever para o curso desejado. Ah!! você pode fazer tudo online, inclusive a prova :)'
#             }
#     else:
#         curso = {'texto': 'Encontramos um erro ao verificar seus dados, por favor verifique o e-mail que você forneceu.'}
#
#     response = HttpResponse(json.dumps(curso), content_type='text/json')
#     response["Access-Control-Allow-Origin"] = '*'
#     response["Access-Control-Allow-Methods"] = 'GET'
#     response["Access-Control-Max-Age"] = '1000'
#     response["Access-Control-Allow-Headers"] = 'X-Requested-With, Content-Type'
#     return response


def ajuste_nota(request):
    inscricao = Inscricao.objects.filter(tipo_selecao=1, fez_redacao=False)

    arquivo = open("log_envios_redacao.txt", "a")
    envios = list()

    for i in inscricao:
        envia_email_redacao(i)
        envios.append('\n')
        envios.append(str(datetime.now()) + '---')
        envios.append(i.pessoa.email)

    envios.append('\n')
    envios.append(str(datetime.now()) + '///////////////////////////////////////////////////')
    arquivo.writelines(envios)

    return render(request, 'ajuste-nota.html', locals())
