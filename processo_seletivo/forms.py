from django import forms
from django.contrib.auth import authenticate, login


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
