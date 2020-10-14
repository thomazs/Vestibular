from django import forms
from django.contrib.auth import authenticate, login

from instituicao.models import Pessoa


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
