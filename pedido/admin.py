from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Pedido, ItemPedido

# Register your models here.


@admin.register(ItemPedido)
class ItemPedidoAdmin(ImportExportModelAdmin):
    list_display = ['pedido', 'produto', 'produto_id']


class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    extra = 1


class PedidoAdmin(admin.ModelAdmin):
    inlines = [
        ItemPedidoInline
    ]


admin.site.register(Pedido, PedidoAdmin)
# admin.site.register(ItemPedido)
