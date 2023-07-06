from typing import Any
from django import http
from django.shortcuts import render, redirect, reverse
from django.views.generic import ListView, DetailView
from django.views import View
from django.http import HttpResponse
from django.contrib import messages
from pedido.resources import ItemPedidoResource

from .utils import get_plot
from produto.models import Variacao
from .models import Pedido, ItemPedido

from utils import utils


class DispatchLoginRequiredMixin(View):
    # Permite apenas usuários logados
    def dispatch(self, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return redirect('perfil:criar')

        return super().dispatch(*args, **kwargs)

    # Permite que o usuário veja apenas os seus pedidos
    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs)
        qs = qs.filter(usuario=self.request.user)
        return qs


class Pagar(DispatchLoginRequiredMixin, DetailView):
    template_name = 'pedido/pagar.html'
    model = Pedido
    pk_url_kwarg = 'pk'
    context_object_name = 'pedido'


class SalvarPedido(View):
    template_name = 'pedido/pagar.html'

    def get(self, *args, **kwargs):
        # Verificar se o usuário está logado
        if not self.request.user.is_authenticated:
            messages.error(
                self.request,
                'Você precisa fazer login'
            )
            return redirect('perfil:criar')

        # Verificar se tem algo no carrinho
        if not self.request.session.get('carrinho'):
            messages.error(
                self.request,
                'Carrinho vazio'
            )
            return redirect('produto:lista')

        # Verificar se o estoque é suficiente para o pedido
        carrinho = self.request.session.get('carrinho')
        carrinho_variacao_ids = [v for v in carrinho]
        bd_variacoes = Variacao.objects.select_related('produto').filter(
            id__in=carrinho_variacao_ids
        )
        for var in bd_variacoes:
            var_id = str(var.id)

            estoque = var.estoque
            qtd_carrinho = carrinho[var_id]['quantidade']
            preco_unit = carrinho[var_id]['preco_unitario']
            preco_unit_promo = carrinho[var_id]['preco_unitario_promocional']

            error_msg_estoque = ''

            if estoque < qtd_carrinho:
                carrinho[var_id]['quantidade'] = estoque
                carrinho[var_id]['preco_quantitativo'] = estoque * preco_unit
                carrinho[var_id]['preco_quantitativo_promocional'] = estoque * \
                    preco_unit_promo

                error_msg_estoque = 'Estoque insuficiente para alguns produtos '\
                    'do seu carrinho. Reduzimos a quantidade desses produtos. '\
                    'Por favor, verifique quais produtos foram afetados.'

                if error_msg_estoque:
                    messages.error(
                        self.request,
                        error_msg_estoque
                    )
                    self.request.session.save()
                    return redirect('produto:carrinho')

        print(carrinho_variacao_ids)
        print(bd_variacoes)

        qtd_total_carrinho = utils.qtd_total_carrinho(carrinho)
        vlr_total_carrinho = utils.total_carrinho(carrinho)

        pedido = Pedido(
            usuario=self.request.user,
            total=vlr_total_carrinho,
            qtd_total=qtd_total_carrinho,
            status='C',
        )

        pedido.save()

        ItemPedido.objects.bulk_create(
            [
                ItemPedido(
                    pedido=pedido,
                    produto=v['produto_nome'],
                    produto_id=v['produto_id'],
                    variacao=v['variacao_nome'],
                    variacao_id=v['variacao_id'],
                    preco=v['preco_quantitativo'],
                    preco_promo=v['preco_quantitativo_promocional'],
                    quantidade=v['quantidade'],
                    imagem=v['imagem'],
                ) for v in carrinho.values()
            ]
        )

        del self.request.session['carrinho']
        return redirect(
            reverse(
                'pedido:pagar',
                kwargs={
                    'pk': pedido.pk
                }
            )
        )


class Detalhe(DispatchLoginRequiredMixin, DetailView):
    model = Pedido
    context_object_name = 'pedido'
    template_name = 'pedido/detalhe.html'
    pk_url_kwarg = 'pk'


class Lista(DispatchLoginRequiredMixin, ListView):
    model = Pedido
    context_object_name = 'pedido'
    template_name = 'pedido/lista.html'
    paginate_by = 3
    ordering = ['-id']
    print(context_object_name)


def export(request):
    itempedido_resource = ItemPedidoResource()
    dataset = itempedido_resource.export()
    # response = HttpResponse(dataset.csv, content_type='text/csv')
    # response['Content-Disposition'] = 'attachment; filename="member.csv"'
    # response = HttpResponse(dataset.json, content_type='application/json')
    # response['Content-Disposition'] = 'attachment; filename="persons.json"'
    response = HttpResponse(
        dataset.xls, content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="itenspedidos.xls"'
    return response


def main_view(request):
    qs = Pedido.objects.all()
    x = [x.pk for x in qs]
    y = [y.total for y in qs]
    chart = get_plot(x, y)

    return render(request, 'pedido/grafico.html', {'chart': chart})
