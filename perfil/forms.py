from typing import Any, Dict, Mapping, Optional, Type, Union
from django import forms
from django.contrib.auth.models import User
from django.core.files.base import File
from django.db.models.base import Model
from django.forms.utils import ErrorList
from . import models


class PerfilForm(forms.ModelForm):
    class Meta:
        model = models.Perfil
        fields = '__all__'
        exclude = ('usuario',)


class UserForm(forms.ModelForm):
    senha = forms.CharField(
        required=False,
        widget=forms.PasswordInput(),
        label='Senha',
    )
    senha2 = forms.CharField(
        required=False,
        widget=forms.PasswordInput(),
        label='Confirmação Senha'
    )

    def __init__(self, usuario=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.usuario = usuario

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username',
                  'senha', 'senha2', 'email')

    def clean(self, *args, **kwargs):
        data = self.data
        cleaned = self.cleaned_data
        validation_error_msgs = {}

        usuario_data = cleaned.get('username')
        email_data = cleaned.get('email')
        senha_data = cleaned.get('senha')
        senha2_data = cleaned.get('senha2')

        usuario_db = User.objects.filter(username=usuario_data).first()
        email_db = User.objects.filter(email=email_data).first()

        error_usuario_existe = 'Usuário já existe'
        error_email_existe = 'E-mail já existe'
        error_senha_diferente = 'As duas senhas não conferem'
        error_senha_curta = 'Senha menor que 6 caracteres'
        error_senha_obrigatoria = 'Senha é um campo obrigatório'

        # Usuários logados: atualização
        if self.usuario:
            if usuario_db:
                if usuario_data != usuario_db.username:
                    validation_error_msgs['username'] = error_usuario_existe

            if email_db:
                if email_data != email_db.email:
                    validation_error_msgs['email'] = error_email_existe

            if senha_data:
                if senha_data != senha2_data:
                    validation_error_msgs['senha'] = error_senha_diferente
                    validation_error_msgs['senha2'] = error_senha_diferente

                if len(senha_data) < 6:
                    validation_error_msgs['senha'] = error_senha_curta

            print('LOGADO')

        # Usuários não logados: cadastro
        else:
            if usuario_db:
                validation_error_msgs['username'] = error_usuario_existe

            if email_db:
                validation_error_msgs['email'] = error_email_existe

            if not senha_data:
                validation_error_msgs['senha'] = error_senha_obrigatoria

            if not senha2_data:
                validation_error_msgs['senha2'] = error_senha_obrigatoria

            if senha_data != senha2_data:
                validation_error_msgs['senha'] = error_senha_diferente
                validation_error_msgs['senha2'] = error_senha_diferente

            if len(senha_data) < 6:
                validation_error_msgs['senha'] = error_senha_curta

            print('NÃO LOGADO')

        if validation_error_msgs:
            raise (forms.ValidationError(validation_error_msgs))
