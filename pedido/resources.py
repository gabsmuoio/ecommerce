from import_export import resources
from pedido.models import ItemPedido


class ItemPedidoResource(resources.ModelResource):
    class Meta:
        model = ItemPedido
