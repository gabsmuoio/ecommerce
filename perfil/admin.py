from django.contrib import admin

from import_export.admin import ImportExportModelAdmin
from .models import Perfil

# Register your models here.


@admin.register(Perfil)
class PerfilAdmin(ImportExportModelAdmin):
    list_display = ['usuario', 'data_nasc', 'cpf']


# admin.site.register(Perfil)
