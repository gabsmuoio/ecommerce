from django.urls import path, re_path
from . import views

app_name = 'pedido'

urlpatterns = [
    path('pagar/<int:pk>', views.Pagar.as_view(), name="pagar"),
    path('salvarpedido/', views.SalvarPedido.as_view(), name="salvarpedido"),
    path('lista/', views.Lista.as_view(), name="lista"),
    path('detalhe/<int:pk>', views.Detalhe.as_view(), name="detalhe"),
    re_path(r'^export-exl/$', views.export, name='export'),
    re_path('grafico/', views.main_view, name='grafico'),
]
