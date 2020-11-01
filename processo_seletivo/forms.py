from django import forms
from django.contrib.auth import authenticate, login

from instituicao.models import Pessoa, Curso
from processo_seletivo.models import Inscricao


class LoginForm(forms.Form):
    email = forms.CharField(label='Email', required=True)
    senha = forms.CharField(label='Senha', required=True, widget=forms.PasswordInput)
    request = None

    def clean(self):
        data = super(LoginForm, self).clean()
        if data.get('email') and data.get('senha'):
            has_user = authenticate(username=data['email'], password=data['senha'])
            if has_user is None:
                raise forms.ValidationError('Email ou senha inválido!')
            login(self.request, user=has_user)
        else:
            raise forms.ValidationError('É preciso informar o email e a senha!')
        return data


class FormCadastro(forms.ModelForm):
    class Meta:
        model = Pessoa
        fields = ('nome', 'fone', 'email')

    def clean_nome(self):
        nome = self.data.get('nome', '')
        if nome == '':
            raise forms.ValidationError('É preciso informar o nome')

        if len(nome.split(' ')) < 2:
            raise forms.ValidationError('Informe o nome completo')

        return nome.upper()

    def clean(self):
        data = super(FormCadastro, self).clean()
        email = data.get('email', '')
        if email and Pessoa.objects.only('id', 'email').filter(email=email).exists():
            raise forms.ValidationError('Email já cadastrado!')
        return data


class FormCompletaCadastro(forms.ModelForm):
    senha = forms.CharField(label='Senha de Acesso', required=True, widget=forms.PasswordInput())
    confsenha = forms.CharField(label='Confirmação de Senha', required=True, widget=forms.PasswordInput())

    class Meta:
        model = Pessoa
        fields = ('id', 'rg', 'cpf', 'dt_nasc')

    def __init__(self, *args, **kwargs):
        super(FormCompletaCadastro, self).__init__(*args, **kwargs)
        self.fields['rg'].required = True
        self.fields['cpf'].required = True
        self.fields['dt_nasc'].required = True

    def clean(self):
        data = super(FormCompletaCadastro, self).clean()
        senha = data.get('senha', '').strip()
        confsenha = data.get('confsenha', '').strip()

        if senha and confsenha and senha != confsenha:
            raise forms.ValidationError('Senha não confere com sua confirmação!')
        elif senha == '' or confsenha == '':
            raise forms.ValidationError('É necessário informar a senha e sua confirmação')

        return data


class FormInscricao(forms.ModelForm):
    class Meta:
        model = Inscricao
        fields = (
            'tipo_selecao', 'nota_enem', 'ano_enem', 'comprovante_enem', 'treineiro', 'comprovante_escolaridade',
            'nec_intlibras', 'nec_ledor', 'nec_transcritor', 'nec_localfacilacesso', 'nec_outros',
            'nec_outros_desc', 'nec_prova_presencial', 'curso'
        )

    def formata(self):
        tipos_input = ['nota_enem', 'ano_enem', 'curso']
        tipos_file = ['comprovante_enem', 'comprovante_escolaridade', ]
        tipos_checkbox = [
            'treineiro', 'nec_prova_presencial', 'nec_outros', 'nec_localfacilacesso', 'nec_transcritor',
            'nec_ledor', 'nec_intlibras']
        tipos = {
            'form-control': tipos_input,
            'form-control-file': tipos_file,
            'form-check-input': tipos_checkbox,
        }
        for cn, lf in tipos.items():
            for nf in lf:
                self.fields[nf].widget.attrs['placeholder'] = self.fields[nf].label
                self.fields[nf].widget.attrs['title'] = self.fields[nf].label
                self.fields[nf].widget.attrs['class'] = cn

    def __init__(self, *args, **kwargs):
        edicao = kwargs.pop('edicao', None)
        super(FormInscricao, self).__init__(*args, **kwargs)
        if edicao:
            cursos_id = [ec.curso.id for ec in edicao.edicaocurso_set.only('curso').all()]
            self.fields['curso'].queryset = self.fields['curso'].queryset.filter(id__in=cursos_id)
        else:
            self.fields['curso'].queryset = Curso.objects.none()

        self.formata()

class FormCorrigeRedacao(forms.ModelForm):
    class Meta:
        model = Inscricao
        fields = ('nota_redacao_p1', 'nota_redacao_p2', 'nota_redacao_p3', 'nota_redacao_p4', 'nota_redacao_p5',)

    def __init__(self, *args, **kwargs):
        super(FormCorrigeRedacao, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
            self.fields['nota_redacao_p1'].required = True
            self.fields['nota_redacao_p2'].required = True
            self.fields['nota_redacao_p3'].required = True
            self.fields['nota_redacao_p4'].required = True
            self.fields['nota_redacao_p5'].required = True