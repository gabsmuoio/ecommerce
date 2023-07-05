# type: ignore

from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView
from django.views import View
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
import copy

from . import models
from . import forms


class BasePerfil(View):
    template_name = 'perfil/criar.html'

    def setup(self, *args, **kwargs):
        super().setup(*args, **kwargs)

        self.carrrinho = copy.deepcopy(self.request.session.get('carrinho', {}))

        self.perfil = None

        if self.request.user.is_authenticated:
            self.perfil = models.Perfil.objects.filter(
                usuario=self.request.user
            ).first()

            self.contexto = {
                'userform': forms.UserForm(
                    data=self.request.POST or None,
                    usuario=self.request.user,
                    instance=self.request.user,
                ),
                'perfilform': forms.PerfilForm(
                    data=self.request.POST or None,
                    instance=self.perfil
                )
            }
        else:
            self.contexto = {
                'userform': forms.UserForm(
                    data=self.request.POST or None
                ),
                'perfilform': forms.PerfilForm(
                    data=self.request.POST or None
                )
            }

        self.userform = self.contexto['userform']
        self.perfilform = self.contexto['perfilform']

        if self.request.user.is_authenticated:
            self.template_name = 'perfil/atualizar.html'

        self.renderizar = render(
            self.request, self.template_name, self.contexto)

    def get(self, *args, **kwargs):
        return self.renderizar


class Criar(BasePerfil):
    def post(self, *args, **kwargs):
        # Verificando se o formulário do usuário é válido
        if not self.userform.is_valid() or not self.perfilform.is_valid():
            print('INVÁLIDO')
            messages.error(
                self.request,
                'Existem erros no formulário de cadastro. Favor corrigir!'
            )
            return self.renderizar
        
        username = self.userform.cleaned_data.get('username')
        password = self.userform.cleaned_data.get('senha')
        email = self.userform.cleaned_data.get('email')
        first_name = self.userform.cleaned_data.get('first_name')
        last_name = self.userform.cleaned_data.get('last_name')
        
        # Usuário logado: atualização
        if self.request.user.is_authenticated:
            print('Autenticado')
            usuario = get_object_or_404(
                User, username=self.request.user.username
            )
            usuario.username = username

            if password:
                usuario.set_password(password)

            usuario.email = email
            usuario.first_name = first_name
            usuario.last_name = last_name
            usuario.save()

            if not self.perfil:
                self.perfilform.cleaned_data['usuario'] = usuario
                perfil = models.Perfil(**self.perfilform.cleaned_data)
                perfil.save()
            else:
                perfil = self.perfilform.save(commit=False)
                perfil.usuario = usuario
                perfil.save()


        # Usuário não logado: cadastro
        else:
            print('Não Autenticado')
            usuario = self.userform.save(commit=False)
            usuario.set_password(password)
            usuario.save()

            perfil = self.perfilform.save(commit=False)
            perfil.usuario = usuario
            perfil.save()

        print('VÁLIDO')

        if password:
            autentica = authenticate(
                self.request,
                username=usuario,
                password=password
            )
        
            if autentica:
                login(self.request, user=usuario)


        self.request.session['carrinho'] = self.carrrinho
        self.request.session.save()

        messages.success(
            self.request,
            'Cadastro criado/atualizado com sucesso'
        )

        messages.success(
            self.request,
            'Você fez login e pode concluir sua compra'
        )

        return redirect('produto:carrinho')
        return self.renderizar


class Atualizar(View):
    def get(self, *args, **kwargs):
        return HttpResponse('Atualizar')


class Login(View):
    def post(self, *args, **kwargs):
        username = self.request.POST.get('username')
        password = self.request.POST.get('password')

        #print(username,password)

        if not username or not password:
            messages.error(
                self.request,
                'Usuário ou senha inválidos.'
            )
            return redirect('perfil:criar')
        
        usuario = authenticate(
            self.request, username=username, password=password
            )

        if not usuario:
            messages.error(
                self.request,
                'Usuário ou senha inválidos.'
            )
            return redirect('perfil:criar')

        messages.success(
                self.request,
                'Você fez login no sistema.'
        )
        
        login(self.request, user=usuario)
        return redirect('produto:carrinho')


class Logout(View):
    def get(self, *args, **kwargs):
        carrrinho = copy.deepcopy(self.request.session.get('carrinho'))
        logout(self.request)
        # Transferindo o carrinho para a próximo sessão, pós logout
        self.request.session['carrinho'] = carrrinho
        self.request.session.save()

        return redirect('produto:lista')
