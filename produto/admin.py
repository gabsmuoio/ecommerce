from django.contrib import admin
from .models import Produto, Variacao

# Register your models here.


class VariacaoInline(admin.TabularInline):
    model = Variacao
    extra = 1


class ProdutoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'descricao_curta', 'descricao_longa',
                    'get_preco_formatado', 'get_preco_promo_formatado']
    inlines = [
        VariacaoInline
    ]


admin.site.register(Produto, ProdutoAdmin)
admin.site.register(Variacao)
